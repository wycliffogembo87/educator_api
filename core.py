import requests
import shutil

from fastapi import Depends
from fastapi import status
from fastapi import HTTPException
from fastapi import UploadFile

from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials

from loguru import logger
from typing import List
from pathlib import Path

from pony.orm import *

from uuid import UUID

from models import User
from models import Exam
from models import Participant
from models import Question
from models import Submission
from models import Grade
from models import Performance
from models import Notification
from models import Mentorship
from models import Status
from models import Role
from models import Mark

import models
import schemas
import settings
import util


security = HTTPBasic()


def is_authorized(user_role: Role, action: str):
    logger.debug("Action : {}, Role : {}".format(action, user_role))
    if user_role not in settings.roles[action]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only {} can {}".format(settings.roles[action], action)
        )
    return True


@db_session
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user(credentials.username)
    if user and \
        user.status == Status.active and \
            util.verify_password(credentials.password, user.password):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password or inactive account",
        headers={"WWW-Authenticate": "Basic"},
    )


@db_session
def get_user(username: str):
    return User.get(username=username, status=Status.active)


def upload_video(user_role: Role, uploaded_file: UploadFile, videos_dir: str):
    is_authorized(user_role, "upload_file")

    def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
        try:
            with open(destination, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        finally:
            upload_file.file.close()
    
    save_upload_file(uploaded_file, videos_dir + uploaded_file.filename)

    return {
        "file_name": uploaded_file.filename,
        "content_type": uploaded_file.content_type
    }


@db_session
def create_exam(user_id: UUID, user_role: Role, exam: schemas.Exam):
    is_authorized(user_role, "create_exam")

    exam_data = dict(
        name=exam.name,
        user=User[user_id]
    )
    if exam.video_tutorial_name:
        exam_data["video_tutorial_name"] = exam.video_tutorial_name

    return Exam(**exam_data)


@db_session
def add_participant(user_id: UUID, user_role: Role, participant: schemas.Participant):
    is_authorized(user_role, "add_participant")

    exam_id = participant.exam_id
    learner_id = participant.user_id

    exam = Exam.get(id=exam_id, user=User[user_id])
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found : id: {}".format(exam_id)
        )

    learner = User.get(id=learner_id, role=Role.learner)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found : id: {}".format(learner_id)
        )

    participant = Participant(
        exam=exam,
        user=learner
    )

    return participant.to_dict()


@db_session
def create_question(user_id: UUID, user_role: Role, question_in: schemas.Question):
    is_authorized(user_role, "create_question")

    exam = Exam.get(id=question_in.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found : id: {}".format(question_in.exam_id)
        )

    question = dict(
        text=question_in.text,
        marks=question_in.marks,
        exam=exam
    )

    if question_in.multi_choice:
        question["multi_choice"] = question_in.multi_choice
    
    if question_in.answer:
        question["answer"] = question_in.answer
    
    counter = select(max(q.number) for q in Question if q.exam == exam)[:][0]
    if not counter:
        counter = 0
    question["number"] = counter + 1

    return Question(**question).to_dict()


@db_session
def create_submission(user_id: UUID, user_role: Role, submission: schemas.Submission):
    is_authorized(user_role, "create_submission")
    
    question = Question.get(id=submission.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Question not found : question_id: {}".format(
                    submission.question_id
                )
            )
        )
    
    participant = Participant.get(exam=question.exam, user=User[user_id])
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Participant not found : exam_id: {}".format(
                    question.exam.id
                )
            )
        )

    if len(question.multi_choice) > 0:
        if submission.answer == question.answer:
            marks_obtained = question.marks
            mark = Mark.auto_tick
        else:
            marks_obtained = 0
            mark = Mark.auto_cross

        submission = Submission(
            answer=submission.answer,
            question=question,
            user=User[user_id],
            marks_obtained=marks_obtained,
            mark=mark
        )
    else:
        submission = Submission(
            answer=submission.answer,
            question=question,
            user=User[user_id]
        )

    performance_review(submission)

    return submission.to_dict()


@db_session
def mark_submission(user_id: UUID, user_role: Role, submission: schemas.Submission):
    is_authorized(user_role, "mark_submission")

    mark = Mark.tick if submission.mark == "tick" else Mark.cross
    marks_to_award = submission.marks
    submission_id = submission.submission_id

    submission = Submission.get(id=submission_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Submission not found : submission_id: {}".format(
                    submission_id
                )
            )
        )
    
    if submission.mark == Mark.unmarked:
        submission.mark = mark
        if marks_to_award:
            submission.marks_obtained = marks_to_award
        else:
            submission.marks_obtained = (
                submission.question.marks
                if mark == Mark.tick else 0
            )

        performance_review(submission)

        return submission.to_dict()
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Submission already auto marked : submission_id: {}".format(
                    submission_id
                )
            )
        )


def performance_review(submission : models.Submission):
    exam = submission.question.exam

    exam_questions = select(
        q
        for q in Question
        if q.exam == exam
    )[:]

    total_marks, total_number_of_questions = 0, 0
    for exam_question in exam_questions:
        total_marks += exam_question.marks
        total_number_of_questions += 1

    learner_submissions = select(
        s
        for s in Submission
        if s.question.exam == exam
        and s.user == submission.user
    )[:]

    ticks = 0
    crosses = 0
    unmarked = 0
    marks_obtained = 0
    
    for s in learner_submissions:
        if s.mark == Mark.tick or s.mark == Mark.auto_tick:
            ticks += 1
            marks_obtained += s.marks_obtained
        elif s.mark == Mark.cross or s.mark == Mark.auto_cross:
            crosses += 1
        elif s.mark == Mark.unmarked:
            unmarked += 1
        else:
            pass
    
    percentage = int(marks_obtained / total_marks * 100)
    grade = Grade.get(
        lambda g:
        percentage >= g.starting_percentage
        and percentage <= g.ending_percentage
    )

    performance = Performance.get(user=submission.user, exam=exam)

    if not performance:
        performance_data = dict(
            ticks=ticks,
            crosses=crosses,
            unmarked=unmarked,
            marks_obtained=marks_obtained,
            total_marks=total_marks,
            total_number_of_questions=total_number_of_questions,
            percentage=percentage,
            grade=grade,
            exam=exam,
            user=submission.user
        )
        performance = Performance(**performance_data)
    else:
        performance.ticks = ticks
        performance.crosses = crosses
        performance.unmarked = unmarked
        performance.marks_obtained = marks_obtained
        performance.total_marks = total_marks
        performance.percentage = percentage
        performance.grade = grade
    
    logger.debug(performance.to_dict())
    
    return performance


@db_session
def get_exam_performance(user_role: Role, exam_id: str):
    is_authorized(user_role, "get_exam_performance")

    exam = Exam.get(id=exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found : id: {}".format(exam_id)
        )
    
    results = select(p for p in Performance if p.exam == exam )[:]

    performance = []
    for result in results:
        performance.append(result.to_dict())
    
    return performance




@db_session
def notify_user(user_role: Role, user_id: str, message: str):
    is_authorized(user_role, "notify_user")
    
    user = User.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "User not found : user_id: {}".format(
                    user_id
                )
            )
        )
    return send_sms(user, [user.phone_number], message)


def send_sms(user: models.User, recipients: List[str], message: str):

    api_key = str(settings.AFRICASTALKING_API_KEY)
    api_username = str(settings.AFRICASTALKING_API_USERNAME)

    data = {
        'username': api_username,
        'to': ','.join(recipients),
        'message': message,
        # 'from': str(settings.AFRICASTALKING_API_SENDER_ID)
    }
    headers = {
        'apiKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    # logger.debug('SMS send request : {}'.format(data))

    response = requests.post(
        settings.AFRICASTALKING_API_URL, data=data,
        headers=headers
    )

    try:
        response = response.json()
    except Exception as error:
        logger.debug(error)
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    else:
        sms_message_data = response['SMSMessageData']
        notification = Notification(user=user, metadata=sms_message_data)
        logger.debug(notification)
    
    return response


@db_session
def request_for_mentorship(user_id: str, user_role: Role, mentorship: schemas.Mentorship):
    is_authorized(user_role, "request_form_mentorship")

    tutor_id = mentorship.tutor_id
    challenge_being_faced = mentorship.challenge_being_faced

    mentorship = Mentorship(
        user = User[user_id],
        tutor=UUID(tutor_id),
        challenge_being_faced=challenge_being_faced
    )

    return mentorship.to_dict()