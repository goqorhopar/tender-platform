"""
Tender Platform - Celery Configuration
Production-grade Celery setup with Redis broker and result backend.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


# Create Celery application
celery_app = Celery(
    "tender_platform",
    broker=settings.effective_celery_broker,
    backend=settings.effective_celery_backend,
    include=["app.tasks.tasks"],
)

# Configure Celery
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Result settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Broker settings
    broker_heartbeat=30,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=5,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Rate limiting
    task_default_rate_limit="100/m",
    
    # Retries
    task_default_retry_delay=30,
    task_max_retries=3,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-old-tenders": {
        "task": "app.tasks.tasks.cleanup_old_tenders",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "send-daily-notifications": {
        "task": "app.tasks.tasks.send_daily_notifications",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    "sync-external-tenders": {
        "task": "app.tasks.tasks.sync_external_tenders",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}


# ============================================================================
# TASK DECORATOR
# ============================================================================
def task(*args, **kwargs):
    """Custom task decorator with default settings."""
    kwargs.setdefault("bind", False)
    kwargs.setdefault("autoretry_for", (Exception,))
    kwargs.setdefault("max_retries", 3)
    kwargs.setdefault("default_retry_delay", 30)
    return celery_app.task(*args, **kwargs)
