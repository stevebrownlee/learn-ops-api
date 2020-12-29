#!/bin/bash
psql -U postgres learnops -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'"  | psql -U postgres learnops
rm -rf ./LearningAPI/migrations
python manage.py migrate
python manage.py makemigrations LearningAPI
python manage.py migrate LearningAPI
python manage.py loaddata groups
python manage.py loaddata users
python manage.py loaddata tokens
python manage.py loaddata nss_users
python manage.py loaddata cohorts

