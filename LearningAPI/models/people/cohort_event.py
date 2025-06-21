from django.db import models

class CohortEvent(models.Model):
    """Any important event related to a cohort, such as a graduation or a special announcement."""
    cohort = models.ForeignKey("Cohort", on_delete=models.CASCADE, related_name="events", help_text="The cohort this event is associated with")
    event_name = models.CharField(max_length=255, help_text="Name of the event")
    event_type = models.ForeignKey("CohortEventType", on_delete=models.DO_NOTHING, null=False, blank=False, help_text="Type of the event (e.g., graduation, announcement)")
    event_datetime = models.DateTimeField(help_text="Date and time of the event")
    description = models.TextField(blank=True, help_text="Description of the event")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the event was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the event was last updated")
