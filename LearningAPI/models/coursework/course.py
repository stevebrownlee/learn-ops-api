from django.db import models


class Course(models.Model):
    """Model for NSS courses"""
    name = models.CharField(max_length=75)
    date_created = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self) -> str:
        return self.name
