from rest_framework import viewsets
from LearningAPI.serializers import CohortSerializer
from LearningAPI.models import Cohort


class CohortViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
