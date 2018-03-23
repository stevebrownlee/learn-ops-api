from rest_framework import viewsets
from LearningAPI.serializers import NssUserCohortSerializer
from LearningAPI.models import NssUserCohort


class NssUserCohortViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = NssUserCohort.objects.all()
    serializer_class = NssUserCohortSerializer