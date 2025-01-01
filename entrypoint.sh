#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

exec gunicorn -w 3 -b 0.0.0.0:8000 LearningPlatform.wsgi
