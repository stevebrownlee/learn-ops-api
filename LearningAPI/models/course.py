from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=75)

    @property
    def chapters(self):
        return self.__chapters

    @chapters.setter
    def chapters(self, value):
        self.__chapters = value