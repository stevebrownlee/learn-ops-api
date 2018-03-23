from rest_framework import viewsets
from LearningAPI.serializers import CapstoneTypeSerializer
from LearningAPI.models import CapstoneType


class CapstoneTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows capstone types to be viewed or edited.
    """
    queryset = CapstoneType.objects.all()
    serializer_class = CapstoneTypeSerializer