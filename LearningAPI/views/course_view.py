from django.db.models import Count
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import Course, Book


class CourseViewSet(ViewSet):
    """Course view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        course = Course()
        course.name = request.data["name"]

        try:
            course.save()
            serializer = CourseSerializer(course, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            course = Course.objects.annotate(
                chapters=Count('books__chapters')
            ).get(pk=pk)

            serializer = CourseSerializer(course, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            course = Course.objects.get(pk=pk)
            course.name = request.data["name"]

            course.save()
        except Course.DoesNotExist:
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
            course = Course.objects.get(pk=pk)
            course.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Course.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            courses = Course.objects.all().order_by('pk')

            serializer = CourseSerializer(
                courses, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class BookSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Book
        fields = ('id', 'name',)

class CourseSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    books = BookSerializer(many=True)
    # books = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Book.objects.all())

    class Meta:
        model = Course
        fields = ('id', 'name', 'books', 'chapters')
