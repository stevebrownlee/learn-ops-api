python manage.py dumpdata auth.user --indent 4 > authusers.json
python manage.py dumpdata LearningAPI.NSSUser --indent 4 > nssusers.json
python manage.py dumpdata socialaccount.socialaccount --indent 4 > social.json
python manage.py dumpdata LearningAPI.LearningRecord --indent 4 > records.json
python manage.py dumpdata LearningAPI.LearningRecordEntry --indent 4 > entries.json