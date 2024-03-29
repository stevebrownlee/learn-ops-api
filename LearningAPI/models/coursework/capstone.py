from django.db import models


class Capstone(models.Model):
    """Capstone model"""
    student = models.ForeignKey("NssUser",
                                on_delete=models.DO_NOTHING,
                                related_name="capstones")
    course = models.ForeignKey("Course", on_delete=models.DO_NOTHING)
    proposal_url = models.CharField(max_length=256)
    repo_url = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField()

    def __str__(self) -> str:
        return f'{self.student}: {self.course.name}'

    @property
    def current_status(self):
        return self.statuses.order_by('-date').first()
