from django.db import models


class LearningObjective(models.Model):
    BLOOMS_TAXONOMY_LEVEL = (
        ('REM', 'Remember'),
        ('UND', 'Understand'),
        ('APP', 'Apply'),
        ('ANZ', 'Analyze'),
        ('EVL', 'Evaluate'),
        ('CRT', 'Create'),
    )
    swbat = models.CharField(max_length=255)
    bloom_level = models.CharField(max_length=3, choices=BLOOMS_TAXONOMY_LEVEL)
