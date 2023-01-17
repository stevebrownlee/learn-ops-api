from django.db import models

class CohortGithubProject(models.Model):
    """Links for the cohort created in Github Classroom"""
    cohort = models.ForeignKey("Cohort", on_delete=models.CASCADE)
    project_name = models.CharField(max_length=75, unique=True)
    assessment = models.BooleanField(default=True)
    project_url = models.CharField(max_length=255, unique=True)
