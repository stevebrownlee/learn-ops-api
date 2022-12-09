"""NssUser database model"""
from django.db import models
from django.conf import settings

class NssUser(models.Model):
    """Model for NSS-specific user information beyond Django user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # This field will hold the user's Slack Member Id
    slack_handle = models.CharField(max_length=55, null=True, blank=True)
    github_handle = models.CharField(max_length=55, null=True, blank=True)

    def __repr__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def cohorts(self):
        assignments = self.assigned_cohorts.all().order_by("-id")
        cohort_list = []
        for assignment in assignments:
            cohort_list.append({
                "id": assignment.cohort.id,
                "name": assignment.cohort.name,
                "start_date": assignment.cohort.start_date,
                "end_date": assignment.cohort.end_date,
            })
        return cohort_list
