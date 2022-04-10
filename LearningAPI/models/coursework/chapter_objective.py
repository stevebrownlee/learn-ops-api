from django.db import models


class ChapterObjective(models.Model):
    chapter = models.ForeignKey(
        "Chapter", on_delete=models.CASCADE, related_name="objectives")
    objective = models.ForeignKey(
        "LearningObjective", on_delete=models.CASCADE, related_name="chapters")
