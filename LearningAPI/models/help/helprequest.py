""" This module contains the HelpRequest model for the Help app. """
from django.db import models
from django.utils import timezone

class HelpRequest(models.Model):
    """
    HelpRequest model
    """
    author = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='help_requests')
    category = models.ForeignKey('HelpCategory', on_delete=models.PROTECT, related_name='help_requests')
    title = models.CharField(max_length=255)
    content = models.TextField()
    github_url = models.URLField()
    exception_message = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)
    loom_url = models.URLField(blank=True, null=True)
    llm_prompt = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title