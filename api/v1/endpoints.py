import os

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from schema import CreateExam
from schema import Submissions
from schema import Notification
from schema import Mentorship


router = APIRouter(redirect_slashes=False)


@router.get("/video/{tutorial_name}", tags=["video"], status_code=200)
def get_video_tutorial(tutorial_name: str):
    """
    Video files stored in a file storage service like amazon s3 buckets
    A source url can point direct to this files without passing the server
    but that means anyone will be able to view this videos

    Usage example:
        <!DOCTYPE html>
            <html>
                <body>
                    <video width="320" height="240" controls>
                        <source src="http://127.0.0.1:8000/video/test.mp4" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <
                    <input type="file" id="fileinput" />
                </body>
            </html>
    """
    file_name = '{}/{}'.format(os.getcwd(), tutorial_name)
    video_tutorial = open(file_name, mode='rb')
    return StreamingResponse(video_tutorial, media_type="video/mp4")


@router.post("/video", tags=["video"], status_code=201)
def upload_video_tutorial(
    fileb: UploadFile = File(...),
    tutorial_name: str = Form(...)
):
    """
    Upload video tutorials and their names
    just incase this won't be uploaded directly to a file storage service
    """
    return {
        "upload_status": "success",
        "tutorial_name": tutorial_name,
        "fileb_content_type": fileb.content_type,
    }

@router.post("/exam", response_model=CreateExam, tags=["exam"], status_code=201)
def create_exam(exam: CreateExam):
    """
    Demostrate creating a new exam.
    This data will be stored in relational database.
    """
    return exam

@router.post("/submission", tags=["exam"], status_code=201)
def process_submission(submissions: Submissions):
    """
    1. Fetch exam from database
    2. Compare filled answers to tutors answers
       and use that to grade the learner.
    """
    return {"score": "75%", "mean_grade": "A"}

@router.post("/notification", tags=["notification"], status_code=201)
def notify_users(notification : Notification):
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
def request_for_mentorship(mentorship : Mentorship):
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