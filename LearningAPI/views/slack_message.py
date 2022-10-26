"""View module for handling requests about park areas"""
import os
import requests
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class SlackMessage(ViewSet):
    """For creating Slack channels"""

    def create(self, request):
        """Handle POST requests to create team Slack channels"""

        student_id = request.data.get("student", None)

        if student_id is not None:

            # Create the Slack channel
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            channel_payload = {
                "text": request.data.get("text", "Test message"),
                "token": os.getenv("SLACK_BOT_TOKEN"),
                "channel": student_id
            }

            res = requests.post(
                "https://slack.com/api/chat.postMessage", data=channel_payload, headers=headers)
            message_response = res.json()

            return Response(message_response, status=status.HTTP_201_CREATED)

        return Response(None, status=status.HTTP_400_BAD_REQUEST)
