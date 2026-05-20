import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1"

celery_app = Celery(
    "twitter_clone",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)