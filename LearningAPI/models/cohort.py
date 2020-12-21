from django.db import models


class Cohort(models.Model):
    name = models.CharField(max_length=55)
    slack_channel = models.CharField(max_length=55)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    break_start_date = models.DateField(auto_now=False, auto_now_add=False)
    break_end_date = models.DateField(auto_now=False, auto_now_add=False)
