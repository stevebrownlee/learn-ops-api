from django.db import models


class StudentMentor(models.Model):
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="mentors")
    mentor = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="students")
    capstone = models.ForeignKey("Capstone", on_delete=models.CASCADE)
