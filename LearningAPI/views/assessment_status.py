from rest_framework import serializers, permissions
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models import StudentAssessmentStatus


class StatusSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = StudentAssessmentStatus
        fields = '__all__'

class StatusPermission(permissions.BasePermission):
    """Custom permissions for assessment status view"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve',]:
            return True
        else:
            return False


class AssessmentStatusView(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = StudentAssessmentStatus.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [StatusPermission]
