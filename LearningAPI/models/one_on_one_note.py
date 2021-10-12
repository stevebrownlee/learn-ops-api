from django.db import models


class OneOnOneNote(models.Model):
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="feedback")
    coach = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="coach_notes")

    notes = models.TextField()
    session_date = models.DateField(auto_now=True)

    @property
    def author(self):
        return f'{self.coach.user.first_name} {self.coach.user.last_name}'
