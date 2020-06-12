import os
import errno
import traceback
from enum import Enum

from fastapi import status
from fastapi import HTTPException

from loguru import logger
from functools import wraps

from passlib.context import CryptContext

from pony.orm.core import TransactionIntegrityError
from pony.orm.dbapiprovider import StrConverter


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

def logger_setup():
    mkdir_p('{}/logs'.format(os.getcwd()))

    logs_name = "logs/educator_api.log"

    logger.add(
        logs_name,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="12:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )


def decorator(func):
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        """ function_wrapper of greeting """
        logger.debug("Before, " + func.__name__ + " returns:")
        response = func(*args, **kwargs)
        logger.debug("After, " + func.__name__ + " returns:")
        return response
    return function_wrapper


def global_exception_handler(func):
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
        except HTTPException as err:
            logger.error(err)
            logger.debug(traceback.format_exc())
            raise
        except TransactionIntegrityError as err:
            logger.error(err)
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=("This record cannot be submitted more than once")
            )
        except Exception as err:
            logger.error(err)
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err)
            )
        logger.info(response)
        
        return response
    return function_wrapper