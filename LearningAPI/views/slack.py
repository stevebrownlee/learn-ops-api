"""View module for handling requests about park areas"""
import os
import requests
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from LearningAPI.models.people import NssUser


class SlackChannel(ViewSet):
    """For creating Slack channels"""

    def create(self, request):
        """Handle POST requests to create team Slack channels"""

        # Create the Slack channel
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        channel_payload = {
            "name": request.data["name"],
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        student_slack_ids = set()
        for student_id in request.data["students"]:
            student = NssUser.objects.get(pk=student_id)
            if student.slack_handle is not None:
                student_slack_ids.add(student.slack_handle)

        res = requests.post("https://slack.com/api/conversations.create", timeout=10, data=channel_payload, headers=headers)
        channel_res = res.json()

        # Add students to Slack channel
        invitation_payload = {
            "channel": channel_res["channel"]["id"],
            "users": ",".join(list(student_slack_ids)),
            "token": os.getenv("SLACK_BOT_TOKEN")
        }

        res = requests.post("https://slack.com/api/conversations.invite", timeout=10, data=invitation_payload, headers=headers)
        students_res = res.json()

        combined_response = {
            "channel": channel_res,
            "invitations": students_res
        }

        return Response(combined_response, status=status.HTTP_201_CREATED)
