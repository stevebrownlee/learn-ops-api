#!/bin/bash

sudo -u postgres psql -c "DROP DATABASE IF EXISTS $LEARN_OPS_DB WITH (FORCE);"
sudo -u postgres psql -c "CREATE DATABASE $LEARN_OPS_DB;"

sudo -u postgres psql -c "CREATE USER $LEARN_OPS_USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
sudo -u postgres psql -c "ALTER ROLE $LEARN_OPS_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $LEARN_OPS_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $LEARN_OPS_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $LEARN_OPS_DB TO $LEARN_OPS_USER;"
