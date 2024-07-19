# imports for this module's classes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers, status
from LearningAPI.models.help import RequestQuery
from LearningAPI.models.people import NssUser

# Generate class for RequestQuerySerializer
class RequestQuerySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for request queries"""

    class Meta:
        model = RequestQuery
        fields = ('id', 'query', 'helpful_request')


#Generate the view class to handle HTTP requests for the RequestQuery model
class RequestQueryViewSet(viewsets.ViewSet):
    """RequestQuery view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized request query instance
        """
        request_query = RequestQuery()
        request_query.query = request.data['query']
        request_query.searcher = NssUser.objects.get(user=request.auth.user)

        request_query.save()

        serializer = RequestQuerySerializer(request_query, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

