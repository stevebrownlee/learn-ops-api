import datetime
from django.db import models
from . import LearningWeight
from ..people import Assessment


class AssessmentWeight(models.Model):
    """Model for relationship between an assessment and its objectives"""
    weight = models.ForeignKey(LearningWeight, on_delete=models.CASCADE, related_name='assessment_assignments')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='weight_assignments')
