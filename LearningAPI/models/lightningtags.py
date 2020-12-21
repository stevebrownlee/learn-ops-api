from django.db import models


class LightningTag(models.Model):
    exercise = models.ForeignKey(
        "LightningExercise", on_delete=models.CASCADE, related_name="lightningtags")
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="lightningtags")
