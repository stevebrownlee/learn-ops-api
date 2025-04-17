"""Foundations Course tracking view set module"""
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.coursework import FoundationsExercise
from LearningAPI.models.people import Cohort, NssUserCohort, NssUser


class FoundationsPermission(permissions.BasePermission):
    """Foundations permissions"""

    def has_permission(self, request, view):
        if view.action in ['list',]:
            return request.auth.user.is_staff
        if view.action in ['update',]:
            return True

        return False


class FoundationsSerializer(serializers.ModelSerializer):
    """JSON serializer for Foundations exercises"""

    class Meta:
        model = FoundationsExercise
        fields = ('id', 'learner_github_id', 'title', 'slug', 'attempts', 'learner_name', 'cohort',
                  'complete', 'completed_on', 'first_attempt', 'last_attempt', 'used_solution', )
        # Exclude completed_code field


def create_entry(pk, exercise, request, user_id):
    """Create or update a FoundationsExercise entry
    Args:
        exercise (FoundationsExercise): The FoundationsExercise instance to update or create
        request (Request): The request object containing data for the exercise
    """
    cohort = request.data.get('cohort', "Unassigned")

    if cohort != "Unassigned":
        # Possible values are a string that starts with 'd' for day cohorts or 'e' for evening cohorts
        # followed by a number representing the cohort number
        # Convert 'd' into 'Day ' and 'e' into 'Evening '
        if cohort.startswith('d'):
            cohort = 'Day ' + cohort[1:]
        elif cohort.startswith('e'):
            cohort = 'Evening ' + cohort[1:]

    exercise.cohort = cohort
    exercise.slug = pk
    exercise.attempts = request.data.get('attempts', 0)
    exercise.learner_name = request.data.get('username', "")
    exercise.complete = request.data.get('completed', False)
    exercise.title = request.data.get('title', "Undefined")

    # Parse ISO 8601 timestamp for completed_on
    completed_at = request.data.get('completedAt', None)
    if completed_at:
        exercise.completed_on = datetime.fromisoformat(completed_at.replace('Z', '+00:00')).date()
    else:
        exercise.completed_on = None

    # Parse ISO 8601 timestamp for first_attempt
    first_attempt = request.data.get('firstAttempt', None)
    if first_attempt:
        exercise.first_attempt = datetime.fromisoformat(first_attempt.replace('Z', '+00:00')).date()
    else:
        exercise.first_attempt = None

    # Parse ISO 8601 timestamp for last_attempt
    last_attempt = request.data.get('lastAttempt', None)
    if last_attempt:
        exercise.last_attempt = datetime.fromisoformat(last_attempt.replace('Z', '+00:00')).date()
    else:
        exercise.last_attempt = None

    exercise.completed_code = request.data.get('completedCode', None)
    exercise.used_solution = request.data.get('solutionShown', None)
    exercise.learner_github_id = user_id
    exercise.save()

class FoundationsViewSet(ViewSet):
    """Foundations view set"""

    permission_classes = (FoundationsPermission,)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        user_id = request.data.get('userId', None)
        if user_id is not None:
            try:
                exercise = FoundationsExercise.objects.get(slug=pk, learner_github_id=user_id)
                create_entry(pk, exercise, request, user_id)

            except FoundationsExercise.DoesNotExist:
                # If the foundations exercise entry does not exist, create it
                exercise = FoundationsExercise()
                create_entry(pk, exercise, request, user_id)

                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except IntegrityError:
                return Response(None, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You must provide a \'userId\' in the request body'}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        """Handle GET requests to get all foundations exercises

        Returns:
            Response -- JSON serialized list of foundations exercises
        """
        # Get query parameters
        learner_name = request.query_params.get('learnerName', None)
        last_attempt_param = request.query_params.get('lastAttempt', None)

        # Get all exercises ordered by learner_github_id, and grouped by learner_name
        exercises = FoundationsExercise.objects.all().order_by('learner_github_id')

        # Filter by learner_name if provided
        if learner_name is not None:
            exercises = exercises.filter(learner_name__icontains=learner_name)

        # Filter by last_attempt
        if last_attempt_param is not None:
            # If lastAttempt parameter is provided, use it
            try:
                last_attempt_date = datetime.fromisoformat(last_attempt_param.replace('Z', '+00:00')).date()
                exercises = exercises.filter(last_attempt__gte=last_attempt_date)
            except ValueError:
                # If invalid date format, use default (current date - 90 days)
                thirty_days_ago = datetime.now().date() - timedelta(days=90)
                exercises = exercises.filter(last_attempt__gte=thirty_days_ago)
        else:
            # Default to current date minus 90 days
            thirty_days_ago = datetime.now().date() - timedelta(days=90)
            exercises = exercises.filter(last_attempt__gte=thirty_days_ago)

        # Create hashmap to store unique learners. Github ID is the key and a list of exercises is the value
        # This will help in filtering out duplicate learners
        unique_learners = {}
        for exercise in exercises:
            if exercise.learner_github_id not in unique_learners:
                unique_learners[exercise.learner_github_id] = {
                    'learner_name': exercise.learner_name,
                    'exercises': [],
                    'cohort': exercise.cohort,
                }
            unique_learners[exercise.learner_github_id]['exercises'].append(exercise)

        # Serialize the unique learners with UniqueLearnerSerializer
        unique_learners_list = []
        for learner_id, learner_data in unique_learners.items():
            unique_learners_list.append(UniqueLearnerSerializer(data=learner_data).create(learner_data))


        # serializer = FoundationsSerializer(exercises, many=True)
        # return Response(serializer.data)
        return Response(unique_learners_list)


# Create a serializer that converts the `unique_learners` structure to JSON
class UniqueLearnerSerializer(serializers.Serializer):
    """JSON serializer for unique learners"""
    learner_name = serializers.CharField()
    cohort = serializers.CharField()
    exercises = FoundationsSerializer(many=True)

    def create(self, validated_data):
        """Create a new unique learner"""
        exercises = FoundationsSerializer(validated_data.get('exercises', []), many=True)
        return {
            'learner_name': validated_data.get('learner_name'),
            'cohort': validated_data.get('cohort'),
            'exercises': exercises.data
        }
