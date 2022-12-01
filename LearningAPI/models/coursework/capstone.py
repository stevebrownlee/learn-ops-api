from django.db import models


class Capstone(models.Model):
    """Capstone model"""
    student = models.ForeignKey("NssUser", on_delete=models.DO_NOTHING, related_name="capstones")
    course = models.ForeignKey("Course", on_delete=models.DO_NOTHING)
    proposal_url = models.CharField(max_length=256)
    repo_url = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.course.name

    @property
    def status_count(self):
        return self.__status_count

    @status_count.setter
    def status_count(self, value):
        self.__status_count = value