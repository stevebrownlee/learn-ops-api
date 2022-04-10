"""Module for daily status model"""
from django.db import models
from . import NssUser

class DailyStatus(models.Model):
    """Model for notes to send to students"""
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="statuses")
    coach = models.ForeignKey(NssUser, on_delete=models.CASCADE)

    status = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

    @property
    def author(self):
        return f'{self.coach.user.first_name} {self.coach.user.last_name}'

    class Meta:
        ordering = ['-created_on']