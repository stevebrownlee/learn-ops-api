from django.db import models


class LightningExercise(models.Model):
    name = models.CharField(max_length=75)
    book = models.ForeignKey("CourseBook", on_delete=models.CASCADE)