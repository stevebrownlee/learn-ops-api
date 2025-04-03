from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import HttpResponseServerError
from rest_framework import serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from datetime import datetime
from LearningAPI.models.coursework import FoundationsExercise

class FoundationsPermission(permissions.BasePermission):
    """Foundations permissions"""

    def has_permission(self, request, view):
        return True


class FoundationsViewSet(ViewSet):
    """Foundations view set"""

    permission_classes = (FoundationsPermission,)

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
            exercise.learner_github_id = user_id
            exercise.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except IntegrityError:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

