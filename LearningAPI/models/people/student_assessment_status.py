"""Model for assessment statuses"""
from django.db import models


class StudentAssessmentStatus(models.Model):
    """Model for assessment statuses"""
    status = models.CharField(max_length=512)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = "Book Assessment Status"
        verbose_name_plural = "Book Assessment Statuses"