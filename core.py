from fastapi import Depends
from fastapi import status
from fastapi import HTTPException

from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials

from passlib.context import CryptContext

from pony.orm import *

from uuid import UUID

from models import User
from models import Exam
from models import Question
from models import Submission
from models import Grade
from models import Performance
from models import Status
from models import Role
from models import Mark

import models
import schemas

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

roles = dict(
    create_exam=[Role.tutor],
    create_question=[Role.tutor],
    create_submission=[Role.learner],
    mark_submission=[Role.tutor]
)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def is_authorized(user: models.User, action: str):
    print("Action : {}, Role : {}".format(action, user.role))
    print(dir(Role))
    if user.role not in roles[action]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only {} can {}".format(roles[action], action)
        )
    return True

@db_session
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user(credentials.username)
    if user and \
        user.status == Status.active and \
            verify_password(credentials.password, user.password):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password or inactive account",
        headers={"WWW-Authenticate": "Basic"},
    )

@db_session
def get_user(username: str):
    return User.get(username=username, status=Status.active)

@db_session
def create_user(username: str, password: str, phone_number: str, email: str, role: Role):
    user = User(
        username=username,
        password=get_password_hash(password),
        phone_number=phone_number,
        email=email,
        role=role,
        # status=Status.active
    )
    return user

@db_session
def create_exam(user: models.User, exam: schemas.Exam):
    
    is_authorized(user, "create_exam")

    exam_data = dict(
        name=exam.name,
        user=User[user.id]
    )
    if exam.video_tutorial_name:
        exam_data["video_tutorial_name"] = exam.video_tutorial_name

    return Exam(**exam_data)

@db_session
def create_question(user: models.User, question: schemas.Question):

    is_authorized(user, "create_question")

    exam = Exam.get(id=question.exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found : id: {}".format(question.exam_id)
        )

    question_data = dict(
        text=question.text,
        marks=question.marks,
        exam=exam
    )

    if question.multi_choice:
        question_data["multi_choice"] = question.multi_choice
    
    if question.answer:
        question_data["answer"] = question.answer
    
    counter = count(q for q in Question if q.exam == exam)
    question_data["number"] = counter + 1

    return Question(**question_data)


@db_session
def mark_submission(user: models.User, submission: schemas.Submission):
    is_authorized(user, "mark_submission")

    mark = Mark.tick if submission.mark == "tick" else Mark.cross

    submission = Submission.get(id=submission.submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Submission not found : submission_id: {}".format(
                    submission.submission_id
                )
            )
        )
    
    if submission.mark == Mark.unmarked:
        submission.mark = mark
    submission.marks_obtained = (
        submission.question.marks
        if mark == Mark.tick else 0
    )

    performance = performance_review(User[user.id], submission)

    print(performance.to_dict())
    print(submission.to_dict())

    return submission

@db_session
def create_submission(user: models.User, submission: schemas.Submission):
    is_authorized(user, "create_submission")
    
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
    
    learner = User[user.id]

    submission = Submission(
        answer=submission.answer,
        question=question,
        user=learner,
        marks_obtained=(
            question.marks
            if submission.answer == question.answer
            else 0
        ),
        mark=(
            Mark.auto_tick
            if question.multi_choice
            and len(question.multi_choice) > 0
            and submission.answer == question.answer
            else
            Mark.auto_cross
        )
    )

    performance = performance_review(learner, submission)

    print(performance.to_dict())
    print(submission.to_dict())

    return submission

def performance_review(learner : models.User, submission : models.Submission):
    exam = submission.question.exam

    auto_passed_questions = select(
        q
        for q in Question
        if q.multi_choice
        and len(q.multi_choice) > 0
        and q.answer
        and len(q.answer) > 0
        and submission.answer == q.answer
        and q.exam == exam
        and 
    )[:]
    print(auto_passed_questions)

    auto_failed_questions = select(
        q
        for q in Question
        if q.multi_choice
        and len(q.multi_choice) > 0
        and q.answer
        and len(q.answer) > 0
        and submission.answer != q.answer
        and q.exam == exam
    )[:]
    print(auto_failed_questions)

    passed_questions = select(
        q
        for q in submission.question:
        if q.mark == Mark.tick
        and q.exam == exam
    )[:]
    print(passed_questions)

    failed_questions = select(
        q
        for q in Question
        if q.mark == Mark.cross
        and q.exam == exam
    )[:]
    print(failed_questions)

    stats = select(
        (sum(q.marks), count())
        for q in Question
        if q.exam == exam
    )[:][0]
    print(stats)
    total_marks, total_number_of_questions = stats

    auto_tick_count = 0
    auto_tick_total_marks = 0
    auto_cross_count = 0
    auto_cross_total_marks = 0

    for q in auto_passed_questions:
        auto_tick_count += 1
        auto_tick_total_marks += q.marks
    
    for q in auto_failed_questions:
        auto_cross_count += 1
        auto_cross_total_marks += q.marks

    tick_count = 0
    tick_total_marks = 0
    cross_count = 0
    cross_total_marks = 0
    
    for q in passed_questions:
        tick_count += 1
        tick_total_marks += q.marks
    
    for q in failed_questions:
        cross_count += 1
        cross_total_marks += q.marks
    
    percentage = auto_tick_total_marks / total_marks * 100

    grade = Grade.get(
        lambda g:
        percentage >= g.starting_percentage
        and percentage <= g.ending_percentage
    )
    print(grade)

    performance = Performance.get(user=learner, exam=exam)

    if not performance:
        performance_data = dict(
            tick_count=tick_count,
            tick_total_marks=tick_total_marks,
            cross_count=cross_count,
            cross_total_marks=cross_total_marks,
            auto_tick_count=auto_tick_count,
            auto_tick_total_marks=auto_tick_total_marks,
            auto_cross_count=auto_cross_count,
            auto_cross_total_marks=auto_cross_total_marks,
            total_number_of_questions=total_number_of_questions,
            total_marks=total_marks,
            percentage=int(percentage),
            grade=grade,
            exam=exam,
            user=learner
        )
        performance = Performance(**performance_data)
    else:
        performance.tick_count = 0
        performance.tick_count = 0
        performance.tick_total_marks = 0
        performance.cross_count = 0
        performance.cross_total_marks = 0
        performance.auto_tick_count = auto_tick_count
        performance.auto_tick_total_marks = auto_tick_total_marks
        performance.auto_cross_count = auto_cross_count
        performance.auto_cross_total_marks = auto_cross_total_marks
        performance.total_number_of_questions = total_number_of_questions
        performance.total_marks = total_marks
        performance.grade = grade
    
    return performance

@db_session
def populate_grades():
    grades = [
        dict(starting_percentage=0, ending_percentage=65, letter_grade="E/F", four_point_zero_grade=0.0),
        dict(starting_percentage=65, ending_percentage=66, letter_grade="D", four_point_zero_grade=1.0),
        dict(starting_percentage=67, ending_percentage=69, letter_grade="D+", four_point_zero_grade=1.3),
        dict(starting_percentage=70, ending_percentage=72, letter_grade="C-", four_point_zero_grade=1.7),
        dict(starting_percentage=73, ending_percentage=76, letter_grade="C", four_point_zero_grade=2.0),
        dict(starting_percentage=77, ending_percentage=79, letter_grade="C+", four_point_zero_grade=2.3),
        dict(starting_percentage=80, ending_percentage=82, letter_grade="B-", four_point_zero_grade=2.7),
        dict(starting_percentage=83, ending_percentage=86, letter_grade="B", four_point_zero_grade=3.0),
        dict(starting_percentage=87, ending_percentage=89, letter_grade="B+", four_point_zero_grade=3.3),
        dict(starting_percentage=90, ending_percentage=92, letter_grade="A-", four_point_zero_grade=3.7),
        dict(starting_percentage=93, ending_percentage=96, letter_grade="A", four_point_zero_grade=4.0),
        dict(starting_percentage=97, ending_percentage=100, letter_grade="A+", four_point_zero_grade=4.0)
    ]
    for grade in grades:
        g = Grade(**grade)
        print(g.to_dict())

@db_session
def populate_users():
    users = [
        dict(username='tutor', password=get_password_hash('tutor123'), phone_number="+254728043275", email="wycliff@brck.com", role=Role.tutor),
        dict(username='learner', password=get_password_hash('learner123'), phone_number="+254735688154", email="wycliffogembo87@gmail.com", role=Role.learner),
        dict(username='staff', password=get_password_hash('staff123'), phone_number="+254728043276", email="wycliffogembo88@gmail.com", role=Role.tutor),
        dict(username='admin', password=get_password_hash('admin123'), phone_number="+254728043277", email="wycliffogembo89@gmail.com", role=Role.tutor)
    ]
    for user in users:
        u = User(**user)
        print(u.to_dict())

if __name__ == '__main__':
    populate_users()
    populate_grades()