from rest_framework import serializers
from LearningAPI.models import NssUserBadge


class NssUserBadgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NssUserBadge
        fields = '__all__'