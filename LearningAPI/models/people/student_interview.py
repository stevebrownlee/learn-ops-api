from django.db import models


class StudentInterview(models.Model):
    """Data model for storing when an instructor completes a student interview"""
    student = models.ForeignKey("NssUser", on_delete=models.CASCADE, related_name="interviewers")
    instructor = models.ForeignKey("NssUser", on_delete=models.CASCADE, related_name="interviews")
    date_completed = models.DateField(auto_now_add=True)