from django.db import models

class CohortInfo(models.Model):
    """Additional, non-critical information for a cohort."""
    cohort = models.OneToOneField("Cohort", on_delete=models.CASCADE, related_name="info")
    student_organization_url = models.CharField(max_length=75, unique=True, null=True, blank=True)
    github_classroom_url = models.CharField(max_length=75, unique=True, null=True, blank=True)
    attendance_sheet_url = models.CharField(max_length=255, unique=True, null=True, blank=True)
