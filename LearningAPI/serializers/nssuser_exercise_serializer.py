from rest_framework import serializers
from LearningAPI.models import NssUserExercise


class NssUserExerciseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NssUserExercise
        fields = '__all__'