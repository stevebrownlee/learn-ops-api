from django.db import models
from . import NssUser, ProposalStatus, CapstoneType


class Proposal(models.Model):
    nss_user = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING)
    proposal_status = models.ForeignKey(ProposalStatus, on_delete=models.DO_NOTHING)
    capstone_type = models.ForeignKey(CapstoneType, on_delete=models.DO_NOTHING)
    description = models.TextField()