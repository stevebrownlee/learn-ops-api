from django.db import models


class Course(models.Model):
    """Model for NSS courses"""
    name = models.CharField(max_length=75)

    def __str__(self) -> str:
        return self.name

    @property
    def chapters(self):
        try:
            return self.__chapters
        except AttributeError:
            return 0

    @chapters.setter
    def chapters(self, value):
        self.__chapters = value