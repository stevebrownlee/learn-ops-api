"""NssUser database model"""
from django.db import models
from django.conf import settings


class NssUser(models.Model):
    """Model for NSS-specific user information beyond Django user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # This field will hold the user's Slack Member Id
    slack_handle = models.CharField(max_length=55, null=True, blank=True)
    github_handle = models.CharField(max_length=55, null=True, blank=True)

    def __repr__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def assessment_overview(self):
        assessment_list = []
        for assessment in self.assessments.all().order_by("-id"):
            assessment_list.append({
                "id": assessment.id,
                "name": assessment.assessment.name,
                "status": assessment.status.status,
                "book": assessment.assessment.assigned_book,
                "reviewed_by": assessment.instructor.user.first_name
            })
        return assessment_list

    @property
    def cohorts(self):
        assignments = self.assigned_cohorts.all().order_by("-id").first()
        cohort_list = []
        for assignment in assignments:
            cohort_list.append({
                "id": assignment.cohort.id,
                "name": assignment.cohort.name,
                "start_date": assignment.cohort.start_date,
                "end_date": assignment.cohort.end_date,
            })
        return cohort_list

    @property
    def current_cohort(self):
        assignment = self.assigned_cohorts.order_by("-id").last()
        return {
            "name": assignment.cohort.name,
            "id": assignment.cohort.id,
            "client_course": assignment.cohort.info.client_course_url,
            "server_course": assignment.cohort.info.server_course_url,
            "start": assignment.cohort.start_date,
            "end": assignment.cohort.end_date,
            "github_org": assignment.cohort.info.student_organization_url,
            "courses": assignment.cohort.courses.order_by('index').values('course__name', 'course__id'),
        }
