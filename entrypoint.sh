#!/bin/bash

set -e

# Wait for database to be ready
until PGPASSWORD=$LEARN_OPS_PASSWORD psql -h "$LEARN_OPS_HOST" -U "$LEARN_OPS_USER" -d "$LEARN_OPS_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Generate fixtures for development
export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"

# Create socialaccount fixture if it doesn't exist
if [ ! -f "./LearningAPI/fixtures/socialaccount.json" ]; then
    echo "Creating socialaccount fixture"
    echo $(pwd)
    echo $(ls)
    echo $(ls LearningAPI)
    cat > ./LearningAPI/fixtures/socialaccount.json <<EOF
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
fi

# Generate Django password and create superuser fixture if it doesn't exist
if [ ! -f "./LearningAPI/fixtures/superuser.json" ]; then
    echo "Creating superuser fixture"
    DJANGO_GENERATED_PASSWORD=$(pipenv run python ./djangopass.py "$LEARN_OPS_SUPERUSER_PASSWORD")
    cat > ./LearningAPI/fixtures/superuser.json <<EOF
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
            "email": "admin@learningplatform.local",
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
fi

# Run Django commands through pipenv (matching local development workflow)
echo "Running migrations..."
pipenv run python manage.py migrate

# Load fixtures
echo "Loading fixtures..."
pipenv run python manage.py loaddata socialaccount || echo "socialaccount fixture load failed"
pipenv run python manage.py loaddata complete_backup || echo "complete_backup fixture load failed"  
pipenv run python manage.py loaddata superuser || echo "superuser fixture load failed"

# Clean up temporary fixtures (keep them for development)
# rm -f ./LearningAPI/fixtures/superuser.json
# rm -f ./LearningAPI/fixtures/socialaccount.json

# Collect static files
echo "Collecting static files..."
pipenv run python manage.py collectstatic --noinput

# Start the Django development server within the virtual environment
echo "Starting Django development server within pipenv virtual environment..."
exec pipenv run python manage.py runserver 0.0.0.0:8000