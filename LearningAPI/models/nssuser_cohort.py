from django.db import models
from . import NssUser, Cohort


class NssUserCohort(models.Model):
    nss_user = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING)
    cohort = models.ForeignKey(Cohort, on_delete=models.DO_NOTHING)