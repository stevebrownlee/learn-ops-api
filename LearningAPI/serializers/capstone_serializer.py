from rest_framework import serializers
from LearningAPI.models import Capstone


class CapstoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capstone
        fields = '__all__'