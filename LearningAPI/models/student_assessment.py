"""Model for student assessments"""
from django.db import models
from . import NssUser, Assessment


class StudentAssessment(models.Model):
    """Model for assessments assigned to a student"""
    student = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING, related_name='assessments')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    instructor = models.ForeignKey(NssUser, null=True, on_delete=models.SET_NULL, related_name='assignments')
    url = models.CharField(max_length=512, default="")

    class Meta:
       unique_together = (('student', 'assessment',),)