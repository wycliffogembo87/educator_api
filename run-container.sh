#!/bin/bash

set -e

# Run migrations
dbmate up

# python app/seed.py

exec gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
