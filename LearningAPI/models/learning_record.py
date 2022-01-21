from django.db import models
from django.db.models.fields import DateField
import datetime


"""Model for instructor records per student task"""


class LearningRecord(models.Model):
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name='records')
    weight = models.ForeignKey(
        "LearningWeight", on_delete=models.CASCADE, related_name="records")
    achieved = models.BooleanField(default=False)
    created_on = models.DateField(null=False, blank=True, default=datetime.date.today, editable=False)


    def __str__(self) -> str:
        return f'{self.student.user.first_name} {self.student.user.last_name} {self.description}'
