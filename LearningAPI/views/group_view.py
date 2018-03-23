from rest_framework import viewsets
from LearningAPI.serializers import GroupSerializer
from django.contrib.auth.models import Group


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer