from rest_framework import viewsets
from LearningAPI.serializers import ExerciseSerializer
from LearningAPI.models import Exercise


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer