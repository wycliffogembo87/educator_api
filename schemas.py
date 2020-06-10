from pydantic import BaseModel
from typing import List
from typing import Dict
from uuid import UUID
from datetime import datetime
from models import Status
from models import Role
from models import Mark

class User(BaseModel):
    username : str
    phone_number : str
    email : str
    role : Role
    status : Status
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Question(BaseModel):
    exam_id : str
    number : int = None
    text : str
    multi_choice : List[str] = None # If None then free_text
    marks : int
    answer : str

class ExamOut(BaseModel):
    id : UUID
    name : str
    video_tutorial_name : str = None
    user : User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class QuestionOut(BaseModel):
    id : UUID
    number : int
    text : str
    multi_choice : List[str] = None # If None then free_text
    marks : int
    answer : str = None
    # exam_id : UUID
    # exam : ExamOut
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Questions(BaseModel):
    exam_id : str
    questions : List[Question]

class Exam(BaseModel):
    name : str
    video_tutorial_name : str = None

class Submission(BaseModel):
    question_id : str
    answer : str

class SubmissionOut(BaseModel):
    id : UUID
    answer : str
    mark : Mark
    marks_obtained : int = None
    comment : str = None
    question : QuestionOut
    user : User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Submissions(BaseModel):
    exam_id : str
    answers : List[Submission]

class Notification(BaseModel):
    learner_id : str
    channel : str = "sms" # Or email or any other
    message : str

class Mentorship(BaseModel):
    learner_id : str
    tutor : str
    challenge_being_faced : str

class UploadedFile(BaseModel):
    file_name : str
    content_type : str