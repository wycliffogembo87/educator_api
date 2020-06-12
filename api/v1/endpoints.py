import os, sys
import traceback
from loguru import logger

from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from fastapi import Depends
from fastapi import status
from fastapi import HTTPException

from fastapi.responses import StreamingResponse

import schemas
import core
import models
import util

security = HTTPBasic()

router = APIRouter(redirect_slashes=False)

# Create video storage directory
videos_dir = '{}/videos/'.format(os.getcwd())
util.mkdir_p(videos_dir)


@router.get("/user", response_model=schemas.User, tags=["user"])
@util.global_exception_handler
def get_user(user : models.User = Depends(core.authenticate_user)):
    """
    Description:

        This endpoint just return the users account details.
    """
    return user


@router.post("/video", response_model=schemas.UploadedFile, tags=["video"], status_code=201)
@util.global_exception_handler
def upload_video(
    uploaded_file: UploadFile = File(...),
    user : schemas.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint enables tutors to upload video tutorials.

    Please note the following:

        - Video tutorials should be uploaded to a file storage service e.g amazon s3.
        - Below is just for demo purpose.
        - The file name is the video tutorial name.
        - Only tutors can upload videos
    
    Demo:

        If you upload a video with file name as test.mp4 you will be able to see it stream in this swagger spec stream video section. 
    """

    return core.upload_video(user.role, uploaded_file, videos_dir)


@router.get("/video/{file_name}", tags=["video"], status_code=200)
@util.global_exception_handler
def stream_video(
    file_name: str,
    user : schemas.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint enables users to stream video tutorials.


    Please Note the following:

        - Video files should stored in a file storage service like amazon s3 buckets.
        - A source url can point direct to this files without passing the server but that means anyone will be able to view this videos.
        - For better and scalable streaming a third party service like mux.com can be used.
    
    Params:

        file_name
            - This is the same as the video tutorial name.
            - A video can have many exams attached to it through this parameter.

    Usage example:

        <!DOCTYPE html>
            <html>
                <body>
                    <video width="320" height="240" controls>
                        <source src="http://127.0.0.1:8000/api/v1/video/test.mp4" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </body>
            </html>
    
    <!DOCTYPE html>
        <html>
            <body>
                <video width="320" height="240" controls>
                    <source src="http://127.0.0.1:8000/api/v1/video/test.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
        </html>
    """
    file_content = open(videos_dir + file_name, mode='rb')
    return StreamingResponse(file_content, media_type="video/mp4")


@router.post("/exam", response_model=schemas.ExamOut, tags=["exam"], status_code=201)
@util.global_exception_handler
def create_exam(
    exam: schemas.Exam,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:
        
        This endpoint enables tutors to create exams.

    Please note the following:

        - Only tutors allowed to create exams.

    Params:

        name
            - String
            - Mandatory
            - E.g KCSE prep phase two exam
            - Should be descriptive

        video_tutorial_name
            - String
            - Optional
            - E.g kcse_prep.mp4
            - Its the video tutorial file name and can be left out if the exam doesn't have a video tutorial.
    """
    return core.create_exam(user.id, user.role, exam)


@router.post("/exam/participant", tags=["exam"], status_code=201)
@util.global_exception_handler
def add_participant(
    participant: schemas.Participant,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:
        
        This endpoint enables tutors to add participants for a particular exams.

    Please note the following:

        - Only tutors allowed to add participants.

    Params:

        exam_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - Its returned when one creates an exam

        user_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - This is the id of the learner who is qualified to sit for this exam
    """
    return core.add_participant(user.id, user.role, participant)


# response_model=schemas.QuestionOut throws DatabaseSessionOver exception
@router.post("/exam/question", tags=["exam"], status_code=201)
@util.global_exception_handler
def create_question(
    question: schemas.Question,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:
        
        This endpoint enables tutors to add questions to an exam.
    
    Please note the following:

        - Only tutors allowed to create questions.
    
    Params:

        exam_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - Its returned when one creates an exam
    
        text
            - String
            - Mandatory
            - E.g Who is the current president of Kenya?
            - This is the the actual question

        multi_choice
            - List[String]
            - Optional
            - E.g ["A. Daniel Moi", "B. Uhuru Kenyatta", "C. William Ruto", "D. Raila Odinga"]
            - Do not submit this param if you want a free text question.

        marks : int
            - Integer
            - Mandatory
            - E.g 5
            - This is the number of points a learner will get for correctly answering this question

        answer
            - String
            - Mandatory
            - E.g "B" if a multi_choice, "Uhuru Kenyatta" if free text
            - This is the answer to this question, and can be used for realtime auto grading 
    """
    return core.create_question(user.id, user.role, question)


# response_model=schemas.SubmissionOut throws DatabaseSessionOver exception
@router.post("/exam/submission", tags=["exam"], status_code=201)
@util.global_exception_handler
def create_submission(
    submission: schemas.Submission,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint enables the a learner to answer a question.
    
    Please note the following:

        - Only learners allowed to create submissions.
    
    Params:

        question_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - Its returned when one creates a question
        
        answer
            - String
            - Mandatory
            - E.g "B" if a multi_choice, "Uhuru Kenyatta" if free text
            - This is the answer a learner submits to a particular question

    """
    return core.create_submission(user.id, user.role, submission)


# response_model=schemas.SubmissionOut throws DatabaseSessionOver exception
@router.post("/exam/submission/mark", tags=["exam"], status_code=201)
@util.global_exception_handler
def mark_submission(
    submission: schemas.MarkSubmission,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint enables a tutor to mark answers provided as correct or wrong or partially correct.
        This especially applies to free text questions and multi_choice questions are auto marked. 
    
    Please note the following:

        - If a learner has attempted to answer, the tutor can award marks other than the exact marks stated for that question.
        - Only tutors allowed to mark submissions.
    
    Params:

        submission_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - Its returned when a learner answers a given question 
        
        mark
            - String
            - Mandatory
            - E.g tick or cross
            - The indicator that a question is correctly answerd or not
        
        marks
            - Integer
            - Optional
            - E.g 4
            - The number of points that the tutor feels the learner deserves to be awarded based on how he/she answered a given question. If not submitted the questions already defined marks will be used
    """
    return core.mark_submission(user.id, user.role, submission)

@router.get("/exam/{exam_id}/performance", tags=["exam"], status_code=200)
@util.global_exception_handler
def get_exam_performance(
    exam_id : str,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:
        
        This endpoint returns the perfomance of a particular exam.

    Please note the following:

        - Only tutors allowed to get exam perfomance.

    Params:

        exam_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - This is obtained when an exam is created
    """
    return core.get_exam_performance(user.role, exam_id)


@router.post("/notification", tags=["notification"], status_code=201)
@util.global_exception_handler
def notify_user(
    notification : schemas.Notification,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint can be used to send sms notification to any user.

    Please note the following:

        - Only tutors, staff and admins can send notifications
    
    Params:

        user_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - This id is used to fetch contact details from the users account and sends an sms to the users phone number. It is obtained when a users account is created.
        
        message
            - String
            - Mandatory
            - E.g Hi. You have now been moveed to level 2. Congratulations
            - The message can be any thing the sender wants to communicate to the receiver.
    """
    return core.notify_user(
        user.role, notification.user_id, notification.message
    )


# response_model=schemas.MentorshipOut throws DatabaseSessionOver exception
@router.post("/mentorship", tags=["mentorship"], status_code=201)
@util.global_exception_handler
def request_for_mentorship(
    mentorship : schemas.Mentorship,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Description:

        This endpoint enables learners to request for mentoirship from tutors.
    
    Please note the following:

        - Only learners can request for mentorship.

    Params:

        tutor_id
            - String
            - Mandatory
            - E.g e3ff1d3c-f018-475f-a3cb-c1c3f4bc0258
            - This is the tutors account id obtained when the users account for this tutor is created.
        
        challenge_being_faced
            - String
            - Mandatory
            - E.g I need help in understanding the mole concept
            - This is just a short description of why you need mentorship.
    """
    return core.request_for_mentorship(user.id, user.role, mentorship)