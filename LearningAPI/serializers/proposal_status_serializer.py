from rest_framework import serializers
from LearningAPI.models import ProposalStatus


class ProposalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalStatus
        fields = ('url', 'status')