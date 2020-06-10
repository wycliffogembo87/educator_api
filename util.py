import os
import errno
import traceback

from fastapi import status
from fastapi import HTTPException

from loguru import logger
from functools import wraps

from pony.orm.core import TransactionIntegrityError


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

    logs_name = "logs/sm.log.{time}"

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
        print("Before, " + func.__name__ + " returns:")
        response = func(*args, **kwargs)
        print("After, " + func.__name__ + " returns:")
        return response
    return function_wrapper


def global_exception_handler(func):
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
        except HTTPException:
            raise
        except TransactionIntegrityError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=("This record cannot be submitted more than once")
            )
        except Exception as err:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err)
            )
        
        return response
    return function_wrapper