from starlette.config import Config
from starlette.datastructures import Secret

from util import Role

# Config will be read from environment variables and/or ".env" files.

config = Config(".env")

DEBUG = config('DEBUG', cast=bool, default=False)

ENVIRONMENT = config('ENVIRONMENT', default='staging')

SECRET_KEY = config('SECRET_KEY', cast=Secret)

DB_USER = config('DB_USER')
DB_PASS = config('DB_PASS', cast=Secret)
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
DB_PORT = config('DB_PORT', default='5432')

DATABASE_URL = config('DATABASE_URL')

AFRICASTALKING_API_KEY = config('AFRICASTALKING_API_KEY', cast=Secret)
AFRICASTALKING_API_SENDER_ID = config('AFRICASTALKING_API_SENDER_ID')
AFRICASTALKING_API_URL = config('AFRICASTALKING_API_URL')
AFRICASTALKING_API_USERNAME = config('AFRICASTALKING_API_USERNAME')

roles = dict(
    upload_file=[Role.tutor],
    create_exam=[Role.tutor],
    add_participant=[Role.tutor],
    create_question=[Role.tutor],
    create_submission=[Role.learner],
    mark_submission=[Role.tutor],
    get_exam_performance=[Role.tutor],
    notify_user=[Role.tutor, Role.staff, Role.admin],
    request_form_mentorship=[Role.learner]
)