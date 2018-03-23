from rest_framework import viewsets
from LearningAPI.serializers import NssUserExerciseSerializer
from LearningAPI.models import NssUserExercise


class NssUserExerciseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = NssUserExercise.objects.all()
    serializer_class = NssUserExerciseSerializer