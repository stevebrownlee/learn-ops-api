#!/bin/bash

# Dump the existing database
set -e
sudo su - postgres <<EOF
psql -U $LEARN_OPS_USER $LEARN_OPS_DB -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'"  | psql -U $LEARN_OPS_USER $LEARN_OPS_DB
EOF

# Run existing migrations
python3 manage.py migrate

# Load data from backup
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
