import datetime
from django.db import models


class LearningRecordEntry(models.Model):
    """Model for tracking individual notes on learning objectives per student"""
    record = models.ForeignKey(
        "LearningRecord", on_delete=models.CASCADE, related_name="entries")
    note = models.TextField()
    recorded_on = models.DateField(
        null=False, blank=True, default=datetime.date.today, editable=False)
    instructor = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name='student_records')

    class Meta:
        ordering = ("-recorded_on",)