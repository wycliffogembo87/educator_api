from pydantic import BaseModel
from typing import List, Dict

class Question(BaseModel):
    number : int
    question : str
    multichoice : List[str] = None # If None then free_text
    answer : str

class CreateQuiz(BaseModel):
    quiz_id : str
    name : str
    questions : List[Question]
    video_tutorial_name : str = None
    tutor_id : str

class FilledAnswer(BaseModel):
    learner_id : str
    question_number : int
    answer : str

class FilledAnswers(BaseModel):
    quiz_id : str
    answers : List[FilledAnswer]

class Notification(BaseModel):
    learner_id : str
    channel : str = "sms" # Or email or any other
    message : str

class Mentorship(BaseModel):
    learner_id : str
    tutor : str
    challenge_being_faced : str