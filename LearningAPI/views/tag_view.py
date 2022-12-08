from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Tag
        fields = '__all__'

class TagViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing core skills.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
