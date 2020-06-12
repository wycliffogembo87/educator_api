from loguru import logger

from pony.orm import db_session

from models import User
from models import Grade
from models import Role
from models import Status

import util


@db_session
def create_user(username : str, password : str, phone_number : str, email : str, role : Role):
    user = User(
        username=username,
        password=util.get_password_hash(password),
        phone_number=phone_number,
        email=email,
        role=role,
        status=Status.active
    )
    return user


@db_session
def populate_grades():
    grades = [
        dict(starting_percentage=0, ending_percentage=65, letter_grade="E/F", four_point_zero_grade=0.0),
        dict(starting_percentage=65, ending_percentage=66, letter_grade="D", four_point_zero_grade=1.0),
        dict(starting_percentage=67, ending_percentage=69, letter_grade="D+", four_point_zero_grade=1.3),
        dict(starting_percentage=70, ending_percentage=72, letter_grade="C-", four_point_zero_grade=1.7),
        dict(starting_percentage=73, ending_percentage=76, letter_grade="C", four_point_zero_grade=2.0),
        dict(starting_percentage=77, ending_percentage=79, letter_grade="C+", four_point_zero_grade=2.3),
        dict(starting_percentage=80, ending_percentage=82, letter_grade="B-", four_point_zero_grade=2.7),
        dict(starting_percentage=83, ending_percentage=86, letter_grade="B", four_point_zero_grade=3.0),
        dict(starting_percentage=87, ending_percentage=89, letter_grade="B+", four_point_zero_grade=3.3),
        dict(starting_percentage=90, ending_percentage=92, letter_grade="A-", four_point_zero_grade=3.7),
        dict(starting_percentage=93, ending_percentage=96, letter_grade="A", four_point_zero_grade=4.0),
        dict(starting_percentage=97, ending_percentage=100, letter_grade="A+", four_point_zero_grade=4.0)
    ]
    for grade in grades:
        g = Grade(**grade)
        logger.debug(g.to_dict())


@db_session
def populate_users():
    users = [
        dict(username='tutor', password=util.get_password_hash('tutor123'), phone_number="+254728043275", email="wycliff@brck.com", role=Role.tutor),
        dict(username='learner', password=util.get_password_hash('learner123'), phone_number="+254735688154", email="wycliffogembo87@gmail.com", role=Role.learner),
        dict(username='staff', password=util.get_password_hash('staff123'), phone_number="+254728043276", email="wycliffogembo88@gmail.com", role=Role.tutor),
        dict(username='admin', password=util.get_password_hash('admin123'), phone_number="+254728043277", email="wycliffogembo89@gmail.com", role=Role.tutor)
    ]
    for user in users:
        u = User(**user)
        logger.debug(u.to_dict())


if __name__ == '__main__':
    populate_users()
    populate_grades()