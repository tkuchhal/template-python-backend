from celery import Celery
from app.config import ConfigManager

ConfigManager.initialize()
redis = ConfigManager.get_redis_adapter()

celery = Celery(
    'celery',
    broker=redis.get_url(),
    backend=redis.get_url(),
    include=['app.tasks.task_definitions']
)

celery.conf.update(
    result_expires=3600,
)

celery.autodiscover_tasks(['app.tasks'])
