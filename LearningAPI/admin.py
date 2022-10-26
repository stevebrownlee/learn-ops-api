from django.contrib import admin

from .models.people import NssUser
from .models.coursework import Course
from .models.skill import (CoreSkill, CoreSkillRecord, LearningRecord,
                           LearningRecordEntry, LearningWeight)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Core skills"""
    list_display = ['name',]

@admin.register(CoreSkill)
class CoreSkillAdmin(admin.ModelAdmin):
    """Core skills"""
    list_display = ['label',]

@admin.register(CoreSkillRecord)
class CoreSkillRecordAdmin(admin.ModelAdmin):
    """Core skill records"""
    list_display = ('student', 'skill', 'level',)

@admin.register(LearningWeight)
class LearningWeightAdmin(admin.ModelAdmin):
    """Learning weights"""
    list_display = ['label', 'weight',]

@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    """Learning records"""
    list_display = ['student', 'weight',]

@admin.register(LearningRecordEntry)
class LearningRecordEntryAdmin(admin.ModelAdmin):
    """Learning record entries"""
    list_display = ['record', 'instructor', 'note']

@admin.register(NssUser)
class NssUserAdmin(admin.ModelAdmin):
    """Users"""
    list_display = ['user', 'slack_handle', 'github_handle']
