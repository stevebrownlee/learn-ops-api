from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework import serializers
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser
from LearningAPI.models import NssUser
from rest_framework.response import Response

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
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        students = NssUser.objects.filter(user__is_staff=False)

        serializer = StudentSerializer(
            students, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        return Response({}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        return Response({}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        return Response({}, status=status.HTTP_200_OK)

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

