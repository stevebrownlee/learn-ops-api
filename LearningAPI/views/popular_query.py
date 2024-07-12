from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from LearningAPI.models.help import RequestQuery

@api_view(['GET'])
def popular_queries(request):
    try:
        # Query for popular searches with helpful_request_id
        popular_searches = RequestQuery.objects.get_common_patterns(50)

        # Format the result
        result = [
            {
                "query_token": item,
            }
            for item in popular_searches
        ]

        return Response(result, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)