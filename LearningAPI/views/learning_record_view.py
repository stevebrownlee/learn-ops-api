from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import LearningRecord
from LearningAPI.models import LearningRecordWeight
from LearningAPI.models.nssuser import NssUser


class NssUserSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = NssUser
        fields = ('id', 'name')


class RecordWeightSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    score = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    instructor = NssUserSerializer()

    def get_score(self, obj):
        return obj.weight.weight

    def get_label(self, obj):
        return obj.weight.label

    class Meta:
        model = LearningRecordWeight
        fields = ('id', 'score', 'note', 'recorded_on', 'instructor', 'label')


class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    weights = RecordWeightSerializer(many=True)
    student = NssUserSerializer()

    class Meta:
        model = LearningRecord
        fields = ('student', 'description', 'obtained_from',
                  'weights', 'created_on',)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class LearningRecordViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning records.
    """
    queryset = LearningRecord.objects.all()
    serializer_class = LearningRecordSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination
