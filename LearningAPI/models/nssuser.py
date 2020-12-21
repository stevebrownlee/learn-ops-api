from django.db import models
from django.conf import settings


class NssUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slack_handle = models.CharField(max_length=55, null=True, blank=True)
    github_handle = models.CharField(max_length=55, null=True, blank=True)
