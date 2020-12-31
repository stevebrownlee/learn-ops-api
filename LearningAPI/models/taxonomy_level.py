from django.db import models


class TaxonomyLevel(models.Model):
    level_name = models.CharField(max_length=20)
