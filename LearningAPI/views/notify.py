from rest_framework.decorators import api_view
from rest_framework.response import Response
from LearningAPI.models.people import NssUser
from LearningAPI.utils import SlackAPI

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

    instructors = request.data.get("instructors", None)
    student_channel = request.data.get("studentChannel", None)
    message = request.data.get("message", None)

    if instructors:
        # Get the cohort's instrutor Slack channel
        target_user = NssUser.objects.get(user=request.auth.user)
        slack_channel = target_user.assigned_cohorts.order_by("-id").first().cohort.slack_channel
        SlackAPI().send_message( text=message, channel=slack_channel )
        return Response({ 'message': 'Notification sent to instructor channel'}, status=200)

    elif student_channel is not None:
        slack_channel = target_user.assigned_cohorts.order_by("-id").first().cohort.slack_channel
        SlackAPI().send_message( text=message, channel=student_channel )
        return Response({ 'message': 'Notification sent to student'}, status=200)

    return Response({ 'message': 'Invalid request'}, status=400)
