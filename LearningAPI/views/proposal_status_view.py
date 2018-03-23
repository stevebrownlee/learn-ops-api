from rest_framework import viewsets
from LearningAPI.serializers import ProposalStatusSerializer
from LearningAPI.models import ProposalStatus


class ProposalStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ProposalStatus.objects.all()
    serializer_class = ProposalStatusSerializer