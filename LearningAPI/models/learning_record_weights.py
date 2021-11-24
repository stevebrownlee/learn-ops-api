from django.db import models


class LearningRecordWeights(models.Model):
    record = models.ForeignKey(
        "LearningRecord", on_delete=models.CASCADE, related_name="weights")
    weight = models.ForeignKey(
        "LearningWeight", on_delete=models.CASCADE, related_name="records")
