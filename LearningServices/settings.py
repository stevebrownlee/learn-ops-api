from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Redis and Django RQ settings
# Redis configuration dictionary
REDIS_CONFIG = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'DB': 0,
    'DEFAULT_TIMEOUT': 360,
}

RQ_QUEUES = {
    'popular_queries': {
        'HOST': REDIS_CONFIG['HOST'],
        'PORT': REDIS_CONFIG['PORT'],
        'DB': REDIS_CONFIG['DB'],
        'DEFAULT_TIMEOUT': REDIS_CONFIG['DEFAULT_TIMEOUT'],
    }
}

HELP_COMMON_TERMS_LIMIT=20
POPULAR_QUERIES_LIMIT=5
