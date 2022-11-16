from rest_framework import serializers, permissions
from rest_framework.viewsets import ModelViewSet
from LearningAPI.models.coursework import ProposalStatus


class ProposalStatusSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = ProposalStatus
        fields = '__all__'


class ProposalStatusPermission(permissions.BasePermission):
    """Custom permissions for assessment status view"""
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve',]:
            return True
        else:
            return False


class ProposalStatusView(ModelViewSet):
    """
    A simple ViewSet for viewing and editing learning weights.
    """
    queryset = ProposalStatus.objects.all()
    serializer_class = ProposalStatusSerializer
    permission_classes = [ProposalStatusPermission]
