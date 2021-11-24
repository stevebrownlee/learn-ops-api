from django.db import models


class LearningRecord(models.Model):
    RECORD_SOURCE = (
        ("ONEON", 'Student 1 on 1'),
        ("SCORE", 'Assessment score'),
        ("CLASS", 'Github Classroom'),
    )

    student = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    description = models.CharField(max_length=55)
    obtained_from = models.CharField(
        max_length=5,
        choices=RECORD_SOURCE,
        default="ONEON",
    )
