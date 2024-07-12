import redis
import json
from django.conf import settings
from django.db import models


class RequestQueryManager(models.Manager):
    def get_common_patterns(self):
        # Connect to Redis
        redis_cache = LearningAPI.utils.get_redis_connection()

        queries = RequestQuery.objects.filter(helpful_request__isnull=False).values_list('query', flat=True)

        # Fetch the cached results
        cached_results = redis_cache.get('search_results')

        # Check if results exist in the cache
        if cached_results:
            return json.loads(cached_results)
        else:
            # Return a default value or handle the cache miss
            return [{'query_token': 'No cached results available'}]

class RequestQuery(models.Model):
    query = models.TextField(null=False, blank=False)
    searcher = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='search_queries')
    helpful_request = models.ForeignKey('HelpRequest', on_delete=models.SET_NULL, null=True, blank=True)

    # objects = RequestQueryManager()
