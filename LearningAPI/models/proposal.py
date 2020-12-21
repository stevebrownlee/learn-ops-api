from django.db import models


class Proposal(models.Model):
    nss_user = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING)
    proposal_status = models.ForeignKey("ProposalStatus", on_delete=models.DO_NOTHING)
    description = models.TextField()
    course = models.ForeignKey("Course", on_delete=models.DO_NOTHING)
