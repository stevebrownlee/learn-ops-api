"""NssUser database model"""
import statistics
import logging

from django.db import models
from django.conf import settings
from django.db.models import Sum


class NssUser(models.Model):
    """Model for NSS-specific user information beyond Django user"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # This field will hold the user's Slack Member Id
    slack_handle = models.CharField(max_length=55, null=True, blank=True)
    github_handle = models.CharField(max_length=55, null=True, blank=True)

    def __repr__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def score(self):
        """Return total learning score"""

        # First get the total of the student's technical objectives
        total = 0
        scores = self.learning_records.filter(achieved=True) \
            .annotate(total_score=Sum("weight__weight")) \
            .values_list('total_score', flat=True)
        total = sum(list(scores))

        # Get the average of the core skills' levels and adjust the
        # technical score positively by the percent

        core_skill_records = list(
            self.core_skills.values_list('level', flat=True))

        try:
            # Hannah and I did this on a Monday morning, so it may be the wrong
            # approach, but it's a step in the right direction
            mean = statistics.mean(core_skill_records)
            total = round(total * (1 + (mean / 10)))

        except statistics.StatisticsError:
            pass

        return total

    @property
    def assessment_overview(self):
        assessment_list = []
        for assessment in self.assessments.all().order_by("-assessment__book__index"):
            assessment_list.append({
                "id": assessment.id,
                "name": assessment.assessment.name,
                "status": assessment.status.status,
                "book": assessment.assessment.assigned_book,
                "reviewed_by": assessment.instructor.user.first_name,
                "github_url": assessment.url
            })
        return assessment_list

    @property
    def current_cohort(self):
        assignment = self.assigned_cohorts.order_by("-id").last()
        if assignment is None:
            return {
                "name": "Unassigned"
            }

        try:
            return {
                "name": assignment.cohort.name,
                "id": assignment.cohort.id,
                "client_course": assignment.cohort.info.client_course_url,
                "server_course": assignment.cohort.info.server_course_url,
                "zoom_url": assignment.cohort.info.zoom_url,
                "start": assignment.cohort.start_date,
                "end": assignment.cohort.end_date,
                "ic": assignment.cohort.slack_channel,
                "github_org": assignment.cohort.info.student_organization_url,
                "courses": assignment.cohort.courses.order_by('index').values('course__name', 'course__id', 'active'),
            }
        except Exception as ex:
            logger = logging.getLogger("LearningPlatform")
            logger.exception(getattr(ex, 'message', repr(ex)))

            return {
                "name": assignment.cohort.name,
                "id": assignment.cohort.id,
                "start": assignment.cohort.start_date,
                "end": assignment.cohort.end_date,
                "ic": assignment.cohort.slack_channel,
                "courses": assignment.cohort.courses.order_by('index').values('course__name', 'course__id', 'active'),
            }
