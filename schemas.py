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
    exam : ExamOut
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Exam(BaseModel):
    name : str
    video_tutorial_name : str = None

class StartExam(BaseModel):
    exam_id : str
    duration : int = None
    alert_after : List[int] = None

class Participant(BaseModel):
    exam_id : str
    user_id : str

class Submission(BaseModel):
    question_id : str
    answer : str

class MarkSubmission(BaseModel):
    submission_id : str
    mark : str # tick or cross
    marks : int = None

class Grade(BaseModel):
    id : UUID
    starting_percentage : int
    ending_percentage : int
    letter_grade : str
    four_point_zero_grade : float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Performance(BaseModel):
    id : UUID
    ticks : int
    crosses : int
    unmarked : int
    marks_obtained : int
    total_marks : int
    total_number_of_questions : int
    percentage : int
    grade : Grade
    exam : ExamOut
    user : User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    
class SubmissionOut(BaseModel):
    id : UUID
    answer : str
    mark : Mark
    marks_obtained : int
    comment : str = None
    question : QuestionOut
    user : User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Notification(BaseModel):
    user_id : str
    message : str

class Mentorship(BaseModel):
    tutor_id : str
    challenge_being_faced : str

class MentorshipOut(BaseModel):
    id : UUID
    tutor : UUID
    challenge_being_faced : str
    is_active : bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UploadedFile(BaseModel):
    file_name : str
    content_type : str