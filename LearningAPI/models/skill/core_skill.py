from django.db import models


class CoreSkill(models.Model):
    """Model for Core Skill for NSS"""
    label = models.CharField(max_length=55)

    def __str__(self):
        return self.label