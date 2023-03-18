import os
import requests

from rest_framework import serializers, permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from LearningAPI.models.coursework import CapstoneTimeline, Capstone, ProposalStatus


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

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        capstone_id = request.data.get('capstone', None)
        status_id = request.data.get('status', None)


        if capstone_id is not None and status_id is not None:
            capstone = Capstone.objects.get(pk=capstone_id)
            proposal_status = ProposalStatus.objects.get(pk=status_id)

            timeline = CapstoneTimeline()
            timeline.capstone = capstone
            timeline.status = proposal_status
            timeline.save()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Send message to student
            channel_payload = {
                "text": f":hi: Hello, {capstone.student}!\n\n\n:mortar_board: Your capstone proposal was marked as {proposal_status.status}.",
                "token": os.getenv("SLACK_BOT_TOKEN"),
                "channel": "G08NYBJSY"
            }

            requests.post(
                "https://slack.com/api/chat.postMessage",
                data=channel_payload,
                headers=headers,
                timeout=10
            )

            serialized = TimelineSerializer(timeline).data
            return Response(serialized, status=status.HTTP_201_CREATED)

        return Response({'message': 'You must provide a capstone Id and a proposal status Id'}, status=status.HTTP_400_BAD_REQUEST)
