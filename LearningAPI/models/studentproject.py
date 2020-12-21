from django.db import models


class StudentProject(models.Model):
    nss_user = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="studentprojects")
    project = models.ForeignKey("Project", on_delete=models.DO_NOTHING, related_name="studentprojects")
    github_url = models.CharField(max_length=256)