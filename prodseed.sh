#!/bin/bash

scp chortlehoort@learning:/home/chortlehoort/api-actions-runner/_work/learn-ops-api/learn-ops-api/authusers.json .
scp chortlehoort@learning:/home/chortlehoort/api-actions-runner/_work/learn-ops-api/learn-ops-api/nssusers.json .
scp chortlehoort@learning:/home/chortlehoort/api-actions-runner/_work/learn-ops-api/learn-ops-api/social.json .
scp chortlehoort@learning:/home/chortlehoort/api-actions-runner/_work/learn-ops-api/learn-ops-api/records.json .
scp chortlehoort@learning:/home/chortlehoort/api-actions-runner/_work/learn-ops-api/learn-ops-api/entries.json .

python3 manage.py loaddata authusers.json
python3 manage.py loaddata nssusers.json
python3 manage.py loaddata social.json
python3 manage.py loaddata records.json
python3 manage.py loaddata entries.json

rm authusers.json
rm nssusers.json
rm social.json
rm records.json
rm entries.json
