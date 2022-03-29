from django.http import HttpResponseServerError
from django.db.models import Count, Q
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import (
    DailyStatus, NssUser, OneOnOneNote,
    Cohort, LearningRecordEntry, LearningRecord,
    CoreSkillRecord
)
from LearningAPI.views.core_skill_record_view import CoreSkillRecordSerializer


class StudentPermission(permissions.BasePermission):
    """Permissions for student resource"""

    def has_permission(self, request, view):
        if view.action in ['list', 'destroy', 'status', 'feedback']:
            return request.auth.user.is_staff
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update']:
            return True
        else:
            return False


class StudentPagination(PageNumberPagination):
    """Pagination for student resource"""
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 80


class StudentViewSet(ModelViewSet):
    """Student view set"""

    permission_classes = (StudentPermission,)
    pagination_class = StudentPagination

    def create(self, request):
        """Handle POST operations"""
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            try:
                student = NssUser.objects.get(pk=pk)

            except ValueError as ex:
                student = NssUser.objects.get(slack_handle=pk)

            if request.auth.user == student.user or request.auth.user.is_staff:
                serializer = StudentSerializer(
                    student, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "You are not authorized to view this student profile."},
                    status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist as ex:
            return Response(
                {"message": "That student does not exist."},
                status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
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

        if student_status == "unassigned":
            students = NssUser.objects.\
                annotate(cohort_count=Count('assigned_cohorts')).\
                filter(user__is_staff=False, user__is_active=True, cohort_count=0)
        else:
            students = NssUser.objects.filter(user__is_active=True, user__is_staff=False)

        serializer = SingleStudent(
            students, many=True, context={'request': request})

        search_terms = self.request.query_params.get('q', None)
        if search_terms is not None:
            for letter in list(search_terms):
                students = students.filter(
                    Q(user__first_name__icontains=letter)
                    | Q(user__last_name__icontains=letter)
                )

            serializer = SingleStudent(
                students, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        cohort = self.request.query_params.get('cohort', None)
        feedback = self.request.query_params.get('feedback', None)

        if cohort is not None:
            cohort_filter = Cohort.objects.get(pk=cohort)
            students = students.filter(assigned_cohorts__cohort=cohort_filter)

            if feedback is not None and feedback == 'true':
                serializer = MicroStudents(
                    students, many=True, context={'request': request})
            else:
                serializer = MicroStudents(
                    students, many=True, context={'request': request})

        page = self.paginate_queryset(serializer.data)
        paginated_response = self.get_paginated_response(page)
        return paginated_response

    @action(methods=['post'], detail=True)
    def status(self, request, pk):
        """Add daily status from stand-up"""

        if request.method == "POST":
            try:
                daily_status = DailyStatus()
                daily_status.coach = NssUser.objects.get(user=request.auth.user)
                daily_status.student = NssUser.objects.get(pk=pk)
                daily_status.status = request.data["status"]

                daily_status.save()

                response = {
                    "id": daily_status.id,
                    "status": daily_status.status
                }

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response(response, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post'], detail=True)
    def feedback(self, request, pk):
        """Add feedback from 1:1 session"""

        if request.method == "POST":
            try:
                note = OneOnOneNote()
                note.coach = NssUser.objects.get(user=request.auth.user)
                note.student = NssUser.objects.get(pk=pk)
                note.notes = request.data["notes"]

                note.save()

            except NssUser.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response({'message': 'Student note created'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Unsupported HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def student_score(self, obj):
    """Return total learning score"""
    total = 0
    scores = LearningRecord.objects.\
        filter(student=obj, achieved=True).\
        order_by("-id")

    for score in scores:
        total += score.weight.weight

    return total


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = OneOnOneNote
        fields = ['id', 'notes', 'session_date', 'author']


class StudentStatusSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = DailyStatus
        fields = ['id', 'status', 'created_on', 'author']


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


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    statuses = StudentStatusSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    core_skill_records = serializers.SerializerMethodField()

    def get_score(self, obj):
        return student_score(self, obj)

    def get_records(self, obj):
        records = LearningRecord.objects.filter(student=obj).order_by("achieved")
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
                  'cohorts', 'feedback', 'records', 'statuses')


class MicroStudents(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return student_score(self, obj)

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'score')


class SingleStudent(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return student_score(self, obj)

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
                  'cohorts', 'feedback', 'repos', 'score',)
