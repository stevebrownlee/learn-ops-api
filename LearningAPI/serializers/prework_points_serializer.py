from rest_framework import serializers
from LearningAPI.models import PreworkPoints


class PreworkPointsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PreworkPoints
        fields = '__all__'