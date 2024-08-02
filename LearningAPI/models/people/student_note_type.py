"""Module for student note types"""
from django.db import models

class StudentNoteType(models.Model):
    """ Model for note types """
    label = models.CharField(max_length=32)