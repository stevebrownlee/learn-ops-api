"""NssUser database model"""
from django.db import models
from django.conf import settings
from django.db.models import Count, Q
from LearningAPI.models.coursework import Capstone, StudentProject, CohortCourse, Project


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
    def github(self):
        return self.__github

    @github.setter
    def github(self, value):
        self.__github = value

    @property
    def bookxx(self):
        student_project = StudentProject.objects.filter(student=self).last()

        if student_project is None:
            cohort_course = CohortCourse.objects.get(cohort__id=self.cohorts[0]['id'], index=0)
            project = Project.objects.get(book__course=cohort_course.course, book__index=0, index=0)

            return {
                "id": project.book.id,
                "name": project.book.name,
                "project": project.name
            }

        return {
            "id": student_project.project.book.id,
            "name": student_project.project.book.name,
            "project": student_project.project.name
        }

    @property
    def name(self):
        return str(self)

    @property
    def submitted_proposals(self):
        proposals = Capstone.objects.filter(student=self).annotate(
            status_count=Count("statuses"),
            approved=Count(
                'statuses',
                filter=Q(statuses__status__status="Approved")
            ),
            mvp=Count(
                'statuses',
                filter=Q(statuses__status__status="MVP")
            ),
            changes=Count(
                'statuses',
                filter=Q(statuses__status__status="Requires Changes")
            )
        ).values('status_count', 'approved', 'mvp', 'changes')

        return proposals

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
    def current_cohort(self):
        assignment = self.assigned_cohorts.order_by("-id").last()
        return {
            "name": assignment.cohort.name,
            "id": assignment.cohort.id,
            "client_course": assignment.cohort.info.client_course_url,
            "server_course": assignment.cohort.info.server_course_url,
            "zoom_url": assignment.cohort.info.zoom_url,
            "start": assignment.cohort.start_date,
            "end": assignment.cohort.end_date,
            "github_org": assignment.cohort.info.student_organization_url,
            "courses": assignment.cohort.courses.order_by('index').values('course__name', 'course__id'),
        }
