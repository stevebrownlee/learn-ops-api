from django.db import models


class TreehouseBadge(models.Model):
    name = models.CharField(max_length=55)
    technology = models.CharField(max_length=55)