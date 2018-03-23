from rest_framework import viewsets
from LearningAPI.serializers import NssUserBadgeSerializer
from LearningAPI.models import NssUserBadge


class NssUserBadgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = NssUserBadge.objects.all()
    serializer_class = NssUserBadgeSerializer