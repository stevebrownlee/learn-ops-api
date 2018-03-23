from rest_framework import serializers
from LearningAPI.models import NssUserCohort


class NssUserCohortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NssUserCohort
        fields = '__all__'