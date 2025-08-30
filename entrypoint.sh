#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL at $LEARN_OPS_HOST:$LEARN_OPS_PORT..."
    while ! pg_isready -h "$LEARN_OPS_HOST" -p "$LEARN_OPS_PORT" -U "$LEARN_OPS_USER"; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
}

# Wait for database to be ready
wait_for_postgres

echo "PostgreSQL is ready!"

# Generate socialaccount fixture with environment variables
echo "Creating socialaccount fixture..."
cat > ./LearningAPI/fixtures/socialaccount.json << EOF
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

# Generate superuser fixture with environment variables
echo "Creating superuser fixture..."
export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"

DJANGO_GENERATED_PASSWORD=$(python3 ./djangopass.py "$LEARN_OPS_SUPERUSER_PASSWORD")

cat > ./LearningAPI/fixtures/superuser.json << EOF
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

# Run migrations
echo "Running database migrations..."
python3 manage.py migrate

# Load fixture data
echo "Loading fixture data..."
python3 manage.py flush --no-input
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
python3 manage.py loaddata superuser

# Clean up temporary fixture files
echo "Cleaning up temporary fixture files..."
rm -f ./LearningAPI/fixtures/socialaccount.json
rm -f ./LearningAPI/fixtures/superuser.json

echo "Database setup complete!"

# Start the Django development server
echo "Starting Django development server..."
python3 manage.py runserver 0.0.0.0:8000