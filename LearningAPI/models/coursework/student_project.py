from django.db import models


class StudentProject(models.Model):
    """Model for tracking student progress through the courses"""
    student = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="projects")
    project = models.ForeignKey("Project", on_delete=models.DO_NOTHING, related_name="students")
    date_created = models.DateField(auto_now=True, auto_now_add=False)
