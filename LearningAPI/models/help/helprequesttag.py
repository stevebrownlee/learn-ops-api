from django.db import models

class HelpRequestTag(models.Model):
    help_request = models.ForeignKey('HelpRequest', on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey('HelpTag', on_delete=models.CASCADE, related_name='help_requests')

    class Meta:
        unique_together = ['help_request', 'tag']

    def __str__(self):
        # pylint: disable=no-member
        return f"{self.help_request.title} - {self.tag.name}"