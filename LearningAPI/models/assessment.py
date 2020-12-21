from django.db import models


class Assessment(models.Model):
    is_qa = models.BooleanField()
    is_project = models.BooleanField()
    url = models.CharField(max_length=255)
