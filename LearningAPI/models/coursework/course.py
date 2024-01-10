from django.db import models


class Course(models.Model):
    """Model for NSS courses"""
    name = models.CharField(max_length=75)
    date_created = models.DateField(auto_now=True, auto_now_add=False)
    active = models.BooleanField(default=True)

    def __str__(self) -> str: # pylint: disable=E0307
        return self.name
