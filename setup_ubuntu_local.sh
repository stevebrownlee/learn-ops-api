#!/bin/bash

set +o histexpand
set -eu
source .env
#####
# Install required software
#####
# sudo apt-get update -y

# Check if PostgreSQL is installed
if ! command -v psql &>/dev/null; then
    echo "PostgreSQL is not installed"
    sudo apt install postgresql postgresql-contrib -y
fi

echo "Restarting Postgresql"
if [ -d /run/systemd/system ]; then
    echo "Systemd is enabled"
    sudo systemctl start postgresql >> /dev/null
else
    echo "Systemd is not enabled"
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
# Install Pyenv and required Python version
#####
if command -v pyenv &>/dev/null; then
    echo "pyenv is installed."
else
    # Install dependency packages that are necessary to install pyenv on WSL Ubuntu environment
    sudo apt install -y curl git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

    # Install pyenv on WSL Ubuntu environment
    curl https://pyenv.run | bash

    # Add necessary config to shell profile (.zshrc)
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"' >>$HOME/.zshrc

    # Update path of current subshell execution
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
fi

# Check if Python 3.9.1 is installed
if pyenv versions --bare | grep -q '^3.9.1$'; then
    echo "Python 3.9.1 is already installed."
else
    echo "Python 3.9.1 is not installed. Installing now..."
    pyenv install 3.9.1
fi

# Get the global Python version set in pyenv
global_version=$(pyenv global)

# Check that global version of python is 3.9.1
if [[ $global_version == '3.9.1' ]]; then
    echo "Python 3.9.1 is the global version."
else
    echo "Python 3.9.1 is not the global version. The global version is $global_version."
    echo "Setting global version of python to 3.9.1"
    pyenv global 3.9.1
fi


pip3 install pipenv


#####
# Create socialaccount.json fixture
#####
export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"
echo "Creating socialaccount fixture"

sudo tee ./LearningAPI/fixtures/socialaccount.json <<EOF
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
DJANGO_GENERATED_PASSWORD=$(python3 ./djangopass.py "$LEARN_OPS_SUPERUSER_PASSWORD" >&1)

sudo tee ./LearningAPI/fixtures/superuser.json <<EOF
[
    {
        "model": "auth.user",
        "pk": null,
        "fields": {
            "password": "$DJANGO_GENERATED_PASSWORD",
            "last_login": null,
            "is_superuser": true,
            "username": "$LEARN_OPS_SUPERUSER_NAME",
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
pipenv --python 3.9.1
pipenv install
pipenv run migrate

# Load data from backup
pipenv run bash -c "python3 manage.py flush --no-input \
    && python3 manage.py loaddata socialaccount \
    && python3 manage.py loaddata complete_backup \
    && python3 manage.py loaddata superuser"

rm ./LearningAPI/fixtures/superuser.json -y
rm ./LearningAPI/fixtures/socialaccount.json -y

echo "LEARNING_GITHUB_CALLBACK=http://localhost:3000/auth/github" >>.env
