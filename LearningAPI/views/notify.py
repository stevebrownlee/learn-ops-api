import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from LearningAPI.models.people import NssUser

@api_view(['POST'])
def notify(request):
    """
    Sends a notification message to a Slack channel.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: The HTTP response object with a success message.

    Raises:
        NssUser.DoesNotExist: If the NssUser object does not exist.
        AttributeError: If the user attribute is not present in the request's auth object.
        IndexError: If the assigned_cohorts queryset is empty.
        AttributeError: If the cohort attribute is not present in the first assigned_cohorts object.
        AttributeError: If the slack_channel attribute is not present in the cohort object.
        requests.exceptions.Timeout: If the request to the Slack API times out.
    """

    student = NssUser.objects.get(user=request.auth.user)
    slack_channel = student.assigned_cohorts.order_by("-id").first().cohort.slack_channel

    message = request.data.get("message")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    requests.post(
        "https://slack.com/api/chat.postMessage",
        data={
            "text": message,
            "token": os.getenv("SLACK_BOT_TOKEN"),
            "channel": slack_channel
        },
        headers=headers,
        timeout=10
    )

    return Response({ 'message': 'Notification sent to Slack!'}, status=200)
