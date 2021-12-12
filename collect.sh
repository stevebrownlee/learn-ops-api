#!/bin/bash
python3 manage.py collectstatic --noinput
chown -R chortlehoort ./staticfiles