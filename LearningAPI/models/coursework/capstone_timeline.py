from django.db import models


class CapstoneTimeline(models.Model):
    """Model for recording history of capstone proposal"""
    capstone = models.ForeignKey("Capstone", on_delete=models.DO_NOTHING, related_name="statuses")
    status = models.ForeignKey("ProposalStatus", on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now=True, auto_now_add=False)

    @property
    def student(self):
        return f'{self.capstone.student.user.first_name} {self.capstone.student.user.last_name}' # pylint: disable=E1101
