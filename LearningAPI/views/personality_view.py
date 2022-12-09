from rest_framework import serializers, permissions
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.people import StudentPersonality

from .personality import myers_briggs_persona

class PersonalitySerializer(serializers.ModelSerializer):
    """JSON serializer"""
    briggs_myers_type = serializers.SerializerMethodField()

    def get_briggs_myers_type(self, obj):
        if obj.briggs_myers_type != "":
            return {
                "code": obj.briggs_myers_type,
                "description": myers_briggs_persona(obj.briggs_myers_type)
            }
        else:
            return {}

    class Meta:
        model = StudentPersonality
        fields = (
            'briggs_myers_type', 'bfi_extraversion',
            'bfi_agreeableness', 'bfi_conscientiousness',
            'bfi_neuroticism', 'bfi_openness',
        )

class PersonalityPermission(permissions.BasePermission):
    """Custom permissions for assessment personality view"""
    def has_permission(self, request, view):
        if view.action in ['list',]:
            return request.auth.user.is_staff
        else:
            return False


class PersonalityView(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = StudentPersonality.objects.all()
    serializer_class = PersonalitySerializer
    permission_classes = [PersonalityPermission]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(student__id=self.request.query_params['studentId'])
        return query_set
