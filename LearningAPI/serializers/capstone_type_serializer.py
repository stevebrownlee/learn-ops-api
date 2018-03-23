from rest_framework import serializers
from LearningAPI.models import CapstoneType


class CapstoneTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapstoneType
        fields = '__all__'