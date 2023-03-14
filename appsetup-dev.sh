#!/bin/bash

sudo apt update -y
sudo apt install git curl python3-pip postgresql postgresql-contrib -y
sudo systemctl start postgresql.service

# service postgresql start as alternative

pipenv shell
pipenv install


