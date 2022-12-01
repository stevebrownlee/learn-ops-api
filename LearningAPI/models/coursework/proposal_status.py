from django.db import models


class ProposalStatus(models.Model):
    """Model for different statuses for capstone proposals"""
    status = models.CharField(max_length=55)
