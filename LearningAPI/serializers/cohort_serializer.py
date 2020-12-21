from rest_framework import serializers
from LearningAPI.models import Cohort


class CohortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cohort
        fields = '__all__'
