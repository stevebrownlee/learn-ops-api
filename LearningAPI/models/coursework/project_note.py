from django.db import models
from django.db.models.fields import TextField


class ProjectNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    note = models.TextField()
