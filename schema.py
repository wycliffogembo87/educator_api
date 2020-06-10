from pydantic import BaseModel
from typing import List, Dict

class Question(BaseModel):
    number : int
    question : str
    multichoice : List[str] = None # If None then free_text
    marks : int
    answer : str

class CreateExam(BaseModel):
    exam_id : str
    name : str
    questions : List[Question]
    video_tutorial_name : str = None
    tutor_id : str

class Submission(BaseModel):
    learner_id : str
    question_number : int
    answer : str

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