from rest_framework import viewsets
from LearningAPI.serializers import UserCohortSerializer
from LearningAPI.models import UserCohort


class UserCohortViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserCohort.objects.all()
    serializer_class = UserCohortSerializer