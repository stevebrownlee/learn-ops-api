from django.contrib import admin

# Register your models here.
from .models import (
    NssUser,
    LearningRecordWeight,
    LearningRecord,
    LearningWeight
)


@admin.register(LearningWeight)
class LearningWeightAdmin(admin.ModelAdmin):
    list_display = ['label', 'weight',]

@admin.register(LearningRecord)
class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'description', 'obtained_from']

@admin.register(LearningRecordWeight)
class LearningRecordWeightAdmin(admin.ModelAdmin):
    list_display = ['record', 'weight', 'note']

@admin.register(NssUser)
class NssUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'slack_handle', 'github_handle']
