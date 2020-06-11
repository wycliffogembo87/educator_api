import os
import random
from datetime import datetime as dt
from enum import Enum
from loguru import logger

from uuid import UUID
from uuid import uuid4

from pony.orm import Database
from pony.orm import Required
from pony.orm import Optional
from pony.orm import db_session
from pony.orm import PrimaryKey
from pony.orm import Json
from pony.orm import Set
from pony.orm import StrArray
from pony.orm import composite_key
from pony.orm import set_sql_debug
from pony.orm.dbapiprovider import StrConverter

import settings


class Status(Enum):
    active = 0
    inactive = 1
    suspended = 2

class Role(Enum):
    tutor = 0
    learner = 1
    staff = 2
    admin = 3

class Mark(Enum):
    tick = 0
    cross = 1
    auto_tick = 2
    auto_cross = 3
    unmarked = 4

class EnumConverter(StrConverter):
    def validate(self, val, obj=None):
        if not isinstance(val, Enum):
            raise ValueError('Must be an Enum. Got {}'.format(val))
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, val):
        # Any enum type can be used, so py_type ensures the
        # correct one is used to create the enum instance
        return self.py_type[val]

    def sql_type(self):
        return 'VARCHAR(30)'


db = Database()

set_sql_debug(True)

logger.debug("DB_USER: {}".format(settings.DB_USER))
logger.debug("DB_PASS: {}".format(str(settings.DB_PASS)))
logger.debug("DB_HOST: {}".format(settings.DB_HOST))
logger.debug("DB_NAME: {}".format(settings.DB_NAME))
logger.debug("DB_PORT: {}".format(settings.DB_PORT))

db.bind(
    provider='postgres',
    user=settings.DB_USER,
    password=str(settings.DB_PASS),
    host=settings.DB_HOST,
    database=settings.DB_NAME,
    port=settings.DB_PORT
)
db.provider.converter_classes.append((Enum, EnumConverter))

class User(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    username = Required(str, unique=True)
    password = Required(str)
    phone_number = Required(str, unique=True)
    phone_number_verified = Required(bool, default=False)
    email = Required(str, unique=True)
    email_verified = Required(bool, default=False)
    role = Required(Role, default=Role.learner)
    status = Required(Status, default=Status.active)
    level = Required(int, default=1)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    notifications = Set('Notification')
    exams = Set('Exam')
    submissions = Set('Submission')
    performances = Set('Performance')
    notifications = Set('Notification')
    mentorships = Set('Mentorship')


class Exam(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    name = Required(str, index=True)
    video_tutorial_name = Optional(str, index=True)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    user = Required(User)
    questions = Set('Question')
    performances = Set('Performance')


class Question(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    number = Optional(int, index=True)
    text = Required(str)
    multi_choice = Optional(StrArray)
    marks = Required(int)
    answer = Optional(str)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    exam = Required(Exam)
    submissions = Set('Submission')
    composite_key(exam, number)

class Submission(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    answer = Required(str)
    mark = Required(Mark, default=Mark.unmarked)
    marks_obtained = Required(int, default=0)
    comment = Optional(str)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    question = Required(Question)
    user = Required(User)
    composite_key(user, question)

class Mentorship(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    tutor = Required(UUID, index=True)
    challenge_being_faced = Required(str)
    is_active = Required(bool, default=True)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    user = Required(User)


class Notification(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    user = Required(User)


class Grade(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    starting_percentage = Required(int, unique=True)
    ending_percentage = Required(int, unique=True)
    letter_grade = Required(str, unique=True)
    four_point_zero_grade = Required(float)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    performances = Set('Performance')


class Performance(db.Entity):
    id = PrimaryKey(UUID, default=uuid4, auto=True)
    ticks = Required(int)
    crosses = Required(int)
    unmarked = Required(int)
    marks_obtained = Required(int)
    total_marks = Required(int)
    total_number_of_questions = Required(int)
    percentage = Required(int)
    metadata = Required(Json, default={})
    created_at = Required(dt, default=lambda: dt.utcnow(), index=True)
    updated_at = Required(dt, default=lambda: dt.utcnow())
    grade = Required(Grade)
    exam = Required(Exam)
    user = Required(User)
    composite_key(user, exam)


db.generate_mapping(create_tables=True)


if __name__ == '__main__':
    db.generate_mapping(create_tables=True)
    db.drop_all_tables(with_all_data=True)
