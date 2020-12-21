from django.db import models


class CourseBook(models.Model):
    name = models.CharField(max_length=75)
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="books")
