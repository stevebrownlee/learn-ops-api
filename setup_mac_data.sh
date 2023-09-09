#!/bin/bash

function configureDatabase() {
    brew install postgresql

    echo "Database $LEARN_OPS_DB does not exist"

    psql -c "DROP DATABASE IF EXISTS $LEARN_OPS_DB WITH (FORCE);"
    psql -c "CREATE DATABASE $LEARN_OPS_DB;"
    psql -c "CREATE USER $LEARN_OPS_USER WITH PASSWORD '$LEARN_OPS_PASSWORD';"
    psql -c "ALTER ROLE $LEARN_OPS_USER SET client_encoding TO 'utf8';"
    psql -c "ALTER ROLE $LEARN_OPS_USER SET default_transaction_isolation TO 'read committed';"
    psql -c "ALTER ROLE $LEARN_OPS_USER SET timezone TO 'UTC';"
    psql -c "GRANT ALL PRIVILEGES ON DATABASE $LEARN_OPS_USER TO $LEARN_OPS_DB;"
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
