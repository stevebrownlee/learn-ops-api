from django.db import models


class ProjectTag(models.Model):
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="projecttags")
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="projecttags")
