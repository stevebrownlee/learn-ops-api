from django.http import HttpResponseServerError
from django.db.models import Q
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from LearningAPI.models import NssUser, OneOnOneNote, Cohort, NssUserCohort
from LearningAPI.views.learning_record_view import LearningRecordSerializer


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


class StudentViewSet(ViewSet):
    """Student view set"""

    permission_classes = (StudentPermission,)

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
        students = NssUser.objects.filter(user__is_staff=False)
        serializer = StudentSerializer(
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
            students = students.filter(cohorts__cohort=cohort_filter)

            if feedback is not None and feedback == 'true':
                serializer = NoCohortStudentSerializer(
                    students, many=True, context={'request': request})
            else:
                serializer = MiniStudentSerializer(
                    students, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

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


class StudentCohortsSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer's related Django user"""
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.cohort.name

    def get_id(self, obj):
        return obj.cohort.id

    class Meta:
        model = NssUserCohort
        fields = ['name', 'id']


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer for student notes"""

    class Meta:
        model = OneOnOneNote
        fields = ['id', 'notes', 'session_date', 'author']


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    cohorts = StudentCohortsSerializer(many=True)
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
                  'cohorts', 'feedback', 'records')


class NoCohortStudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    feedback = StudentNoteSerializer(many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'slack_handle', 'github_handle',
                  'feedback')


class MiniStudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = NssUser
        fields = ('id', 'name', 'email', 'slack_handle', 'github_handle',)
