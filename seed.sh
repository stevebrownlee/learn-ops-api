#!/bin/bash

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
' > ./LearningAPI/fixtures/socialaccount.json

# Run existing migrations
python3 manage.py migrate

# Load data from backup
python3 manage.py loaddata socialaccount
python3 manage.py loaddata complete_backup
