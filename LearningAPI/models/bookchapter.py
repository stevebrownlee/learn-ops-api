from django.db import models


class BookChapter(models.Model):
    name = models.CharField(max_length=75)
    book = models.ForeignKey("CourseBook", on_delete=models.CASCADE, related_name="chapters")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="chapters")
