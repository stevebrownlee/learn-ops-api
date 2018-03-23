from rest_framework import viewsets
from LearningAPI.serializers import TreehouseBadgeSerializer
from LearningAPI.models import TreehouseBadge


class TreehouseBadgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TreehouseBadge.objects.all()
    serializer_class = TreehouseBadgeSerializer