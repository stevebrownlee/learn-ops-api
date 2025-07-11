#!/bin/bash

source .env

function configureDatabase() {
    brew install postgresql@16
    brew services start postgresql@16

    # Create your user database first
    createdb

    echo "Database $LEARN_OPS_DB does not exist"

    psql -d postgres -c "DROP DATABASE IF EXISTS $LEARN_OPS_DB WITH (FORCE);"
    psql -d postgres -c "CREATE DATABASE $LEARN_OPS_DB;"
    psql -d postgres -c "CREATE USER $LEARN_OPS_USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
    psql -d postgres -c "ALTER ROLE $LEARN_OPS_USER SET client_encoding TO 'utf8';"
    psql -d postgres -c "ALTER ROLE $LEARN_OPS_USER SET default_transaction_isolation TO 'read committed';"
    psql -d postgres -c "ALTER ROLE $LEARN_OPS_USER SET timezone TO 'UTC';"
    psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $LEARN_OPS_DB TO $LEARN_OPS_USER;"

    # Grant schema privileges
    psql -d postgres -c "GRANT ALL ON SCHEMA public TO $LEARN_OPS_USER;"
    psql -d "$LEARN_OPS_DB" -c "GRANT ALL ON SCHEMA public TO $LEARN_OPS_USER;"
    psql -d "$LEARN_OPS_DB" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $LEARN_OPS_USER;"
    psql -d "$LEARN_OPS_DB" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $LEARN_OPS_USER;"
    psql -d "$LEARN_OPS_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $LEARN_OPS_USER;"
    psql -d "$LEARN_OPS_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $LEARN_OPS_USER;"
}

function generateSocialFixture() {
    echo '[
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
                "client_id": "'"$LEARN_OPS_CLIENT_ID"'",
                "secret": "'"$LEARN_OPS_SECRET_KEY"'",
                "key": "",
                "sites": [
                    1
                ]
            }
        }
    ]
    ' >./LearningAPI/fixtures/socialaccount.json
}

function generateSuperuserFixture() {
    export DJANGO_SETTINGS_MODULE="LearningPlatform.settings"
    hashedPassword=$(python3 ./djangopass.py "$LEARN_OPS_SUPERUSER_PASSWORD" >&1)

    echo '[
    {
        "model": "auth.user",
        "pk": null,
        "fields": {
            "password": "'"$hashedPassword"'",
            "last_login": null,
            "is_superuser": true,
            "username": "'"$LEARN_OPS_SUPERUSER_NAME"'",
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
]' >./LearningAPI/fixtures/superuser.json
}

function initializeProject() {
    pipenv --python 3.11.11

    # Install project requirements
    pipenv install

    # Run existing migrations
    pipenv run migrate

    # Load data from backup
    pipenv run bash -c "python3 manage.py flush --no-input \
        && python3 manage.py loaddata socialaccount \
        && python3 manage.py loaddata complete_backup \
        && python3 manage.py loaddata superuser"

    rm ./LearningAPI/fixtures/superuser.json
    rm ./LearningAPI/fixtures/socialaccount.json
}

configureDatabase
generateSocialFixture
generateSuperuserFixture
initializeProject
