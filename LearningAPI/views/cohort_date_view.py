from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from LearningAPI.models.people import Cohort, CohortEvent,CohortEventType
from LearningAPI.utils import get_logger, log_action

logger = get_logger("LearningAPI.cohortevent")

class CohortEventsViewSet(ViewSet):
    """Viewset to handle cohort date-related operations"""

    @log_action("event_creation")
    def create(self, request):
        """Handle POST operations for creating a cohort event

        Returns:
            Response -- JSON serialized instance
        """
        cohort_id = request.data.get('cohort', None)
        event_name = request.data.get('name', None)
        event_type = request.data.get('type', None)
        event_datetime = request.data.get('datetime', None)
        description = request.data.get('description', '')

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            event_type_instance = CohortEventType.objects.get(pk=event_type)
            cohort_event = CohortEvent.objects.create(
                cohort=cohort,
                event_name=event_name,
                event_datetime=event_datetime,
                event_type=event_type_instance,
                description=description
            )
            serializer = CohortDateSerializer(cohort_event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except CohortEventType.DoesNotExist as ex:
            logger.error(f"Cohort event type not found: {ex}")
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Cohort.DoesNotExist as ex:
            logger.error(f"Cohort not found: {ex}")
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(f"Error creating cohort event: {ex}")
            return Response({'message': 'An error occurred while creating the cohort event.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Handle DELETE operations for a cohort event

        Returns:
            Response -- JSON serialized instance
        """
        try:
            cohort_event = CohortEvent.objects.get(pk=pk)
            cohort_event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CohortEvent.DoesNotExist as ex:
            logger.error(f"Cohort event not found: {ex}")
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(f"Error deleting cohort event: {ex}")
            return Response({'message': 'An error occurred while deleting the cohort event.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET operations to retrieve all cohort events

        Returns:
            Response -- JSON serialized list of cohort events
        """
        cohort_id = request.query_params.get('cohort', None)

        try:
            if cohort_id:
                cohort = Cohort.objects.get(pk=cohort_id)
                events = CohortEvent.objects.filter(cohort=cohort).order_by('-event_datetime')
            else:
                events = CohortEvent.objects.all().order_by('-event_datetime')

            serializer = CohortDateSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cohort.DoesNotExist as ex:
            logger.error(f"Cohort not found: {ex}")
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(f"Error retrieving cohort events: {ex}")
            return Response({'message': 'An error occurred while retrieving the cohort events.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CohortEventTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = CohortEventType
        fields = ( 'id', 'description', 'color', )

class CohortDateSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    event_type = CohortEventTypeSerializer(many=False, read_only=True)

    class Meta:
        model = CohortEvent
        fields = ( 'id', 'event_name', 'event_type', 'event_datetime', 'description', )
