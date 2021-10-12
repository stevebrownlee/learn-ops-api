from django.db import models


class Assessment(models.Model):
    name = models.CharField(max_length=55)
    is_qa = models.BooleanField()  # Q&A assessment (e.g. Google forms)
    is_project = models.BooleanField() # Coding project assessment
    url = models.CharField(max_length=255)
