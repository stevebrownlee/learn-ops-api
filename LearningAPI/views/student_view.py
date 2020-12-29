from rest_framework import permissions
from django.http import HttpResponseServerError
from rest_framework import serializers
from rest_framework import status
from django.db.models import Q
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from LearningAPI.models import NssUser


class StudentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'destroy']:
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
            student = NssUser.objects.get(pk=pk)
            if request.auth.user == student.user or request.auth.user.is_staff:
                serializer = StudentSerializer(
                    student, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        except NssUser.DoesNotExist as ex:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

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
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = NssUser.objects.get(pk=pk)
            event.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except NssUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        students = NssUser.objects.filter(user__is_staff=False)

        serializer = StudentSerializer(
            students, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = NssUser
        fields = '__all__'
