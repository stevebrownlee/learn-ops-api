from django.db import models


class FoundationsLearnerProfile(models.Model):
    """Model for tracking learner progress in Foundations Course"""
    learner_github_id = models.CharField(max_length=50)
    learner_name = models.CharField(max_length=75)
    cohort_type = models.CharField(max_length=15, default="day")
    cohort_number = models.IntegerField(default=0)

