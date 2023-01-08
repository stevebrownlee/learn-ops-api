"""Student view module"""
import os
import statistics
import logging

import requests
from django.db.models import Count, Q, Case, When
from django.db.models.fields import IntegerField
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from LearningAPI.decorators import is_instructor
from LearningAPI.models import Tag
from LearningAPI.models.coursework import Capstone, StudentProject, Book, Project
from LearningAPI.models.people import (Cohort, StudentNote, NssUser, StudentAssessment,
                                       OneOnOneNote, StudentPersonality, Assessment,
                                       StudentAssessmentStatus, StudentTag)
from LearningAPI.models.skill import (CoreSkillRecord, LearningRecord,
                                      LearningRecordEntry)
from .personality import myers_briggs_persona


class StudentPagination(PageNumberPagination):
    """Pagination for student resource"""
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 80


class StudentViewSet(ModelViewSet):
    """Student viewset"""

    pagination_class = StudentPagination

    def create(self, request):
        """Handle POST operations"""
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        logger = logging.getLogger("LearningPlatform")

        try:
            try:
                student = NssUser.objects.get(pk=pk)

            except ValueError:
                student = NssUser.objects.get(slack_handle=pk)

            try:
                personality = StudentPersonality.objects.get(student=student)
            except StudentPersonality.DoesNotExist:
                personality = StudentPersonality()
                personality.briggs_myers_type = ""
                personality.bfi_extraversion = 0
                personality.bfi_agreeableness = 0
                personality.bfi_conscientiousness = 0
                personality.bfi_neuroticism = 0
                personality.bfi_openness = 0
                personality.student = student
                personality.save()
            except Exception as ex:
                logger.exception(getattr(ex, 'message', repr(ex)))

            if request.auth.user == student.user or request.auth.user.is_staff:
                serializer = StudentSerializer(
                    student, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "You are not authorized to view this student profile."},
                    status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist:
            return Response(
                {"message": "That student does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            logger.exception(getattr(ex, 'message', repr(ex)))
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            student = NssUser.objects.get(pk=pk)

            if request.auth.user == student.user or request.auth.user.is_staff:
                if "slack_handle" in request.data:
                    student.slack_handle = request.data["slack_handle"]
                if "gitub_handle" in request.data:
                    student.gitub_handle = request.data["gitub_handle"]

                student.save()

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

    @method_decorator(is_instructor())
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single student

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            student = NssUser.objects.get(pk=pk)
            student.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except NssUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all students

        Returns:
            Response -- JSON serialized array
        """
        student_status = self.request.query_params.get('status', None)
        cohort = self.request.query_params.get('cohort', None)
        search_terms = self.request.query_params.get('q', None)

        if student_status == "unassigned":
            students = NssUser.objects.\
                annotate(cohort_count=Count('assigned_cohorts')).\
                filter(user__is_staff=False,
                       user__is_active=True, cohort_count=0)
        else:
            students = NssUser.objects.filter(
                user__is_active=True, user__is_staff=False)

        serializer = SingleStudent(students, many=True)

        if search_terms is not None:
            for letter in list(search_terms):
                students = students.filter(
                    Q(user__first_name__icontains=letter)
                    | Q(user__last_name__icontains=letter)
                )

            serializer = SingleStudent(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if cohort is not None:
            cohort_filter = Cohort.objects.get(pk=cohort)
            students = students.filter(assigned_cohorts__cohort=cohort_filter)

            for student in students:
                try:
                    personality = StudentPersonality.objects.get(student=student)

                except StudentPersonality.DoesNotExist:
                    personality = StudentPersonality()
                    personality.briggs_myers_type = ""
                    personality.bfi_extraversion = 0
                    personality.bfi_agreeableness = 0
                    personality.bfi_conscientiousness = 0
                    personality.bfi_neuroticism = 0
                    personality.bfi_openness = 0
                    personality.student = student
                    personality.save()

            serializer = MicroStudents(students, many=True)

        page = self.paginate_queryset(serializer.data)
        paginated_response = self.get_paginated_response(page)
        return paginated_response

    @method_decorator(is_instructor())
    @action(methods=['post', 'put'], detail=True)
    def assess(self, request, pk):
        """POST when a student starts working on book assessment. PUT to change status."""

        if request.method == "PUT":
            student = NssUser.objects.get(pk=pk)
            assessment_status = StudentAssessmentStatus.objects.get(
                pk=request.data['statusId'])
            latest_assessment = StudentAssessment.objects.filter(
                student=student).last()

            if latest_assessment is not None:
                latest_assessment.status = assessment_status
                latest_assessment.save()

                try:
                    if latest_assessment.status.status == 'Reviewed and Complete':
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                        channel_payload = {
                            "text": request.data.get(
                                "text",
                                f':fox-yay-woo-hoo: Self-Assessment Review Complete\n\n\n:white_check_mark: Your coaching team just marked {latest_assessment.assessment.name} as completed.\n\nVisit https://learning.nss.team to view your messages.'),
                            "token": os.getenv("SLACK_BOT_TOKEN"),
                            "channel": latest_assessment.student.slack_handle
                        }

                        requests.post(
                            "https://slack.com/api/chat.postMessage",
                            data=channel_payload,
                            headers=headers
                        )
                except Exception:
                    return Response({'message': 'Updated, but no Slack message sent'}, status=status.HTTP_204_NO_CONTENT)

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'Students has no assessments assigned'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "POST":
            try:
                try:
                    assessment = Assessment.objects.get(book__id=int(request.data['bookId']))
                except Assessment.DoesNotExist:
                    return Response({'message': 'There is no assessment for this book.'}, status=status.HTTP_404_NOT_FOUND)


                student_assessment = StudentAssessment()
                student_assessment.student = NssUser.objects.get(user__id=pk)
                student_assessment.instructor = NssUser.objects.get(
                    user=request.auth.user)
                student_assessment.status = StudentAssessmentStatus.objects.get(
                    status="In Progress")
                student_assessment.assessment = assessment
                student_assessment.save()
            except Exception as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=True)
    def project(self, request, pk):
        """Add to the list of projects being worked on by student"""

        if request.method == "POST":
            try:
                student_project = StudentProject()
                student_project.student = NssUser.objects.get(pk=pk)
                student_project.project = Project.objects.get(
                    pk=int(request.data['projectId']))
                student_project.save()
            except Exception as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=False)
    def teams(self, request):
        """Add/remove student tag for teams"""

        if request.method == "POST":
            combos = request.data.get('combos', None)

            for combo in combos:
                student = NssUser.objects.get(pk=combo['student'])

                try:
                    tag = Tag.objects.get(name=combo['team'])
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(name=combo['team'])


                assignment = StudentTag.objects.create( student = student, tag = tag )

            return Response(None, status=status.HTTP_201_CREATED)

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=True)
    def note(self, request, pk):
        """Add note for student"""

        if request.method == "POST":
            try:
                instructor_note = StudentNote()
                instructor_note.coach = NssUser.objects.get(
                    user=request.auth.user)
                instructor_note.student = NssUser.objects.get(pk=pk)
                instructor_note.status = request.data["note"]
                instructor_note.save()

                response = {
                    "id": instructor_note.id,
                    "status": instructor_note.status
                }

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response(response, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @method_decorator(is_instructor())
    @action(methods=['post'], detail=True)
    def feedback(self, request, pk):
        """Add feedback from 1:1 session"""

        if request.method == "POST":
            try:
                student = NssUser.objects.get(pk=pk)
                note = OneOnOneNote()
                note.coach = NssUser.objects.get(user=request.auth.user)
                note.student = student
                note.notes = request.data["notes"]
                note.save()

                # Send message to student
                try:
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    channel_payload = {
                        "text": request.data.get("text", "You just received feedback from one of your coaches.\n\nVisit https://learning.nss.team to view your messages."),
                        "token": os.getenv("SLACK_BOT_TOKEN"),
                        "channel": student.slack_handle
                    }

                    requests.post(
                        "https://slack.com/api/chat.postMessage",
                        data=channel_payload,
                        headers=headers
                    )
                except Exception:
                    pass

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response({'message': 'Student note created'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def student_score(obj):
    """Return total learning score"""

    # First get the total of the student's technical objectives
    total = 0
    scores = LearningRecord.objects.\
        filter(student=obj, achieved=True).\
        order_by("-id")

    for score in scores:
        total += score.weight.weight

    # Get the average of the core skills' levels and adjust the
    # technical score positively by the percent
    core_skill_records = CoreSkillRecord.objects.filter(
        student=obj).order_by("pk")
    scores = [record.level for record in core_skill_records]

    try:
        # Hannah and I did this on a Monday morning, so it may be the wrong
        # approach, but it's a step in the right direction
        mean = statistics.mean(scores)
        total = round(total * (1 + (mean / 10)))

    except statistics.StatisticsError:
        pass

    return total


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = OneOnOneNote
        fields = ['id', 'notes', 'session_date', 'author']


class InstructorNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = StudentNote
        fields = ['id', 'note', 'created_on', 'author']


class LearningRecordEntrySerializer(serializers.ModelSerializer):
    """JSON serializer"""
    instructor = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        return f'{obj.instructor.user.first_name} {obj.instructor.user.last_name}'

    class Meta:
        model = LearningRecordEntry
        fields = ('id', 'note', 'recorded_on', 'instructor')


class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    entries = LearningRecordEntrySerializer(many=True)
    objective = serializers.SerializerMethodField()

    def get_objective(self, obj):
        return obj.weight.label

    class Meta:
        model = LearningRecord
        fields = ('id', 'objective', 'achieved', 'entries', )


class PersonalitySerializer(serializers.ModelSerializer):
    """Serializer for a student's personality info"""
    briggs_myers_type = serializers.SerializerMethodField()

    def get_briggs_myers_type(self, obj):
        if obj.briggs_myers_type != "":
            return {
                "code": obj.briggs_myers_type,
                "description": myers_briggs_persona(obj.briggs_myers_type)
            }
        else:
            return {}

    class Meta:
        model = StudentPersonality
        fields = (
            'briggs_myers_type', 'bfi_extraversion',
            'bfi_agreeableness', 'bfi_conscientiousness',
            'bfi_neuroticism', 'bfi_openness',
        )


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    notes = InstructorNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    core_skill_records = serializers.SerializerMethodField()
    personality = PersonalitySerializer(many=False)

    def get_score(self, obj):
        return student_score(obj)

    def get_records(self, obj):
        records = LearningRecord.objects.filter(
            student=obj).order_by("achieved")
        return LearningRecordSerializer(records, many=True).data

    def get_core_skill_records(self, obj):
        records = CoreSkillRecord.objects.filter(student=obj).order_by("pk")
        return CoreSkillRecordSerializer(records, many=True).data

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github', 'score', 'core_skill_records',
                  'cohorts', 'feedback', 'records', 'notes', 'personality',
                  'capstones', 'current_cohort' )


class StudentTagSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = StudentTag
        fields = ('id', 'tag',)
        depth = 1


class CoreSkillRecordSerializer(serializers.ModelSerializer):
    """Serializer for Core Skill Record"""

    class Meta:
        model = CoreSkillRecord
        fields = ('id', 'skill', 'level', )
        depth = 1


class MicroStudents(serializers.ModelSerializer):
    """JSON serializer"""
    tags = StudentTagSerializer(many=True)
    name = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    proposals = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()
    assessment_status = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_assessment_status(self, obj):
        student_project = StudentProject.objects.filter(student=obj).last()

        if student_project is not None:
            book = student_project.project.book

            # Not assigned book assessment yet
            assessment_status = 0

            try:
                student_assessment = StudentAssessment.objects.annotate(assessment_status=Case(
                        When(status__status="In Progress", then=1),
                        When(status__status="Ready for Review", then=2),
                        When(status__status="Reviewed and Complete", then=3),
                        default=0,
                        output_field=IntegerField()
                    ))\
                    .get(assessment__book=book, student=obj)

                assessment_status = student_assessment.assessment_status
            except StudentAssessment.DoesNotExist:
                assessment_status = 0

            return assessment_status
        else:
            return 0

    def get_book(self, obj):
        student_project = StudentProject.objects.filter(student=obj).last()

        if student_project is None:
            book = Book.objects.get(
                course__name__icontains="JavaScript", index=0)
            return {
                "id": book.id,
                "name": book.name,
                "project": ""
            }

        return {
            "id": student_project.project.book.id,
            "name": student_project.project.book.name,
            "project": student_project.project.name
        }

    def get_proposals(self, obj):
        # Three stages - "submitted", "reviewed", "approved"
        proposals = Capstone.objects.filter(student=obj).annotate(
            status_count=Count("statuses"),
            approved=Count(
                'statuses',
                filter=Q(statuses__status__status="Approved")
            ),
            mvp=Count(
                'statuses',
                filter=Q(statuses__status__status="MVP")
            )
        ).order_by("pk")

        proposal_statuses = []

        for proposal in proposals:
            proposal_status = ""

            if proposal.status_count == 0:
                proposal_status = "submitted"
            elif proposal.status_count > 0 and proposal.mvp == 1:
                proposal_status = "mvp"
            elif proposal.status_count > 0 and proposal.approved == 0:
                proposal_status = "reviewed"
            elif proposal.status_count > 0 and proposal.approved == 1:
                proposal_status = "approved"

            proposal_statuses.append({
                "id": proposal.id,
                "status": proposal_status
            })

        return proposal_statuses

    def get_score(self, obj):
        return student_score(obj)

    def get_archetype(self, obj):
        if obj.personality.briggs_myers_type != '':
            return myers_briggs_persona(obj.personality.briggs_myers_type)["type"]

        return ""

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'score', 'tags',
                  'proposals', 'book',
                  'assessment_status',
                  'github', 'cohorts',
                  'archetype',)


class SingleStudent(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    def get_date_joined(self, obj):
        return obj.user.date_joined

    def get_score(self, obj):
        return student_score(obj)

    def get_staff(self, obj):
        return False

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_repos(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["repos_url"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github', 'staff', 'slack_handle',
                  'cohorts', 'feedback', 'repos', 'score', 'date_joined',
                  'current_cohort')
