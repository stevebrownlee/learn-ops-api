from django.db import models


class Course(models.Model):
    """Model for NSS courses"""
    name = models.CharField(max_length=75)

    def __str__(self) -> str:
        return self.name
