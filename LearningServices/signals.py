from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from LearningAPI.models.help import RequestQuery
from LearningServices.services import process_queries
from LearningAPI.utils import get_redis_connection, get_rq_queue


@receiver(post_save, sender=RequestQuery)
def trigger_process_queries(sender, instance, created, **kwargs):
    if created:
        try:
            queue = get_rq_queue()  # Get the RQ queue
            queue.enqueue(process_queries)  # Enqueue the job for asynchronous execution
        except Exception as e:
            print(f"Failed to enqueue process_queries task: {e}")
