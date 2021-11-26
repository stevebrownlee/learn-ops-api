from django.utils import timezone
from django.db import models


class LearningRecordWeight(models.Model):
    record = models.ForeignKey(
        "LearningRecord", on_delete=models.CASCADE, related_name="weights")
    weight = models.ForeignKey(
        "LearningWeight", on_delete=models.CASCADE, related_name="records")
    note = models.TextField()
    recorded_on = models.DateField(
        null=False, blank=True, default=timezone.now, editable=False)
    instructor = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name='student_records')
