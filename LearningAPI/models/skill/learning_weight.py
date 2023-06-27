from django.db import models


class LearningWeight(models.Model):
    """Model for learning objectives for NSS"""
    label = models.CharField(max_length=127)  # Name of the learning objective (e.g. Functions)
    weight = models.IntegerField()  # Numerical weight (or score) for achieving objective
    tier = models.IntegerField(default=1)  # Allows for objectives to be grouped/ordered

    def __str__(self) -> str:
        return f'{self.label} ({self.weight})'
