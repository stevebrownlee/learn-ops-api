#!/bin/bash

psql -c "DROP DATABASE IF EXISTS $USER WITH (FORCE);"
psql -c "CREATE DATABASE $USER;"
psql -c "CREATE USER $USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
psql -c "ALTER ROLE $USER SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE $USER SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE $USER SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"
