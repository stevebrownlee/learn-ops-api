from django.db import models


class ObjectiveTag(models.Model):
    objective = models.ForeignKey(
        "LearningObjective", on_delete=models.CASCADE, related_name="objectivetags")
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="objectivetags")
