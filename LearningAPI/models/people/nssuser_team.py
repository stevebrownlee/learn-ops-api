from django.db import models

class NSSUserTeam(models.Model):
    """ This class is used to store the relationship between a student and a team """
    team = models.ForeignKey("StudentTeam", on_delete=models.CASCADE)
    student = models.ForeignKey("NSSUser", on_delete=models.CASCADE)

