import os
import errno

from loguru import logger


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