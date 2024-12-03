from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import StudentInterview, NssUser


class InterviewViewSet(ViewSet):
    """Interview view set"""

    permission_classes = (IsAdminUser,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        interview = StudentInterview()
        interview.instructor = NssUser.objects.get(user=request.auth.user)
        interview.student = NssUser.objects.get(id=request.data["student_id"])

        try:
            interview.save()
            serializer = InterviewSerializer(interview)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

class InterviewSerializer(serializers.ModelSerializer):
    """JSON serializer for interview objects"""

    class Meta:
        model = StudentInterview
        fields = ( 'id', 'student', 'instructor', )
