from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Cohort, CohortEvent, CohortEventType
from LearningAPI.utils import get_logger

logger = get_logger("LearningAPI.cohortevent")

class CohortEventTypeViewSet(ViewSet):
    """Viewset to handle cohort event type-related operations"""

    def list(self, request):
        """Handle GET operations to retrieve all cohort events

        Returns:
            Response -- JSON serialized list of cohort events
        """
        try:
            cohort_event_types = CohortEventType.objects.all()
            serializer = CohortEventTypeSerializer(cohort_event_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving cohort event types: {e}")
            return HttpResponseServerError("An error occurred while retrieving cohort event types.")



class CohortEventTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = CohortEventType
        fields = ( 'id', 'description', 'color', )
