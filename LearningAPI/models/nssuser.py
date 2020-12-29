from django.db import models
from django.conf import settings


def is_student(user):
    return user.groups.filter(name='Students').exists()


def is_instructor(user):
    return user.groups.filter(name='Instructors').exists()


class NssUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slack_handle = models.CharField(max_length=55, null=True, blank=True)
    github_handle = models.CharField(max_length=55, null=True, blank=True)
