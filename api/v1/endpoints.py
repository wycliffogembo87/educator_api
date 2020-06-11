import os, sys
import shutil
import traceback
from pathlib import Path

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

videos_dir = '{}/videos/'.format(os.getcwd())


@router.get("/user", response_model=schemas.User)
@util.global_exception_handler
def test_auth(user : models.User = Depends(core.authenticate_user)):
    print(user)
    return user


@router.get("/video/{tutorial_name}", tags=["video"], status_code=200)
@util.global_exception_handler
def get_video_tutorial(
    tutorial_name: str,
    user : schemas.User = Depends(core.authenticate_user)
):
    """
    - Video files stored in a file storage service like amazon s3 buckets
    - A source url can point direct to this files without passing the server
    - but that means anyone will be able to view this videos

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
    file_content = open(videos_dir + tutorial_name, mode='rb')
    return StreamingResponse(file_content, media_type="video/mp4")


@router.post("/video", response_model=schemas.UploadedFile, tags=["video"], status_code=201)
@util.global_exception_handler
def upload_video_tutorial(
    uploaded_file: UploadFile = File(...),
    user : schemas.User = Depends(core.authenticate_user)
):
    """
    Upload video tutorials and their names
    just incase this won't be uploaded directly to a file storage service

    The file name is the tutorial name
    """

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

@router.post("/exam", response_model=schemas.ExamOut, tags=["exam"], status_code=201)
@util.global_exception_handler
def create_exam(
    exam: schemas.Exam,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Demostrate creating a new exam.
    """
    return core.create_exam(user, exam)

@router.post("/exam/question", response_model=schemas.QuestionOut, tags=["exam"], status_code=201)
@util.global_exception_handler
def create_question(
    question: schemas.Question,
    user : models.User = Depends(core.authenticate_user)
):
    """
    Demostrate creating a new question for a particular exam.
    """
    return core.create_question(user, question)

@router.post("/exam/submission", response_model=schemas.SubmissionOut, tags=["exam"], status_code=201)
@util.global_exception_handler
def create_submission(
    submission: schemas.Submission,
    user : models.User = Depends(core.authenticate_user)
):
    """
    1. Fetch exam from database
    2. Compare submitted answers to tutors answers
       and use that to grade the learner.
    """
    return core.create_submission(user, submission)

@router.post("/exam/submission/mark", response_model=schemas.SubmissionOut, tags=["exam"], status_code=201)
@util.global_exception_handler
def mark_submission(
    submission: schemas.MarkSubmission,
    user : models.User = Depends(core.authenticate_user)
):
    """
    1. Fetch exam from database
    2. Compare submitted answers to tutors answers
       and use that to grade the learner.
    """
    return core.mark_submission(user, submission)

@router.post("/notification", tags=["notification"], status_code=201)
@util.global_exception_handler
def notify_users(notification : schemas.Notification):
    """
    1. Payload has learner id, channel_type and message
    2. Channel type can be email or sms or any other.
    3. This endpoint only fetches learner info like phone number and
       sends them the message contained in the payload.
    """
    learner_id = notification.learner_id
    profile = get_learner_profile(learner_id)
    if notification.channel == "sms":
        send_sms(profile['phone_number'], notification.message)
    else:
        send_email(profile['email'], notification.message)
    return {"status": "success"}

@router.post("/mentorship", tags=["mentorship"], status_code=201)
@util.global_exception_handler
def request_for_mentorship(mentorship : schemas.Mentorship):
    """
    1. Notify respective tutor of request
    2. Store mentorship request for tracking
    """
    pass

def get_learner_profile(learner_id):
    return {"phone_number": "xyz", "email": "xyz"}

def send_sms(phone_number, message):
    """
    Use a bulk sms service like Africastalking
    """
    pass

def send_email(phone_number, message):
    """
    User a mass mailing service like sendgrid
    """ 
    pass

def get_tutor_profile(tutor_id):
    return {"phone_number": "xyz", "email": "xyz"}