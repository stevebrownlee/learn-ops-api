from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=55)
    implementation_url = models.CharField(max_length=256)
