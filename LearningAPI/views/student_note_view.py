"""Student view module"""
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.people import NssUser
from LearningAPI.models.people import StudentNote


class StudentNoteViewSet(ModelViewSet):
    """Student note viewset"""
    queryset = StudentNote.objects.all()


    def list(self, request):
        studentId = request.query_params.get('studentId', None)

        if studentId is None:
            return Response({'message': 'You must provide a `studentId` query string parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = NssUser.objects.get(pk=studentId)
        except NssUser.DoesNotExist:
            return Response({'message': 'Invalid student id.'}, status=status.HTTP_404_NOT_FOUND)

        notes = StudentNote.objects.filter(student=student)
        data = StudentNoteSerializer(notes, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        student = NssUser.objects.get(pk=request.data['studentId'])
        coach = NssUser.objects.get(user=request.auth.user)

        note_text = request.data.get('note', None)
        if note_text is None:
            return Response({"reason": 'You did not provide any note text.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            note = StudentNote()
            note.student = student
            note.coach = coach
            note.note = note_text
            note.save()

            serializer = StudentNoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentNoteSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = StudentNote
        fields = ('id', 'note', 'author', 'created_on',)
