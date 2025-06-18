#!/bin/bash

set +o histexpand
set -eu
source .env

# If changes need to be made to user's config file, detect the correct one
[[ "$SHELL" == *"bash"* ]] && config_file=".bashrc" || config_file=".zshrc"

manage_service() {
    local service=$1
    local action=$2 # start, stop, or restart
    local service_command=""

    # Detect the init system
    if [[ $(/sbin/init --version) =~ upstart ]]; then
        service_command="sudo service $service $action"
    elif [[ $(systemctl) =~ -\.mount ]]; then
        service_command="sudo systemctl $action $service"
    elif [[ -f /etc/init.d/postgresql ]]; then
        service_command="sudo /etc/init.d/$service $action"
    else
        echo "Init system not supported!"
        return 1
    fi

    # Execute the service command
    echo "Executing: $service_command"
    $service_command
}

#####
# Install required software
#####
sudo apt-get update -y

# Check if PostgreSQL is installed
if ! command -v psql &>/dev/null; then
    echo "PostgreSQL is not installed"
    sudo apt install postgresql postgresql-contrib -y
fi

# Check if systemd is running by examining the presence of systemd's runtime directory
echo "Restarting Postgresql"
manage_service postgresql start

#####
# Get Postgres version
#####
echo "Checking version of Postgres"
VERSION=$($(sudo find /usr -wholename '*/bin/postgres') -V | (grep -E -oah -m 1 '[0-9]{1,}') | head -1)
echo "Found version $VERSION"

#####
# Replace `peer` with `md5` in the pg_hba file to enable peer authentication
# and restart the postgres service to enable the changes
#####
sudo sed -i -e 's/peer/trust/g' /etc/postgresql/"$VERSION"/main/pg_hba.conf
manage_service postgresql restart

#####
# Create the role in the database
#####
echo "Creating Postgresql role and database"

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

# Install Node - Needs to be below zsh set up because of the shell environment
if ! command -v nvm &> /dev/null; then
  echo -e "Installing Node Version Manager..."

  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  source ~/.zshrc &>zsh-reload.log
fi

nvm install --lts
nvm use --lts

#####
# Install Pyenv and required Python version
#####
if command -v pyenv &>/dev/null; then
    echo "pyenv is installed."
else
    echo "Installing pyenv..."

    directory_path="$HOME/.pyenv"
    if [ -d "$directory_path" ]; then
        # Directory exists, now delete it
        echo "Directory exists. Deleting $directory_path..."
        rm -rf "$directory_path"

        # Check if deletion was successful
        if [ ! -d "$directory_path" ]; then
            echo "Directory successfully deleted."
        else
            echo "Failed to delete directory."
        fi
    else
        echo "Directory does not exist."
    fi

    # Install dependency packages that are necessary to install pyenv on WSL Ubuntu environment
    sudo apt install -y curl git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

    # Install pyenv on WSL Ubuntu environment
    curl https://pyenv.run | bash

    # Add necessary config to shell profile (.zshrc)
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"' >>$HOME/$config_file

    # Update path of current subshell execution
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
fi

# Check if Python 3.11.11 is installed
if pyenv versions --bare | grep -q '^3.11.11$'; then
    echo "Python 3.11.11 is already installed."
else
    echo "Python 3.11.11 is not installed. Installing now..."
    pyenv install 3.11.11
fi

# Get the global Python version set in pyenv
global_version=$(pyenv global)

# Check that global version of python is 3.11.11
if [[ $global_version == '3.11.11' ]]; then
    echo "Python 3.11.11 is the global version."
else
    echo "Python 3.11.11 is not the global version. The global version is $global_version."
    echo "Setting global version of python to 3.11.11"
    pyenv global 3.11.11
fi

# Install pipenv for managing virtual environment
pip3 install pipenv django

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
pipenv --python 3.11.11
pipenv install
pipenv run migrate

# Load data from backup
pipenv run bash -c "python3 manage.py flush --no-input \
    && python3 manage.py loaddata socialaccount \
    && python3 manage.py loaddata complete_backup \
    && python3 manage.py loaddata superuser"

sudo rm -f ./LearningAPI/fixtures/superuser.json
sudo rm -f ./LearningAPI/fixtures/socialaccount.json

echo "LEARNING_GITHUB_CALLBACK=http://localhost:3000/auth/github" >>.env

code --install-extension ms-python.python --force
code --install-extension ms-python.vscode-pylance --force
code --install-extension njpwerner.autodocstring --force
code --install-extension streetsidesoftware.code-spell-checker --force
code --install-extension ms-vscode-remote.remote-wsl --force
code --install-extension ms-python.pylint --force
code --install-extension ms-python.black-formatter --force