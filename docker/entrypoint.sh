#!/bin/sh

export APP_STATIC_FILE_PATH=/tmp/deployment-manager

mkdir -p "$APP_STATIC_FILE_PATH"

python manage.py migrate --no-input

python manage.py collectstatic --no-input

python manage.py runserver 0.0.0.0:8000
# gunicorn languages.wsgi:application --bind 0.0.0.0:8000
