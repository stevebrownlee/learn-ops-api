#!/bin/sh

# Exit on any error
set -e

echo "Starting production entrypoint..."

# Wait for database to be ready
echo "Waiting for database..."
python << END
import sys
import time
import psycopg2
from django.conf import settings

# Configure Django settings
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearningPlatform.settings')
django.setup()

suggest_unrecoverable_after = 30
start = time.time()

while True:
    try:
        psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
        )
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("Waiting for database... ({})\n".format(error))
        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(error))
    time.sleep(1)
END

echo "Database is ready!"

# Run Django management commands
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('LEARN_OPS_SUPERUSER_NAME')
password = os.environ.get('LEARN_OPS_SUPERUSER_PASSWORD')

if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print(f"Superuser {username} created successfully")
else:
    print("Superuser already exists or credentials not provided")
END

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --user app \
    --group app \
    --log-level info \
    --access-logfile /api/logs/gunicorn-access.log \
    --error-logfile /api/logs/gunicorn-error.log \
    LearningPlatform.wsgi:application