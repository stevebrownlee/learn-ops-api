from django.db import models


class LightningExercise(models.Model):
    name = models.CharField(max_length=75)
    description = models.TextField()
