from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Cohort, NssUser, CohortInfo


class CohortInfoViewSet(ViewSet):
    """Cohort info view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        cohort = request.data.get('cohort', None)
        attendance = request.data.get('attendance_sheet_url', None)
        classroom = request.data.get('github_classroom_url', None)
        github_org = request.data.get('student_organization_url', None)

        if attendance is None or classroom is None or github_org is None:
            return Response({"reason": "Please provide the attendance sheet URL, Github Classroom URL, and student Github organization URL."}, status=status.HTTP_400_BAD_REQUEST)

        info = CohortInfo()
        info.cohort = Cohort.objects.get(pk=cohort)
        info.attendance_sheet_url = attendance
        info.github_classroom_url = classroom
        info.student_organization_url = github_org

        try:
            info.save()
            serializer = CohortInfoSerializer(info)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            info = CohortInfo.objects.get(pk=pk)
            serializer = CohortInfoSerializer(info)
            return Response(serializer.data)

        except CohortInfo.DoesNotExist as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except ValueError as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            info = CohortInfo.objects.get(pk=pk)
            info.attendance_sheet_url = request.data.get('attendance_sheet_url', None)
            info.github_classroom_url = request.data.get('github_classroom_url', None)
            info.student_organization_url = request.data.get('student_organization_url', None)
            info.save()

        except CohortInfo.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request):
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CohortSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Cohort
        fields = ( 'id', 'name' )


class CohortInfoSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    cohort = CohortSerializer(many=False)

    class Meta:
        model = CohortInfo
        fields = ('id', 'cohort', 'attendance_sheet_url', 'github_classroom_url', 'student_organization_url')

