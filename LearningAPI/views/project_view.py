from django.db.models import Count
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import Chapter, Book, Project


class ProjectViewSet(ViewSet):
    """Project view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        project = Project()
        project.name = request.data["name"]
        project.implementation_url = request.data["implementation_url"]

        try:
            project.save()
            serializer = ProjectSerializer(
                project, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            project = Project.objects.get(pk=pk)

            serializer = ProjectSerializer(
                project, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            project = Project.objects.get(pk=pk)
            project.name = request.data["name"]
            project.implementation_url = request.data["implementation_url"]

            project.save()
        except Project.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            project = Project.objects.get(pk=pk)
            project.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            projects = Project.objects.all().order_by('pk')

            serializer = ProjectSerializer(
                projects, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class ProjectSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Project
        fields = ('id', 'name', 'implementation_url',)
