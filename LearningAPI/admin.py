from django.contrib import admin

# Register your models here.
from .models.people import NssUser, Assessment, Cohort, NssUserCohort
from .models.coursework import Course, ProposalStatus, Capstone, CapstoneTimeline, StudentChapter

from .models.skill import (
    CoreSkill, CoreSkillRecord,
    LearningRecordEntry, LearningRecord, LearningWeight,
)

@admin.register(StudentChapter)
class StudentChapterAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('student', 'chapter',)

@admin.register(CapstoneTimeline)
class CapstoneTimelineAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('capstone', 'status', 'student')

@admin.register(NssUserCohort)
class NssUserCohortAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('nss_user', 'cohort',)

@admin.register(Capstone)
class CapstoneAdmin(admin.ModelAdmin):
    """For managing capstone proposals"""
    list_display = ('student', 'course', 'proposal_url',)


@admin.register(ProposalStatus)
class ProposalStatusAdmin(admin.ModelAdmin):
    """For managing capstone proposals statuses"""
    list_display = ('status',)

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    """For managing cohort information"""
    list_display = ('name', 'slack_channel', 'start_date', 'end_date',)

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Assessment skills"""
    list_display = ('name', 'source_url', 'type',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course skills"""
    list_display = ('name',)

@admin.register(CoreSkill)
class CoreSkillAdmin(admin.ModelAdmin):
    """Core skills"""
    list_display = ('label',)

@admin.register(CoreSkillRecord)
class CoreSkillRecordAdmin(admin.ModelAdmin):
    """Core skill records"""
    list_display = ('student', 'skill', 'level',)

@admin.register(LearningWeight)
class LearningWeightAdmin(admin.ModelAdmin):
    """Learning weights"""
    list_display = ('label', 'weight',)

@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    """Learning records"""
    list_display = ('student', 'weight',)

@admin.register(LearningRecordEntry)
class LearningRecordEntryAdmin(admin.ModelAdmin):
    """Learning record entries"""
    list_display = ('record', 'instructor', 'note',)

@admin.register(NssUser)
class NssUserAdmin(admin.ModelAdmin):
    """Users"""
    list_display = ('user', 'slack_handle', 'github_handle',)
