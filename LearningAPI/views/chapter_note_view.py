from django.db.models import Count
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import ChapterNote, Chapter, Book, Project


class ChapterNoteViewSet(ViewSet):
    """Chapter view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        chapter = Chapter()
        chapter.name = request.data["name"]

        bid = int(request.data["book_id"])
        book = Book.objects.get(pk=bid)
        chapter.book = book

        pid = int(request.data["project_id"])
        project = Project.objects.get(pk=pid)
        chapter.project = project

        try:
            chapter.save()
            serializer = ChapterSerializer(
                chapter, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            chapter = Chapter.objects.get(pk=pk)

            serializer = ChapterSerializer(
                chapter, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            chapter = Chapter.objects.get(pk=pk)
            chapter.name = request.data["name"]

            book = Book.objects.get(pk=request.data["book_id"])
            chapter.book = book

            project = Project.objects.get(pk=request.data["project_id"])
            chapter.project = project

            chapter.save()
        except Chapter.DoesNotExist:
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
            chapter = Chapter.objects.get(pk=pk)
            chapter.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Chapter.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            chapters = Chapter.objects.all().order_by('pk')

            serializer = ChapterSerializer(
                chapters, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class ChapterSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Chapter
        fields = ('id', 'name', 'book', 'project', )
