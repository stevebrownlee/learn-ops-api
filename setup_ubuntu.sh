#!/bin/bash


# ************************************************************************
# SAMPLE USAGE
#
# ./setup_ubuntu.sh \
#     --client=GithubOAuthAppClientId \
#     --secret=GithubOAuthAppSeretKey \
#     --password=DBPasswordOfYourChoice \
#     --django="longstringofrandomcharacters" \
#     --hosts="IP.ADDRESS.OF.VM,127.0.0.1,localhost" \
#     --user=ubuntu
#     --supass=SuperuserPasswordOfYourChoice
#
# ************************************************************************

set +o histexpand
set -eu

for i in "$@"
do
case $i in
    -h=*|--hosts=*) HOSTS="${i#*=}" ;;
    -p=*|--password=*) PASSWORD="${i#*=}" ;;
    -s=*|--secret=*) OAUTHSECRET="${i#*=}" ;;
    -c=*|--client=*) CLIENT="${i#*=}" ;;
    -d=*|--django=*) DJANGOSECRET="${i#*=}" ;;
    -k=*|--slack=*) SLACKTOKEN="${i#*=}" ;;
    -u=*|--suser=*) SUPERUSER="${i#*=}" ;;
    -w=*|--supass=*) SUPERPASS="${i#*=}" ;;
    --default) DEFAULT=YES ;;
    *) # unknown option ;;
esac
done


export LEARN_OPS_CLIENT_ID="$CLIENT"
export LEARN_OPS_SECRET_KEY="$OAUTHSECRET"
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER=learnops
export LEARN_OPS_PASSWORD="$PASSWORD"
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
export LEARN_OPS_DJANGO_SECRET_KEY="$DJANGOSECRET"
export LEARN_OPS_ALLOWED_HOSTS="$HOSTS"
export SLACK_BOT_TOKEN="$SLACKTOKEN"

#####
# Create the Ubuntu user account
#####
USER_HOME="/home/$LEARN_OPS_USER"
if id "$LEARN_OPS_USER" >>/dev/null 2>&1; then
    echo "User exists"
else
    echo "Creating Linux user matching Postgres database"
    sudo useradd -p "$(openssl passwd -1 "$LEARN_OPS_PASSWORD")" "$LEARN_OPS_USER"
    sudo mkdir -p "$USER_HOME"
    sudo usermod -d $USER_HOME $LEARN_OPS_USER
    sudo chown -R $LEARN_OPS_USER $USER_HOME
fi


#####
# Create shell init file and reload
#####
sudo tee $USER_HOME/.bashrc <<EOF
export LEARN_OPS_CLIENT_ID=$CLIENT
export LEARN_OPS_SECRET_KEY=$OAUTHSECRET
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER=learnops
export LEARN_OPS_PASSWORD=$PASSWORD
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
export LEARN_OPS_DJANGO_SECRET_KEY=$LEARN_OPS_DJANGO_SECRET_KEY
export LEARN_OPS_ALLOWED_HOSTS=$HOSTS
export SLACK_BOT_TOKEN=$SLACKTOKEN
export PATH=$PATH:/home/learnops/.local/bin
EOF
sudo su - learnops -c "bash -c 'source ~/.bashrc'"

# sudo su - learnops -c "source ~/.bashrc"


#####
# Install required software
#####
sudo apt-get update -y
packages=("gcc" "git" "curl" "nginx" "certbot" "python3-django" "postgresql-12" "postgresql-contrib-12" "python3-pip" "python3.8-venv")

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
COMMANDS


#####
# Create directory to store static files and take ownership
#####
echo "Creating static file directory"
sudo mkdir -p /var/www/learning.nss.team
sudo chown "$LEARN_OPS_USER":www-data /var/www/learning.nss.team


#####
# Clone the project into /var/www/learningapi
#####
API_HOME=/var/www/learningapi
echo "Creating project directory"
if [ ! -d $API_HOME ]; then
    sudo mkdir $API_HOME
fi

echo "Setting ${LEARN_OPS_USER} as owner of project directory"
sudo chown "${LEARN_OPS_USER}":www-data $API_HOME

cd $API_HOME
if [ -f "$API_HOME/manage.py" ]; then
    echo "Cleaning project directory"
    sudo rm -rf $API_HOME/{*,.[a-zA-z]*}
fi
echo "Cloning project"
sudo git clone https://github.com/stevebrownlee/learn-ops-api.git .
sudo chown -R learnops $API_HOME


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
# Install project requirements
#####
echo "Installing project requirements"
sudo su - learnops << EOF
cd $API_HOME
python3 -m venv venv
source venv/bin/activate
pip3 install django
pip3 install -r requirements.txt >> /dev/null
EOF

#####
# Run existing migrations
#####
echo "Running DB migrations"
if [ ! -d "$API_HOME/logs" ]; then
    mkdir $API_HOME/logs
fi
sudo chown -R learnops:www-data $API_HOME/logs
sudo su - learnops << EOF
cd $API_HOME
source ~/.bashrc

python3 manage.py migrate
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
python3 manage.py loaddata superuser
rm $API_HOME/LearningAPI/fixtures/superuser.json
EOF


#####
# Create gunicorn service file and start service
#####
SVC_FILE_CONTENTS=$(cat << EOF
[Unit]
Description=learnops gunicorn daemon
After=network.target
# Comment
[Service]
Environment="DEBUG=False"
Environment="DEVELOPMENT_MODE=False"
Environment="LEARNING_GITHUB_CALLBACK=https://learning.nss.team/auth/github"
Environment="SLACK_BOT_TOKEN=${SLACKTOKEN}"
Environment="LEARN_OPS_DB=${LEARN_OPS_USER}"
Environment="LEARN_OPS_USER=${LEARN_OPS_USER}"
Environment="LEARN_OPS_PASSWORD=${PASSWORD}"
Environment="LEARN_OPS_HOST=localhost"
Environment="LEARN_OPS_PORT=5432"
Environment="LEARN_OPS_CLIENT_ID=${LEARN_OPS_CLIENT_ID}"
Environment="LEARN_OPS_SECRET_KEY=${LEARN_OPS_SECRET_KEY}"
Environment="LEARN_OPS_DJANGO_SECRET_KEY=${LEARN_OPS_DJANGO_SECRET_KEY}"
Environment="LEARN_OPS_ALLOWED_HOSTS=${LEARN_OPS_ALLOWED_HOSTS}"
User=${LEARN_OPS_USER}
Group=www-data
WorkingDirectory=$API_HOME
ExecStart=/var/www/learningapi/venv/bin/gunicorn -w 3 --bind 127.0.0.1:8000 --log-file /var/www/learningapi/learning.log --access-logfile /var/www/learningapi/learning-access.log LearningPlatform.wsgi
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
)

echo "$SVC_FILE_CONTENTS" > .service
sudo mv .service /etc/systemd/system/learning.service
sudo systemctl enable learning
sudo systemctl daemon-reload
if [ "${SYSTEMD_PID}" == "" ]; then
    sudo systemctl start learning >> /dev/null
else
    sudo service learning start >> /dev/null
fi
