from django.db import models


class LearningObjective(models.Model):
    swbat = models.CharField(max_length=255)
    bloom_level = models.ForeignKey("TaxonomyLevel", on_delete=models.CASCADE, related_name="objectives")
