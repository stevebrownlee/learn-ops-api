#!/bin/bash

set -e

sudo apt update -y
sudo apt install git curl python3-pip postgresql postgresql-contrib -y
pidof systemd && sudo servicectl start postgresql || service postgresql start

# Create directory to store static files and take ownership
sudo mkdir /var/www/learning.nss.team
sudo chown $USER:www-data /var/www/learning.nss.team

# Create the role in the database
sudo su - postgres <<EOF
psql -c "DROP DATABASE IF EXISTS $LEARN_OPS_DB WITH (FORCE);"
psql -c "CREATE DATABASE $LEARN_OPS_DB;"
psql -c "CREATE USER $LEARN_OPS_USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $LEARN_OPS_DB TO $LEARN_OPS_USER;"
EOF

# Create the Ubuntu account
useradd -p $(openssl passwd -1 $LEARN_OPS_PASSWORD) $LEARN_OPS_USER

# Get Postgres version
VERSION=$(postgres -V | egrep -o '[0-9]{1,}\.[0-9]{1,}')

# Replace `peer` with `md5` in the pg_hba file to enable peer authentication
sudo sed -i -e 's/peer/md5/g' /etc/postgresql/$VERSION/main/pg_hba.conf

# Check for systemd
pidof systemd && sudo servicectl restart postgresql || service postgresql restart

# Create socialaccount.json fixture
echo '[
    {
       "model": "sites.site",
       "pk": 1,
       "fields": {
          "domain": "learningplatform.com",
          "name": "Learning Platform"
       }
    },
    {
        "model": "socialaccount.socialapp",
        "pk": 1,
        "fields": {
            "provider": "github",
            "name": "Github",
            "client_id": "'"$LEARN_OPS_CLIENT_ID"'",
            "secret": "'"$LEARN_OPS_SECRET_KEY"'",
            "key": "",
            "sites": [
                1
            ]
        }
    }
  ]
' > ./LearningAPI/fixtures/socialaccount.json

# Install project requirements
pip3 install -r requirements.txt

# Run existing migrations
python3 manage.py migrate

# Load data from backup
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
