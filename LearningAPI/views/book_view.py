from django.db.models import Count
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import Book
from LearningAPI.models import Course
from LearningAPI.models import Chapter


class BookViewSet(ViewSet):
    """Book view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        book = Book()
        book.name = request.data["name"]

        course = Course.objects.get(pk=int(request.data["course_id"]))
        book.course = course

        try:
            book.save()
            serializer = BookSerializer(book, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            book = Book.objects.get(pk=pk)

            serializer = BookSerializer(book, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            book = Book.objects.get(pk=pk)
            book.name = request.data["name"]

            course = Course.objects.get(pk=int(request.data["course_id"]))
            book.course = course

            book.save()
        except Book.DoesNotExist:
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
            book = Book.objects.get(pk=pk)
            book.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            books = Book.objects.all().order_by('pk')

            serializer = BookSerializer(
                books, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class ChapterSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Chapter
        fields = ('id', 'name',)

class BookSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    chapters = ChapterSerializer(many=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'chapters', 'course')
