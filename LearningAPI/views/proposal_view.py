from rest_framework import viewsets
from LearningAPI.serializers import ProposalSerializer
from LearningAPI.models import Proposal


class ProposalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer