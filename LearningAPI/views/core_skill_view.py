from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.skill import CoreSkill


class CoreSkillSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = CoreSkill
        fields = '__all__'

class CoreSkillViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing core skills.
    """
    queryset = CoreSkill.objects.all()
    serializer_class = CoreSkillSerializer
    permission_classes = [IsAdminUser]
