from django.db import models


class NssUserCohort(models.Model):
    """Model for assigning users to cohorts"""
    nss_user = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="assigned_cohorts")
    cohort = models.ForeignKey("Cohort", on_delete=models.DO_NOTHING, related_name="members")
    is_github_org_member = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.cohort.name

    def __repr__(self) -> str:
        return self.cohort.name

    class Meta:
        unique_together = ("nss_user", "cohort")