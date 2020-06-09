import os

from fastapi import FastAPI

import settings
import util

from api import v1

util.logger_setup()

app = FastAPI(title='EducatorAPI ({})'.format(settings.ENVIRONMENT))
app.include_router(v1.router, prefix='/api/v1')