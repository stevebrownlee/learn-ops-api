"""View module for handling requests about park areas"""
import os
import requests
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class SlackChannel(ViewSet):
    """For creating Slack channels"""

    def create(self, request):
        """Handle POST requests to create team Slack channels"""

        payload = {
            'name': request.data['name'],
            'token': os.getenv('SLACK_BOT_TOKEN')
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        res = requests.post(
            "https://slack.com/api/conversations.create", data=payload, headers=headers)

        return Response(res.json(), status=status.HTTP_201_CREATED)
        # return Response({ "res": "test" }, status=status.HTTP_201_CREATED)
