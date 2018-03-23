from django.db import models


class Exercise(models.Model):
    name = models.CharField(max_length=55)