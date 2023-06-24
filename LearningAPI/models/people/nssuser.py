"""NssUser database model"""
import statistics

from django.db import models
from django.conf import settings
from django.db.models import Sum, F, OuterRef, Subquery
from LearningAPI.models.coursework import (
    CapstoneTimeline, StudentProject, CohortCourse, Project
)


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
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def book(self):
        student_project = StudentProject.objects.filter(student=self).last()
        cohort = self.assigned_cohorts.order_by("-id").last()

        if student_project is None:
            cohort_course = CohortCourse.objects.get(
                cohort__id=cohort, index=0)
            project = Project.objects.get(
                book__course=cohort_course.course, book__index=0, index=0)

            return {
                "id": project.book.id,
                "name": project.book.name,
                "project": project.name,
                "index": project.book.index
            }

        return {
            "id": student_project.project.book.id,
            "name": student_project.project.book.name,
            "index": student_project.project.book.index,
            "project": student_project.project.name
        }

    @property
    def name(self):
        return str(self)

    @property
    def assessment_status(self):
        try:
            student_assessment = self.assessments.last()  # pylint: disable=E1101
            if student_assessment.assessment.book.id != self.book["id"]:
                return 0

            status = student_assessment.status.status
            if status == "In Progress":
                return 1
            if status == "Ready for Review":
                return 2
            if status == "Reviewed and Incomplete":
                return 3
            if status == "Reviewed and Complete":
                return 4

        except Exception as ex:
            return 0

    @property
    def proposals(self):
        try:
            lastest_status = CapstoneTimeline.objects.filter(capstone=OuterRef("pk")).order_by("-pk")

            proposals = self.capstones.annotate(
                course_name=F("course__name"),
                current_status_id=Subquery(lastest_status.values('status__id')[:1]),
                current_status=Subquery(lastest_status.values('status__status')[:1])
            ).values('id', 'current_status', 'course_name', 'proposal_url', 'current_status_id')

            return proposals
        except Exception:
            return []

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
        if assignment is None:
            return {
                "name": "Unassigned"
            }

        return {
            "name": assignment.cohort.name,
            "id": assignment.cohort.id,
            "client_course": assignment.cohort.info.client_course_url,
            "server_course": assignment.cohort.info.server_course_url,
            "zoom_url": assignment.cohort.info.zoom_url,
            "start": assignment.cohort.start_date,
            "end": assignment.cohort.end_date,
            "github_org": assignment.cohort.info.student_organization_url,
            "courses": assignment.cohort.courses.order_by('index').values('course__name', 'course__id', 'active'),
        }
