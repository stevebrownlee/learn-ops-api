#!/bin/bash

# ************************************************************************
# SAMPLE USAGE
#
# ./setup_ubuntu.sh \
#     --client=githuboauthappclientid \
#     --secret=githuboauthappseretkey \
#     --password=passwordofyourchoice \
#     --django="longstringofrandomcharacters" \
#     --hosts="learning.nss.team,learningapi.nss.team,127.0.0.1,localhost" \
#     --user=ubuntu
#
# ************************************************************************

set +o histexpand
set -eu

for i in "$@"
do
case $i in
    -h=*|--hosts=*)
    HOSTS="${i#*=}"
    ;;
    -p=*|--password=*)
    PASSWORD="${i#*=}"
    ;;
    -s=*|--secret=*)
    OAUTHSECRET="${i#*=}"
    ;;
    -c=*|--client=*)
    CLIENT="${i#*=}"
    ;;
    -d=*|--django=*)
    DJANGOSECRET="${i#*=}"
    ;;
    -u=*|--user=*)
    CURRENTUSER="${i#*=}"
    ;;
    -k=*|--slack=*)
    SLACKTOKEN="${i#*=}"
    ;;
    --default)
    DEFAULT=YES
    ;;
    *)
            # unknown option
    ;;
esac
done

export LEARN_OPS_CLIENT_ID=${CLIENT}
export LEARN_OPS_SECRET_KEY=${OAUTHSECRET}
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER=learnops
export LEARN_OPS_PASSWORD="${PASSWORD}"
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
export LEARN_OPS_DJANGO_SECRET_KEY="${DJANGOSECRET}"
export LEARN_OPS_ALLOWED_HOSTS="${HOSTS}"
export SLACK_BOT_TOKEN=${SLACKTOKEN}

echo "export LEARN_OPS_CLIENT_ID=${CLIENT}
export LEARN_OPS_SECRET_KEY=${OAUTHSECRET}
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER=learnops
export LEARN_OPS_PASSWORD=\"${PASSWORD}\"
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
export LEARN_OPS_DJANGO_SECRET_KEY=\"${DJANGOSECRET}\"
export LEARN_OPS_ALLOWED_HOSTS=\"${HOSTS}\"
export SLACK_BOT_TOKEN=${SLACKTOKEN}
" >> ~/.bashrc

source /home/$CURRENTUSER/.bashrc

sudo apt update -y
sudo apt install git curl python3-pip postgresql postgresql-contrib -y

echo "Checking if systemd is enabled"
SYSTEMD_PID=$(pidof systemd)

echo "Restarting Postgresql"
if [ x"${SYSTEMD_PID}" == "x" ]; then
    sudo systemctl start postgresql >> /dev/null
else
    sudo service postgresql start >> /dev/null
fi

# Create directory to store static files and take ownership
echo "Creating static file directory"
sudo mkdir -p /var/www/learning.nss.team
sudo chown $USER:www-data /var/www/learning.nss.team

# # Create the role in the database
echo "Creating Postgresql role and database"

set -e

sudo su - postgres <<COMMANDS
psql -c "DROP DATABASE IF EXISTS $LEARN_OPS_DB WITH (FORCE);"
psql -c "CREATE DATABASE $LEARN_OPS_DB;"
psql -c "CREATE USER $LEARN_OPS_USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE $LEARN_OPS_USER SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $LEARN_OPS_DB TO $LEARN_OPS_USER;"
COMMANDS

# Create the Ubuntu account
echo "Creating Linux user matching Postgres database"
sudo useradd -p $(openssl passwd -1 $LEARN_OPS_PASSWORD) $LEARN_OPS_USER

# Get Postgres version
echo "Checking version of Postgres"
VERSION=$( $(sudo find /usr -wholename '*/bin/postgres') -V | (egrep -oah -m 1 '[0-9]{1,}') | head -1)
echo "Found version $VERSION"


# Replace `peer` with `md5` in the pg_hba file to enable peer authentication
sudo sed -i -e 's/peer/md5/g' /etc/postgresql/$VERSION/main/pg_hba.conf

# Check for systemd
pidof systemd && sudo systemctl restart postgresql || service postgresql restart

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
