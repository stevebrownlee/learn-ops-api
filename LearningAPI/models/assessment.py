from django.db import models


class Assessment(models.Model):
    name = models.CharField(max_length=55)
    is_qa = models.BooleanField()
    is_project = models.BooleanField()
    url = models.CharField(max_length=255)
