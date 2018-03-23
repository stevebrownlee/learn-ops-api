from rest_framework import serializers
from LearningAPI.models import Proposal


class ProposalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'