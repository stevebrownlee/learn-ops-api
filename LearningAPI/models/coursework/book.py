from django.db import models


class Book(models.Model):
    """Model for books in the courses"""
    name = models.CharField(max_length=75)
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="books")
    index = models.IntegerField(default=0)

    @property
    def has_assessment(self):
        return self.assessments.count() > 0

    def __str__(self) -> str:
        return self.name


