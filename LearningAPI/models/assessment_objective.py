from django.db import models


class AssessmentObjective(models.Model):
    assessment = models.ForeignKey(
        "Assessment", on_delete=models.CASCADE, related_name="objectives")
    objective = models.ForeignKey(
        "LearningObjective", on_delete=models.CASCADE, related_name="assessments")
