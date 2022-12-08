from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.people import StudentTag
from LearningAPI.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Tag
        fields = '__all__'

class StudentTagSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    # tag = TagSerializer(many=False)

    class Meta:
        model = StudentTag
        fields = ('id', 'student', 'tag', )

class StudentTagViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing core skills.
    """
    queryset = StudentTag.objects.all()
    serializer_class = StudentTagSerializer
    permission_classes = [IsAdminUser]
