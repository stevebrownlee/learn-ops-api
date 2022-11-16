"""Student personality profile database model"""
from django.db import models


class StudentPersonality(models.Model):
    """Model for students to enter in their personality profile data"""
    student = models.OneToOneField("NSSUser", on_delete=models.CASCADE, related_name='personality')
    briggs_myers_type = models.CharField(max_length=6, null=True, blank=True)
    bfi_extraversion = models.IntegerField()
    bfi_agreeableness = models.IntegerField()
    bfi_conscientiousness = models.IntegerField()
    bfi_neuroticism = models.IntegerField()
    bfi_openness = models.IntegerField()
