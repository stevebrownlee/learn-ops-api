from django.db import models


class StudentTag(models.Model):
    """Model relating students to tags"""
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="tags")
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="students")
