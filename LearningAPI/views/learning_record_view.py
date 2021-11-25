from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import LearningRecord

class LearningRecordSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = LearningRecord
        fields = '__all__'

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
