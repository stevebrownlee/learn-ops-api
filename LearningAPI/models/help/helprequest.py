# LearningAPI/models/help_request.py
from django.db import models

class HelpRequest(models.Model):
    student = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    question = models.TextField()
    status = models.CharField(max_length=20, default='invalid')
    created_at = models.DateTimeField(auto_now_add=True)

