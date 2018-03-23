from rest_framework import serializers
from LearningAPI.models import TreehouseBadge


class TreehouseBadgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TreehouseBadge
        fields = '__all__'