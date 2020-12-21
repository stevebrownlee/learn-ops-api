from django.db import models


class StudentProject(models.Model):
    student = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="projects")
    project = models.ForeignKey("Project", on_delete=models.DO_NOTHING, related_name="students")
    github_url = models.CharField(max_length=256)
