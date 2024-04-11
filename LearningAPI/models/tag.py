from django.db import models


class Tag(models.Model):
    """Model for any tag in the system"""
    name = models.CharField(max_length=25)

    def __str__(self) -> str:
        return self.name
