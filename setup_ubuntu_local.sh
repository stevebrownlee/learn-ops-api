#!/bin/bash

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
    sudo chsh -s /bin/bash $LEARN_OPS_USER
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


#####
# Install required software
#####
sudo apt-get update -y
sudo add-apt-repository universe -y
sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main" -y
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update -y

packages=("gcc" "git" "curl" "nginx" "certbot" "python3-django" "postgresql-12" "postgresql-contrib-12" "python3-pip" "python3.10-venv")

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
API_HOME=/mnt/learnops
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
VENV_DIR="/home/learnops/venv"
echo "Installing project requirements and migrating"
sudo su - learnops << EOF
source /home/learnops/.bashrc
export PATH=$PATH:/home/learnops/.local/bin
cd $API_HOME

pip3 install --upgrade pip setuptools
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip3 install django
pip3 install wheel
pip3 install -r requirements.txt

python3 manage.py migrate
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
python3 manage.py loaddata superuser
rm $API_HOME/LearningAPI/fixtures/superuser.json
python3 manage.py collectstatic --noinput
EOF


#####
# Create gunicorn service file and start service
#####
sudo tee /etc/systemd/system/learning.service <<EOF
[Unit]
Description=learnops gunicorn daemon
After=network.target

[Service]
Environment="DEBUG=True"
Environment="DEVELOPMENT_MODE=True"
Environment="LEARNING_GITHUB_CALLBACK=http://api.learning.local/auth/github"
Environment="SLACK_BOT_TOKEN=$SLACKTOKEN"
Environment="LEARN_OPS_DB=$LEARN_OPS_USER"
Environment="LEARN_OPS_USER=$LEARN_OPS_USER"
Environment="LEARN_OPS_PASSWORD=$PASSWORD"
Environment="LEARN_OPS_HOST=localhost"
Environment="LEARN_OPS_PORT=5432"
Environment="LEARN_OPS_CLIENT_ID=$LEARN_OPS_CLIENT_ID"
Environment="LEARN_OPS_SECRET_KEY=$LEARN_OPS_SECRET_KEY"
Environment="LEARN_OPS_DJANGO_SECRET_KEY=$LEARN_OPS_DJANGO_SECRET_KEY"
Environment="LEARN_OPS_ALLOWED_HOSTS=$LEARN_OPS_ALLOWED_HOSTS"
User=$LEARN_OPS_USER
Group=www-data
WorkingDirectory=$API_HOME
ExecStart=$VENV_DIR/bin/gunicorn -w 3 --bind 127.0.0.1:8000 --log-file /mnt/learnops/logs/learning.log --access-logfile /mnt/learnops/logs/learning-access.log LearningPlatform.wsgi
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable learning
sudo systemctl daemon-reload
if [ "${SYSTEMD_PID}" == "" ]; then
    sudo systemctl start learning >> /dev/null
else
    sudo service learning start >> /dev/null
fi


#####
# Create nginx reverse proxy for API
#####
sudo tee /etc/nginx/sites-available/api <<EOF
server {
    listen 80;
    server_name api.learning.local;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_redirect off;
    }

    location /static/ {
        autoindex off;
        root /var/www/learning.nss.team/;
    }
}
EOF

if [ ! -f /etc/nginx/sites-enabled/api ]; then
    sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api
fi
sudo systemctl restart nginx