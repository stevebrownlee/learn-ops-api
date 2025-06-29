from django.db import models

class CohortEventType(models.Model):
    """Storing event types for cohort events, such as graduation or special announcements."""
    description = models.CharField(max_length=255, help_text="Name of the event")
    color = models.CharField(max_length=7, default="#ffffff", help_text="Color associated with the event type in hex format")
