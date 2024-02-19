from django.contrib import admin

# Register your models here.
from .models.people import (
    NssUser, Assessment,
    Cohort, NssUserCohort,
    StudentAssessmentStatus,
    StudentAssessment, CohortInfo
)
from .models.coursework import (
    Course, ProposalStatus, Capstone, Book,
    CapstoneTimeline, StudentProject, Project,
    CohortCourse
)

from .models.skill import (
    CoreSkill, CoreSkillRecord,
    LearningRecordEntry, LearningRecord, LearningWeight,
)

@admin.register(CohortInfo)
class CohortInfoAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('cohort', )

@admin.register(CohortCourse)
class CohortCourseAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('cohort', 'course', 'active', )

@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('student', 'assessment', 'status', )
    search_fields = ["student__user__last_name"]
    search_help_text = "Search by last name"

@admin.register(StudentAssessmentStatus)
class StudentAssessmentStatusAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('status', )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('name', 'implementation_url', 'book' )

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('name', 'course',)

@admin.register(StudentProject)
class StudentProjectAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('student', 'project',)
    search_fields = ["student__user__last_name"]
    search_help_text = "Search by last name"

@admin.register(CapstoneTimeline)
class CapstoneTimelineAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('capstone', 'status', 'student')
    search_fields = ["capstone__student__user__last_name"]
    search_help_text = "Search by last name"


@admin.register(NssUserCohort)
class NssUserCohortAdmin(admin.ModelAdmin):
    """For assigning students to cohorts"""
    list_display = ('nss_user', 'cohort',)
    search_fields = ["nss_user__user__last_name"]
    search_help_text = "Search by last name"

@admin.register(Capstone)
class CapstoneAdmin(admin.ModelAdmin):
    """For managing capstone proposals"""
    list_display = ('student', 'course', 'proposal_url',)
    search_fields = ["student__user__last_name"]
    search_help_text = "Search by last name"


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
    search_fields = ["student__user__last_name"]

@admin.register(LearningRecordEntry)
class LearningRecordEntryAdmin(admin.ModelAdmin):
    """Learning record entries"""
    list_display = ('record', 'instructor', 'note',)
    search_fields = ["record__student__user__last_name"]

@admin.register(NssUser)
class NssUserAdmin(admin.ModelAdmin):
    """Users"""
    list_display = ('full_name', 'slack_handle',)
    ordering = ('-pk',)
    search_fields = ["user__last_name"]
    search_help_text = "Search by last name"
