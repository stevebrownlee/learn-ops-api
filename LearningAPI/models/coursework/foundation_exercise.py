from django.db import models


class FoundationsExercise(models.Model):
    """Model for tracking learner progress in Foundations Course"""
    learner_github_id = models.CharField(max_length=50)
    learner_name = models.CharField(max_length=75)
    title = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    attempts = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)
    first_attempt = models.DateTimeField(null=True, blank=True)
    last_attempt = models.DateTimeField(null=True, blank=True)
    completed_code = models.TextField(null=True, blank=True)
    used_solution = models.BooleanField(default=False)

    def __str__(self) -> str: # pylint: disable=E0307
        return f'{self.learner_github_id} - {self.title} - {self.attempts} - {self.complete}'
