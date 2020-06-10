from fastapi import Depends
from fastapi import status
from fastapi import HTTPException

from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials

from passlib.context import CryptContext

from pony.orm import db_session
from pony.orm import count as pony_count

from uuid import UUID

from models import User
from models import Exam
from models import Question
from models import Submission
from models import Status
from models import Role

import models
import schemas

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

roles = dict(
    create_exam=[Role.tutor, Role.admin],
    create_question=[Role.tutor, Role.admin],
    create_submission=[Role.learner, Role.admin],
)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def is_authorized(user: models.User, action: str):
    print("Action : {}, Role : {}".format(action, user.role))
    if user.role not in roles[action]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tutors can create exams"
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
    
    if question.number:
        question_data["number"] = question.number
    else:
        count = pony_count(q for q in Question if q.exam == exam)
        question_data["number"] = count + 1

    return Question(**question_data)

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
    
    submission = Submission(
        answer=submission.answer,
        question=question,
        user=User[user.id]
    )

    return submission


if __name__ == '__main__':
    user = create_user(
        'wycliffogembo',
        'wycliffogembo123',
        "+254728043275",
        "wycliffogembo87@gmail.com",
        Role.admin
    )
    print(user)