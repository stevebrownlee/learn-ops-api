from rest_framework import viewsets
from LearningAPI.serializers import NssUserSerializer
from LearningAPI.models import NssUser


class NssUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = NssUser.objects.all()
    serializer_class = NssUserSerializer