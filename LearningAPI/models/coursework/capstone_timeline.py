from django.db import models


class CapstoneTimeline(models.Model):
    capstone = models.ForeignKey("Capstone", on_delete=models.DO_NOTHING, related_name="statuses")
    status = models.ForeignKey("ProposalStatus", on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now=True, auto_now_add=False)
