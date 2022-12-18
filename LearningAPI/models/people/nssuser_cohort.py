from django.db import models


class NssUserCohort(models.Model):
    """Model for assigning users to cohorts"""
    nss_user = models.ForeignKey(
        "NssUser", on_delete=models.DO_NOTHING, related_name="assigned_cohorts")
    cohort = models.ForeignKey(
        "Cohort", on_delete=models.DO_NOTHING, related_name="members")

    # TODO: Add an active property to determine which cohort student is currently in

    def __str__(self) -> str:
        return self.cohort.name

    def __repr__(self) -> str:
        return self.cohort.name
