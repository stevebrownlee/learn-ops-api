"""Student view module"""
import os
import json
import logging
import requests
from django.contrib.auth.models import User
from django.db import connection
from django.db import IntegrityError
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from LearningAPI.utils import GithubRequest, SlackAPI
from LearningAPI.decorators import is_instructor
from LearningAPI.models import Tag
from LearningAPI.models.coursework import StudentProject, Project, Capstone, CapstoneTimeline
from LearningAPI.models.people import (StudentNote, NssUser, StudentAssessment,
                                       OneOnOneNote, StudentPersonality, Assessment,
                                       StudentAssessmentStatus, StudentTag, StudentInterview)
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

            if request.auth.user == student.user or request.auth.user.is_staff:
                serializer = StudentSerializer(student, context={'request': request})
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
            # Check if there is a "soft" query string parameter
            soft_delete = request.query_params.get('soft', None)

            student = NssUser.objects.get(pk=pk)
            django_user = User.objects.get(pk=student.user.id)

            # Delete all personality records
            StudentPersonality.objects.filter(student=student).delete()

            # Delete all student assessments
            StudentAssessment.objects.filter(student=student).delete()

            # Delete all student projects
            StudentProject.objects.filter(student=student).delete()

            # Delete all student tags
            StudentTag.objects.filter(student=student).delete()

            # Delete all learning records
            LearningRecordEntry.objects.filter(record__student=student).delete()
            LearningRecord.objects.filter(student=student).delete()

            # Delete all core skill records
            CoreSkillRecord.objects.filter(student=student).delete()

            # Delete all CapstoneTimeline related to student
            CapstoneTimeline.objects.filter(capstone__student=student).delete()

            # Delete all capstones
            Capstone.objects.filter(student=student).delete()

            # Delete student cohorts
            student.assigned_cohorts.all().delete()

            if soft_delete is None:
                # Delete all student notes
                StudentNote.objects.filter(student=student).delete()

                # Delete the student
                student.delete()
                django_user.delete()

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
        cohort = self.request.query_params.get('cohort', None)
        lastname = self.request.query_params.get('lastname_like', None)

        if lastname is not None:
            # Get students by last name and are not assigned to a cohort

            students = NssUser.objects.filter(user__last_name__icontains=lastname, assigned_cohorts=None)
            return Response([{ 'name': student.full_name, 'id': student.id} for student in students], status=status.HTTP_200_OK)

        if cohort is None:
            return Response({
                'message': 'Student lists can only be requested by cohort'
            }, status=status.HTTP_400_BAD_REQUEST)

        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        user_id AS id,
                        github_handle,
                        extra_data,
                        student_name AS name,
                        current_cohort AS cohort_name,
                        current_cohort_id AS cohort_id,
                        assessment_status_id,
                        assessment_url,
                        current_project_id AS project_id,
                        current_project_index AS project_index,
                        current_project_name AS project_name,
                        current_book_id AS book_id,
                        current_book_index AS book_index,
                        current_book_name AS book_name,
                        score,
                        student_notes,
                        student_tags,
                        capstone_proposals,
                        project_duration
                    FROM
                        get_cohort_student_data(%s)
                """, [cohort])
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()

                logger = logging.getLogger("LearningPlatform")
                logger.debug("Number of student records retrieved for cohort %s is %s", cohort, len(results))

                students = []
                for row in results:
                    student = dict(zip(columns, row))
                    student['current_cohort'] = {
                        'id': student['cohort_id'],
                        'name': student['cohort_name']
                    }
                    student['tags'] = json.loads(student['student_tags'])
                    student['avatar'] = json.loads(student['extra_data'])["avatar_url"]
                    student['notes'] = json.loads(student['student_notes'])
                    student['proposals'] = json.loads(student['capstone_proposals'])
                    students.append(student)

                serializer = CohortStudentSerializer(data=students, many=True)

                if serializer.is_valid():
                    logger.debug("Serializer for students by cohort succeeded")
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    logger.debug("Serializer for students by cohort failed")
                    logger.debug(serializer.errors)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                    # return Response({'message': serializer.error_messages}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post', 'put'], detail=True)
    def assess(self, request, pk):
        """POST when a student starts working on book assessment. PUT to change status."""

        slack = SlackAPI()
        logger = logging.getLogger("LearningPlatform")

        if request.method == "PUT":
            student = NssUser.objects.get(pk=pk)
            assessment_status = StudentAssessmentStatus.objects.get(pk=request.data['statusId'])
            latest_assessment = StudentAssessment.objects.filter(student=student).last()

            if latest_assessment is not None:
                latest_assessment.status = assessment_status
                latest_assessment.save()

                try:
                    if latest_assessment.status.status == 'Ready for Review':
                        slack.send_message(
                            text="🎉 Congratulations! You've completed your self-assessment. Your coaching team will review your work and provide feedback soon.",
                            channel=student.slack_handle
                        )

                        slack.send_message(
                            text=f'{student.full_name} in {student.current_cohort["name"]} has completed their self-assessment for {latest_assessment.assessment.name}.\n\nReview it at {latest_assessment.url}',
                            channel=student.current_cohort["ic"]
                        )

                    if latest_assessment.status.status == 'Reviewed and Complete':
                        slack.send_message(
                            text=f':fox-yay-woo-hoo: Self-Assessment Review Complete\n\n\n:white_check_mark: Your coaching team just marked {latest_assessment.assessment.name} as completed.\n\nVisit https://learning.nss.team to view your latest messages and statuses.',
                            channel=latest_assessment.student.slack_handle
                        )

                        # Assign all objectives/weights to the student as complete
                        assessment_objectives = latest_assessment.assessment.objectives.all()
                        for objective in assessment_objectives:
                            try:
                                achieved_record = LearningRecord.objects.create(
                                    student=student,
                                    weight=objective,
                                    achieved=True,
                                )
                                LearningRecordEntry.objects.create(
                                    record=achieved_record,
                                    note=request.data.get("instructorNotes", ""),
                                    instructor=NssUser.objects.get(user=request.auth.user)
                                )
                            except IntegrityError as ex:
                                logger.exception(getattr(ex, 'message', repr(ex)))

                except Exception:
                    return Response({'message': 'Updated, but no Slack message sent'}, status=status.HTTP_204_NO_CONTENT)

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'Students has no assessments assigned'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "POST":
            try:
                try:
                    student = NssUser.objects.get(pk=pk)
                    assessment = Assessment.objects.get(book__id=int(request.data['bookId']))

                except Assessment.DoesNotExist:
                    return Response({'message': 'There is no assessment for this book.'}, status=status.HTTP_404_NOT_FOUND)

                try:
                    existing_assessment = StudentAssessment.objects.get(student=student, assessment=assessment)
                    assessment_uri = request.build_absolute_uri(f'/assessments/{existing_assessment.id}')

                    return Response(
                        { 'message': f'Conflict: {student.full_name} is already assigned to the {assessment.name} assessment' },
                        status=status.HTTP_409_CONFLICT,
                        headers={'Location': assessment_uri}
                    )
                except StudentAssessment.DoesNotExist:
                    pass

                # Create the student assessment record
                student_assessment = StudentAssessment()
                student_assessment.student = student
                student_assessment.instructor = NssUser.objects.get(user=request.auth.user)
                student_assessment.status = StudentAssessmentStatus.objects.get(status="In Progress")
                student_assessment.assessment = assessment
                student_assessment.save()

                gh_request = GithubRequest()
                full_url = assessment.source_url

                # Split the full URL on '/' and get the last two items
                ( org, repo, ) = full_url.split('/')[-2:]

                # Construct request body for creating the repository
                student_org_name = student.current_cohort["github_org"].split("/")[-1]

                # Replace all spaces in the assessment name with hyphens
                hyphenated_assessment_name = assessment.name.replace(" ", "-")
                repo_name = f"{hyphenated_assessment_name}-{student.github_handle}"

                request_body = {
                    "owner": student_org_name,
                    "name": repo_name,
                    "description": f"This is your self-assessment repository for the {assessment.book.name} book",
                    "include_all_branches": False,
                    "private": False
                }

                # Create the repository
                logger.debug("Generating repository for student assessment")
                response = gh_request.post(url=f'https://api.github.com/repos/{org}/{repo}/generate',data=request_body)
                logger.debug(response.json())

                # Assign the student write permissions to the repository
                logger.debug("Adding student as a collaborator to the repository")
                request_body = { "permission":"write" }
                response = gh_request.put(
                    url=f'https://api.github.com/repos/{student_org_name}/{repo_name}/collaborators/{student.github_handle}',
                    data=request_body
                )

                if response.status_code != 204:
                    logger.debug("Error: Student was not added as a collaborator to the assessment repository")
                    return Response(
                        {
                            'message': 'Error: Student was not added as a collaborator to the assessment repository.'
                        },
                        status=status.HTTP_502_BAD_GATEWAY
                    )

                # Send message to student
                created_repo_url = f'https://github.com/{student_org_name}/{repo_name}'
                slack.send_message(
                    text=f"🐙 Your self-assessment repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                    channel=student.slack_handle
                )

                # Send message to instructors
                slack_channel = student.assigned_cohorts.order_by("-id").first().cohort.slack_channel
                slack.send_message(
                    text=f"📝 {student.full_name} has started the self-assessment for {assessment.name}.",
                    channel=slack_channel
                )

                # Update the student assessment record with the Github repo URL
                student_assessment.url = created_repo_url
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
                student_project.project = Project.objects.get(pk=int(request.data['projectId']))
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

                StudentTag.objects.create(student=student, tag=tag)

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
                        headers=headers,
                        timeout=1000
                    )
                except Exception:
                    pass

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response({'message': 'Student note created'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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


class CoreSkillRecordSerializer(serializers.ModelSerializer):
    """Serializer for Core Skill Record"""

    class Meta:
        model = CoreSkillRecord
        fields = ('id', 'skill', 'level', )
        depth = 1


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


class CohortStudentSerializer(serializers.Serializer):
    """JSON serializer"""
    id = serializers.IntegerField()
    github_handle = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    current_cohort = serializers.DictField()
    avatar = serializers.CharField(allow_blank=True, allow_null=True)
    assessment_status_id = serializers.IntegerField(allow_null=True)
    assessment_url = serializers.CharField(max_length=256, allow_blank=True, allow_null=True)
    project_id = serializers.IntegerField(allow_null=True)
    project_duration = serializers.IntegerField(allow_null=True)
    project_index = serializers.IntegerField(allow_null=True)
    project_name = serializers.CharField(max_length=100)
    book_id = serializers.IntegerField(allow_null=True)
    book_index = serializers.IntegerField(allow_null=True)
    book_name = serializers.CharField(max_length=100)
    score = serializers.IntegerField(allow_null=True)
    notes = serializers.ListField(allow_empty=True, required=False)
    proposals = serializers.ListField(allow_empty=True, required=False)
    tags = serializers.ListField(allow_empty=True, required=False)
    interview_count = serializers.SerializerMethodField()

    def get_interview_count(self, obj):
        return StudentInterview.objects.filter(student_id = obj['id']).count()

    def get_avatar(self, obj):
        try:
            github = obj.user.socialaccount_set.get(user=obj['id'])
            return github.extra_data["avatar_url"]
        except Exception:
            return ""


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    notes = InstructorNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    core_skill_records = serializers.SerializerMethodField()

    def get_project(self, obj):
        project = StudentProject.objects.filter(student=obj).last()
        if project is not None:
            return {
                "id": project.project.id,
                "name": project.project.name
            }
        else:
            return {
                "id": 0,
                "name": "Unassigned"
            }

    def get_records(self, obj):
        records = LearningRecord.objects.filter(
            student=obj).order_by("achieved")
        return LearningRecordSerializer(records, many=True).data

    def get_core_skill_records(self, obj):
        records = CoreSkillRecord.objects.filter(student=obj).order_by("pk")
        return CoreSkillRecordSerializer(records, many=True).data

    def get_name(self, obj):
        return obj.full_name

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = (
            'id', 'name', 'project', 'email', 'github_handle', 'score',
            'core_skill_records', 'feedback', 'records', 'notes', 'capstones',
            'current_cohort'
        )
