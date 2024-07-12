from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from django.db.models import Q
from LearningAPI.models.help import HelpRequest, RequestQuery

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
                RequestQuery.objects.create(query=query, searcher=request.user)

            # Get common search patterns
            common_patterns = RequestQuery.objects.get_common_patterns()

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
            Response -- JSON serialized RequestQuery instance
        """
        try:
            help_request = HelpRequest.objects.get(pk=pk)
            query = request.data.get('query', '')

            request_query = RequestQuery.objects.create(
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

# Generate a help request serializer class
class HelpRequestSerializer(serializers.ModelSerializer):
    """JSON serializer for help requests

    Arguments:
        serializers
    """
    class Meta:
        model = HelpRequest
        fields = ('id', 'title', 'content', 'created_at', 'author', 'is_resolved')

# Generate class for RequestQueriesSerializer
class RequestQueriesSerializer(serializers.ModelSerializer):
    """JSON serializer for request queries

    Arguments:
        serializers
    """
    class Meta:
        model = RequestQuery
        fields = ('id', 'query', 'searcher', 'helpful_request')
        depth = 1