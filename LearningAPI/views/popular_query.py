import json
import redis
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def popular_queries(request):
    try:
        redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)

        # Fetch the cached results
        cached_results = redis_connection.get('search_results')

        # Check if results exist in the cache
        if cached_results:
            return Response(json.loads(cached_results), status=status.HTTP_200_OK)
        else:
            # Return a default value or handle the cache miss
            return Response({'message': 'No cached results available'}, status=status.HTTP_404_NOT_FOUND)


    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)