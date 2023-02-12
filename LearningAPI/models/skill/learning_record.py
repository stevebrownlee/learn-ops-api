import datetime
from django.db import models
from . import LearningWeight
from ..people import NssUser


class LearningRecord(models.Model):
    """Model for tracking learning objectives per student"""
    student = models.ForeignKey(NssUser, on_delete=models.CASCADE, related_name='learning_records')
    weight = models.ForeignKey(LearningWeight, on_delete=models.CASCADE, related_name='records')
    achieved = models.BooleanField(default=False)
    created_on = models.DateField(null=False, blank=True, default=datetime.date.today, editable=False)

    def __str__(self) -> str:
        return f'{self.student.user.first_name} {self.student.user.last_name} {self.weight.weight}' # type: ignore
