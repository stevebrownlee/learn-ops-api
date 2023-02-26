#!/bin/bash

# Dump the existing database
psql -U $LEARN_OPS_USER $LEARN_OPS_DB -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'"  | psql -U $LEARN_OPS_USER $LEARN_OPS_DB

# Delete existing migrations and create DB
# rm -rf ./LearningAPI/migrations
python3 manage.py migrate
# python3 manage.py makemigrations LearningAPI
# python3 manage.py migrate LearningAPI

# Load data from backup
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
