from django.db import models


class LearningWeight(models.Model):
    label = models.CharField(max_length=55)
    weight = models.IntegerField()
