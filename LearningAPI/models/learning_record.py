from django.db import models
from django.db.models.fields import DateField
import datetime


"""Model for instructor records per student task"""


class LearningRecord(models.Model):
    RECORD_SOURCE = (
        ("ONEON", 'Student 1 on 1'),
        ("SCORE", 'Assessment score'),
        ("CLASS", 'Github Classroom'),
    )

    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name='records')
    description = models.CharField(max_length=55)
    obtained_from = models.CharField(
        max_length=5,
        choices=RECORD_SOURCE,
        default="ONEON",
    )
    created_on = models.DateField(null=False, blank=True, default=datetime.date.today, editable=False)


    def __str__(self) -> str:
        return f'{self.student.user.first_name} {self.student.user.last_name} {self.description}'
