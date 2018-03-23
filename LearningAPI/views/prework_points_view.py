from rest_framework import viewsets
from LearningAPI.serializers import PreworkPointsSerializer
from LearningAPI.models import PreworkPoints


class PreworkPointsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PreworkPoints.objects.all()
    serializer_class = PreworkPointsSerializer