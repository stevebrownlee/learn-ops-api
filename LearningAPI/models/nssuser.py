from django.db import models
from django.contrib.auth.models import User


class NssUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slack_handle = models.CharField(max_length=55)
    github_handle = models.CharField(max_length=55)
    capstone_mentor = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, blank=True, null=True)
