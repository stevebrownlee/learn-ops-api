"""Model for help requests"""
from django.db import models

class HelpRequest(models.Model):
    """Model for help requests"""
    student = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    question = models.TextField()
    status = models.CharField(max_length=20, default='invalid')
    created_at = models.DateTimeField(auto_now_add=True)
