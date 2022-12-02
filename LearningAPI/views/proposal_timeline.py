from rest_framework import serializers, permissions
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.coursework import CapstoneTimeline


class TimelineSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = CapstoneTimeline
        fields = '__all__'


class TimelinePermission(permissions.BasePermission):
    """Custom permissions for assessment status view"""
    def has_permission(self, request, view):
        if view.action in ['create', 'retrieve', 'list', 'destroy']:
            return request.auth.user.is_staff

        return False


class TimelineView(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = CapstoneTimeline.objects.all()
    serializer_class = TimelineSerializer
    permission_classes = [TimelinePermission]
