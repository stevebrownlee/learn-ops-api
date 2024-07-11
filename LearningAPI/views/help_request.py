from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import HelpRequest, RequestQueries
from .serializers import HelpRequestSerializer, RequestQueriesSerializer

class HelpRequestViewSet(ViewSet):
    """HelpRequest view set"""

    def list(self, request):
        """Handle GET requests for help requests

        Returns:
            Response -- JSON serialized array of help requests and common search patterns
        """
        try:
            query = request.data.get('question', None)
            help_requests = HelpRequest.objects.all()

            if query:
                help_requests = help_requests.filter(
                    Q(title__icontains=query) | Q(content__icontains=query)
                )
                # Record the search query
                RequestQueries.objects.create(query=query, searcher=request.user)

            # Get common search patterns
            common_patterns = RequestQueries.objects.get_common_patterns()

            # Serialize the results
            help_request_serializer = HelpRequestSerializer(
                help_requests, many=True, context={'request': request})

            response_data = {
                'help_requests': help_request_serializer.data,
                'common_patterns': common_patterns
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def mark_helpful(self, request, pk=None):
        """Handle POST requests to mark a help request as helpful

        Returns:
            Response -- JSON serialized RequestQueries instance
        """
        try:
            help_request = HelpRequest.objects.get(pk=pk)
            query = request.data.get('query', '')

            request_query = RequestQueries.objects.create(
                query=query,
                searcher=request.user,
                helpful_request=help_request
            )

            serializer = RequestQueriesSerializer(request_query, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except HelpRequest.DoesNotExist:
            return Response({'message': 'Help request not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    # Add other methods (create, retrieve, update, destroy) as needed, similar to OpportunityViewSet