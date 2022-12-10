"""Model for assessments used by instruction team"""
from django.db import models


class Assessment(models.Model):
    """Model for assessments used by instruction team"""
    ASSESSMENT_TYPES = (
        ("SELF", 'Self-assessment'),
        ("ASSIGNED", 'Assigned by instructor'),
    )
    name = models.CharField(max_length=255)
    source_url = models.CharField(max_length=512)
    book = models.ForeignKey("Book", on_delete=models.CASCADE, default=1)
    type = models.CharField(
        max_length=8,
        choices=ASSESSMENT_TYPES,
        default="SELF",
    )

    def __str__(self):
        return self.name
