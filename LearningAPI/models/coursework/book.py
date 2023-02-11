from django.db import models


class Book(models.Model):
    """Model for books in the courses"""
    name = models.CharField(max_length=75)
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="books")
    description = models.TextField(default='')
    index = models.IntegerField(default=0)

    @property
    def projects(self):
        return self.child_projects.all().order_by("index")

    @property
    def has_assessment(self):
        return self.assessments.count() > 0

    def __str__(self) -> str:
        return self.name
