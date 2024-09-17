from celery import Celery

from src.env import RedisEnv

redis_env = RedisEnv()
app = Celery(
    'tasks',
    broker=redis_env.connect_str,
    backend=redis_env.connect_str
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
