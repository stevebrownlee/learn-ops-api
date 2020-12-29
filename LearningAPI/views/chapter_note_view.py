from django.db.models import Count
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models import ChapterNote, Chapter, NssUser


class ChapterNoteViewSet(ViewSet):
    """Chapter view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        note = ChapterNote()
        note.user = NssUser.objects.get(user=request.auth.user)
        note.markdown_text = request.data["markdown_text"]

        chapter = Chapter.objects.get(pk=int(request.data["chapter_id"]))
        note.chapter = chapter

        try:
            note.save()
            serializer = ChapterNoteSerializer(
                note, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            note = ChapterNote.objects.get(pk=pk)

            serializer = ChapterNoteSerializer(
                note, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            note = ChapterNote.objects.get(pk=pk)
            note.markdown_text = request.data["markdown_text"]

            chapter = Chapter.objects.get(pk=int(request.data["chapter_id"]))
            note.chapter = chapter

            note.save()
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
            note = ChapterNote.objects.get(pk=pk)
            note.delete()

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
            notes = ChapterNote.objects.all().order_by('pk')

            serializer = ChapterNoteSerializer(
                notes, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class ChapterNoteSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = ChapterNote
        fields = ( 'id', 'markdown_text', 'public', 'date', )
