"""Module for daily status model"""
from django.db import models
from . import NssUser

class StudentNote(models.Model):
    """Model for notes to send to students"""
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="notes")
    coach = models.ForeignKey(NssUser, on_delete=models.CASCADE)
    note_type = models.ForeignKey(
        "StudentNoteType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    note = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

    @property
    def author(self):
        return f'{self.coach.user.first_name} {self.coach.user.last_name}'

    class Meta:
        ordering = ['-created_on']