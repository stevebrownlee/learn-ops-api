from django.db import models


class Project(models.Model):
    """Course projects"""
    name = models.CharField(max_length=55)
    implementation_url = models.CharField(max_length=256)
    book = models.ForeignKey(
        "Book", on_delete=models.CASCADE, related_name="child_projects")
    index = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    is_group_project = models.BooleanField(default=False)

    @property
    def course(self):
        return self.book.course.id

    def __str__(self) -> str:
        return self.name
