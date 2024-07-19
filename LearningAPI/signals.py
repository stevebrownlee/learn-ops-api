import json
import logging
import redis
from django.db.models.signals import post_save
from django.dispatch import receiver
from LearningAPI.models.help import RequestQuery

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
logger = logging.getLogger("LearningPlatform")

@receiver(post_save, sender=RequestQuery)
def trigger_process_queries(sender, instance, created, **kwargs):
    if created:
        try:
            queries = list(RequestQuery.objects \
                .filter(helpful_request__isnull=False) \
                .values_list('query', flat=True))
            message = json.dumps({'queries': queries})

            redis_client.publish('channel_help_query', message)

            logger.debug('Published message to channel_help_query')

        except Exception as e:
            logger.exception("Failed to publish message to channel_help_query: %s", e)
