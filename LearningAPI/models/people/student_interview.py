from django.db import models


class StudentInterview(models.Model):
    student = models.ForeignKey("NssUser", on_delete=models.CASCADE, related_name="interviewers")
    instructor = models.ForeignKey("NssUser", on_delete=models.CASCADE, related_name="interviews")
    date_completed = models.DateField(auto_now_add=True)