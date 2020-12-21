from rest_framework import viewsets
from LearningAPI.serializers import CapstoneSerializer
from LearningAPI.models import Capstone


class CapstoneViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Capstone.objects.all()
    serializer_class = CapstoneSerializer