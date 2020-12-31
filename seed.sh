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
python manage.py loaddata user_cohorts
python manage.py loaddata courses
python manage.py loaddata books
python manage.py loaddata projects
python manage.py loaddata chapters
python manage.py loaddata chapter_notes
python manage.py loaddata favorited_notes
python manage.py loaddata taxonomy_levels

