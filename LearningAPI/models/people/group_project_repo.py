from django.db import models
from django.core.exceptions import ValidationError

class GroupProjectRepository(models.Model):
    """ This class stores the repository URLs for a group project """
    team = models.ForeignKey("StudentTeam", on_delete=models.CASCADE, related_name="repositories")
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    repository = models.CharField(max_length=255, default="")

    def clean(self):
        super().clean()
        if not self.project.is_group_project and self.project_id.isdigit():
            raise ValidationError({
                'project': 'Integer IDs are only allowed for projects with is_group_project set to True.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

