from django.db import models


class ProposalStatus(models.Model):
    status = models.CharField(max_length=55)