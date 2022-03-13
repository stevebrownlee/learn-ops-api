#!/bin/bash
# psql -U postgres learnops -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'"  | psql -U postgres learnops
psql postgresql://postgres:web571f8@127.0.0.1:5432/learnops -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'"  | psql -U postgres learnops
# rm -rf ./LearningAPI/migrations
python3 manage.py migrate
# python3 manage.py makemigrations LearningAPI
# python3 manage.py migrate LearningAPI
python3 manage.py loaddata groups
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata nss_users
python3 manage.py loaddata socialaccount
python3 manage.py loaddata cohorts
python3 manage.py loaddata user_cohorts
python3 manage.py loaddata courses
python3 manage.py loaddata books
python3 manage.py loaddata assessments
python3 manage.py loaddata student_assessment_statuses
python3 manage.py loaddata student_assessments
python3 manage.py loaddata projects
python3 manage.py loaddata chapters
python3 manage.py loaddata chapter_notes
python3 manage.py loaddata favorited_notes
python3 manage.py loaddata taxonomy_levels
python3 manage.py loaddata opportunities
python3 manage.py loaddata learning_weights
python3 manage.py loaddata learning_records
python3 manage.py loaddata learning_record_entries

