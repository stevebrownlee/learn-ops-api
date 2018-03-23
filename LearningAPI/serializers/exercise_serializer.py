from rest_framework import serializers
from LearningAPI.models import Exercise


class ExerciseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'