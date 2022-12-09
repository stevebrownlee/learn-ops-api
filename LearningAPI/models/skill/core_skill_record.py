import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from . import CoreSkill
from ..people import NssUser


class CoreSkillRecord(models.Model):
    """Model for tracking learning objectives per student"""
    student = models.ForeignKey(
        NssUser, on_delete=models.CASCADE, related_name='core_skills')
    skill = models.ForeignKey(CoreSkill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_on = models.DateField(null=False, blank=True, default=datetime.date.today, editable=False)
