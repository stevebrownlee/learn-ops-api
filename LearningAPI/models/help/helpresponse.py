from django.db import models
from django.utils import timezone

class HelpRequestResponse(models.Model):
    help_request = models.ForeignKey('HelpRequest', on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='help_request_responses')
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # pylint: disable=no-member
        return f"Response to {self.help_request.title} by {self.author.username}"

    class Meta:
        ordering = ['-created_at']