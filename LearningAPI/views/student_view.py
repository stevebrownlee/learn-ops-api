from django.http import HttpResponseServerError
from django.db.models import Q
from django.db.models import Count
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from LearningAPI.models import NssUser, OneOnOneNote, Cohort, NssUserCohort, LearningRecord
from LearningAPI.views.learning_record_view import RecordWeightSerializer
from django.forms.models import model_to_dict
from rest_framework.pagination import PageNumberPagination


class StudentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'destroy', 'status']:
            return request.auth.user.is_staff
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update']:
            return True
        else:
            return False

class StudentPagination(PageNumberPagination):
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
                student.slack_handle = request.data["slack_handle"]
                student.gitub_handle = request.data["gitub_handle"]

                student.save()

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist as ex:
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
                filter(user__is_staff=False, cohort_count=0)
        else:
            students = NssUser.objects.filter(user__is_staff=False)

        serializer = MiniStudentSerializer(
            students, many=True, context={'request': request})



        search_terms = self.request.query_params.get('q', None)
        if search_terms != None:
            for letter in list(search_terms):
                students = students.filter(
                    Q(user__first_name__icontains=letter)
                    | Q(user__last_name__icontains=letter)
                )

            serializer = MiniStudentSerializer(
                students, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        cohort = self.request.query_params.get('cohort', None)
        feedback = self.request.query_params.get('feedback', None)

        if cohort is not None:
            cohort_filter = Cohort.objects.get(pk=cohort)
            students = students.filter(assigned_cohorts__cohort=cohort_filter)

            if feedback is not None and feedback == 'true':
                serializer = NoCohortStudentSerializer(
                    students, many=True, context={'request': request})
            else:
                serializer = NoCohortStudentSerializer(
                    students, many=True, context={'request': request})

        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    @action(methods=['post'], detail=True)
    def status(self, request, pk):
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


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = OneOnOneNote
        fields = ['id', 'notes', 'session_date', 'author']

class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    weights = RecordWeightSerializer(many=True)

    class Meta:
        model = LearningRecord
        fields = ('description', 'obtained_from', 'weights', 'created_on', 'id', )

class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()

    def get_records(self, obj):
        records = LearningRecord.objects.filter(student=obj).order_by("-id")
        return LearningRecordSerializer(records, many=True).data

    def get_github(self, obj):
        github = obj.user.socialaccount_set.get(user=obj.user)
        return github.extra_data["login"]

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'github',
                  'cohorts', 'feedback', 'records')


class NoCohortStudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    records = LearningRecordSerializer(many=True)

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'slack_handle', 'github_handle',
                  'feedback', 'records')


class MiniStudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    repos = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

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
        fields = ('id', 'name', 'email', 'github', 'staff',
                  'cohorts', 'feedback', 'repos')
