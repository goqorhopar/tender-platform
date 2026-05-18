"""Celery application configuration."""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "tender_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.tender_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    broker_connection_retry_on_startup=True,
    broker_pool_limit=10,
    result_expires=3600,
    task_routes={
        "app.tasks.tender_tasks.*": {"queue": "tenders"},
    },
)

# Scheduled tasks (for Celery Beat)
celery_app.conf.beat_schedule = {
    "check-tender-deadlines": {
        "task": "app.tasks.tender_tasks.check_tender_deadlines",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-tasks": {
        "task": "app.tasks.tender_tasks.cleanup_old_tasks",
        "schedule": 86400.0,  # Every day
    },
}
