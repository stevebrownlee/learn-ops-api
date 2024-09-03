from django.db import models

class StudentTeam(models.Model):
    """ This class is used to create a student team for a cohort """
    group_name = models.CharField(max_length=55)
    cohort = models.ForeignKey("Cohort", on_delete=models.CASCADE)
    sprint_team = models.BooleanField(default=False)
    slack_channel = models.CharField(max_length=55, default="")
    students = models.ManyToManyField("NSSUser", through="NSSUserTeam")
