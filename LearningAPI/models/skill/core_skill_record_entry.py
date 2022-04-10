import datetime
from django.db import models
from . import CoreSkillRecord


class CoreSkillRecordEntry(models.Model):
    """Model for tracking individual notes on core skills per student"""
    record = models.ForeignKey(
        CoreSkillRecord, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    recorded_on = models.DateField(
        null=False, blank=True, default=datetime.date.today, editable=False)
    instructor = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name='student_skills')
