#!/bin/bash

set -e

git clone https://github.com/stevebrownlee/learn-ops-api.git
sudo apt update -y
sudo apt install git curl python3-pip postgresql postgresql-contrib -y
sudo systemctl start postgresql.service
pip3 install -r requirements.txt

sudo mkdir /var/www/learning.nss.team
sudo chown $USER:www-data /var/www/learning.nss.team
