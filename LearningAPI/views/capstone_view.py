import os
import requests
import logging

from rest_framework import serializers
from rest_framework import status, permissions
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from ..models.coursework import Capstone, Course, CapstoneTimeline
from ..models.people import NssUser, Cohort


class CapstonePermission(permissions.BasePermission):
    """Cohort permissions"""

    def has_permission(self, request, view):
        if view.action in ['create', 'update']:
            return True
        elif view.action in ['retrieve', 'list']:
            return request.auth.user.is_staff
        else:
            return False


class CapstoneViewSet(ViewSet):
    """Capstone view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        student = NssUser.objects.get(user=request.auth.user)

        try:
            course = Course.objects.get(pk=request.data.get('course', None))
        except Course.DoesNotExist:
            return Response(
                { 'message': 'Could not find any matching courses'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Capstone.objects.get(student=student, course=course)

            return Response({'message': 'You have already submittted a proposal for this course. If you made updates, just let your instructional team know via Slack'}, status=status.HTTP_400_BAD_REQUEST)
        except Capstone.DoesNotExist:
            proposal = Capstone()
            proposal.course = course
            proposal.student = student
            proposal.description = request.data.get("description", "")
            proposal.proposal_url = request.data.get("proposalURL", "")
            proposal.repo_url = request.data.get("repoURL", "")
            proposal.save()

        # Send message to instructors
        try:
            slack_channel = student.assigned_cohorts.order_by("-id").first().cohort.slack_channel

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Send message to instructor channel
            channel_payload = {
                "text": f"{student} has submitted their {course} capstone proposal",
                "token": os.getenv("SLACK_BOT_TOKEN"),
                "channel": slack_channel
            }

            requests.post(
                "https://slack.com/api/chat.postMessage",
                data=channel_payload,
                headers=headers,
                timeout=10
            )

            # Send message to student
            channel_payload = {
                "text": f":mortar_board: Your {course} capstone proposal was successfully submitted.\n\n\nIf you make changes to anything in your proposal, you do not need to submit again.",
                "token": os.getenv("SLACK_BOT_TOKEN"),
                "channel": student.slack_handle
            }

            requests.post(
                "https://slack.com/api/chat.postMessage",
                data=channel_payload,
                headers=headers,
                timeout=10
            )
        except Exception as ex:
            logger = logging.getLogger("LearningPlatform")
            logger.exception(getattr(ex, 'message', repr(ex)))
            return Response({'message': 'Proposal saved but unable to send Slack message'}, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        proposals = Capstone.objects.filter(pk=pk)
        serializer = CapstoneSerializer(proposals, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        student_id = request.query_params.get("studentId", None)
        cohort_id = request.query_params.get("cohortId", None)

        if cohort_id is not None:
            cohort = Cohort.objects.get(pk=cohort_id)
            proposals = Capstone.objects.filter(student__assigned_cohorts__cohort=cohort)
            serializer = CapstoneSerializer(proposals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if student_id is not None:
            student = NssUser.objects.get(pk=student_id)
            proposals = Capstone.objects.filter(student=student)
            serializer = CapstoneSerializer(proposals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class CapstoneStatusSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.status.status

    class Meta:
        model = CapstoneTimeline
        fields = ('id', 'status', 'date')


class CapstoneSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    course = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    statuses = CapstoneStatusSerializer(many=True)

    def get_course(self, obj):
        return obj.course.name

    def get_name(self, obj):
        return f'{obj.student.user.first_name} {obj.student.user.last_name}'

    class Meta:
        model = Capstone
        fields = ('id', 'name', 'course', 'proposal_url', 'description', 'statuses')
        depth = 1
