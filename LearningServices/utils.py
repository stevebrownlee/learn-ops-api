import redis
from django.conf import settings
from rq import Queue

def get_redis_connection():
    return redis.Redis(
        host=settings.REDIS_CONFIG['HOST'],
        port=settings.REDIS_CONFIG['PORT'],
        db=settings.REDIS_CONFIG['DB']
    )

def get_rq_queue(name='default'):
    connection = get_redis_connection()
    return Queue(name, connection=connection)
