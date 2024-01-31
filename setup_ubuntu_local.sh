#!/bin/bash

set +o histexpand
set -eu

#####
# Install required software
#####
sudo apt-get update -y
sudo add-apt-repository universe -y
sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main" -y
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update -y

packages=("gcc" "git" "curl" "nginx" "certbot" "python3-django" "postgresql" "postgresql-contrib" "python3-pip" "python3.10-venv")

for package in "${packages[@]}"; do
  if ! dpkg-query -W -f='${Status}\n' "$package" | grep -q "ok installed"; then
    echo "Package $package is not installed. Installing..."
    sudo apt-get install -y "$package"
  else
    echo "Package $package is already installed. Skipping..."
  fi
done

echo "Checking if systemd is enabled"
SYSTEMD_PID=$(pidof systemd)

echo "Restarting Postgresql"
if [ "${SYSTEMD_PID}" == "" ]; then
    sudo systemctl start postgresql >> /dev/null
else
    sudo service postgresql start >> /dev/null
fi

#####
# Get Postgres version
#####
echo "Checking version of Postgres"
VERSION=$( $(sudo find /usr -wholename '*/bin/postgres') -V | (grep -E -oah -m 1 '[0-9]{1,}') | head -1)
echo "Found version $VERSION"



#####
# Replace `peer` with `md5` in the pg_hba file to enable peer authentication
#####
sudo sed -i -e 's/peer/trust/g' /etc/postgresql/"$VERSION"/main/pg_hba.conf


#####
# Check for systemd
#####
pidof systemd && sudo systemctl restart postgresql || sudo service postgresql restart


#####
# Create the role in the database
#####
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
psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $LEARN_OPS_USER;"
COMMANDS



#####
# Create directory to store static files and take ownership
#####
API_HOME="${pwd}"
echo "Creating static file directory"
sudo mkdir -p /var/www/learning.nss.team
sudo chown "$LEARN_OPS_USER":www-data /var/www/learning.nss.team



#####
# Create socialaccount.json fixture
#####
export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"
echo "Creating socialaccount fixture"

sudo tee $API_HOME/LearningAPI/fixtures/socialaccount.json <<EOF
[
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
            "client_id": "$LEARN_OPS_CLIENT_ID",
            "secret": "$LEARN_OPS_SECRET_KEY",
            "key": "",
            "sites": [
                1
            ]
        }
    }
]
EOF

echo "Generating Django password"
DJANGO_GENERATED_PASSWORD=$(python3 ./djangopass.py "$SUPERPASS" >&1)

sudo tee $API_HOME/LearningAPI/fixtures/superuser.json <<EOF
[
    {
        "model": "auth.user",
        "pk": null,
        "fields": {
            "password": "$DJANGO_GENERATED_PASSWORD",
            "last_login": null,
            "is_superuser": true,
            "username": "$SUPERUSER",
            "first_name": "Admina",
            "last_name": "Straytor",
            "email": "me@me.com",
            "is_staff": true,
            "is_active": true,
            "date_joined": "2023-03-17T03:03:13.265Z",
            "groups": [
                2
            ],
            "user_permissions": []
        }
    }
]
EOF


#####
# Install project requirements and run migrations
#####
export VIRTUAL_ENV="$(pwd)/.venv"
echo "VIRTUAL_ENV=$VIRTUAL_ENV" >.env
echo "PIPENV_VENV_IN_PROJECT=1" >>.env
echo "LEARNING_GITHUB_CALLBACK=http://localhost:3000/auth/github" >>.env

pip3 install --upgrade pip setuptools
python3 -m venv $VIRTUAL_ENV
source $VIRTUAL_ENV/bin/activate
pip3 install django
pip3 install wheel
pip3 install -r requirements.txt

python3 manage.py migrate
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
python3 manage.py loaddata superuser
rm $API_HOME/LearningAPI/fixtures/superuser.json
python3 manage.py collectstatic --noinput


