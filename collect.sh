#!/bin/bash
python3 manage.py collectstatic --noinput
sudo chown -R chortlehoort ./staticfiles