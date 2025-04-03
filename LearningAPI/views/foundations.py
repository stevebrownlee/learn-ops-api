"""Foundations Course tracking view set module"""
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.coursework import FoundationsExercise

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
        fields = ('id', 'learner_github_id', 'title', 'slug', 'attempts',
                  'complete', 'completed_on', 'first_attempt', 'last_attempt')
        # Exclude completed_code field


class FoundationsViewSet(ViewSet):
    """Foundations view set"""

    permission_classes = (FoundationsPermission,)

    def list(self, request):
        """Handle GET requests to get all foundations exercises

        Returns:
            Response -- JSON serialized list of foundations exercises
        """
        # Get query parameters
        learner_github_id = request.query_params.get('learner_github_id', None)
        last_attempt_param = request.query_params.get('lastAttempt', None)

        # Start with all exercises
        exercises = FoundationsExercise.objects.all()

        # Filter by learner_github_id if provided
        if learner_github_id is not None:
            exercises = exercises.filter(learner_github_id=learner_github_id)

        # Filter by last_attempt
        if last_attempt_param is not None:
            # If lastAttempt parameter is provided, use it
            try:
                last_attempt_date = datetime.fromisoformat(last_attempt_param.replace('Z', '+00:00')).date()
                exercises = exercises.filter(last_attempt__gte=last_attempt_date)
            except ValueError:
                # If invalid date format, use default (current date - 30 days)
                thirty_days_ago = datetime.now().date() - timedelta(days=30)
                exercises = exercises.filter(last_attempt__gte=thirty_days_ago)
        else:
            # Default to current date minus 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            exercises = exercises.filter(last_attempt__gte=thirty_days_ago)

        serializer = FoundationsSerializer(exercises, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            user_id = request.data.get('userId', None)
            exercise = FoundationsExercise.objects.get(slug=pk, learner_github_id=user_id)
            exercise.attempts = request.data.get('attempts', 0)
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
            exercise.learner_github_id = user_id
            exercise.save()


        except FoundationsExercise.DoesNotExist:
            # If the foundations exercise entry does not exist, create it
            exercise = FoundationsExercise()
            exercise.slug = pk
            exercise.attempts = request.data.get('attempts', 0)
            exercise.complete = request.data.get('completed', False)

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
            exercise.title = request.data.get('title', "Undefined")
            exercise.learner_github_id = user_id
            exercise.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except IntegrityError:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

