from django.db import models
from . import NssUser, Exercise


class NssUserExercise(models.Model):
    nss_user = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING)
    exercise = models.ForeignKey(Exercise, on_delete=models.DO_NOTHING)