from starlette.config import Config
from starlette.datastructures import Secret

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
