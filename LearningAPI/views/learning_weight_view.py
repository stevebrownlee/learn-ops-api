from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import LearningWeight

class LearningWeightSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = LearningWeight
        fields = '__all__'

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class LearningWeightViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = LearningWeight.objects.all().order_by("tier")
    serializer_class = LearningWeightSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LargeResultsSetPagination
