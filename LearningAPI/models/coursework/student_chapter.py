from django.db import models


class StudentChapter(models.Model):
    """Model for tracking student progress through the courses"""
    student = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="chapters")
    chapter = models.ForeignKey("Chapter", on_delete=models.DO_NOTHING, related_name="students")
