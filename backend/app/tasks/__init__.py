"""Tasks package."""

from app.tasks.celery_app import celery_app
from app.tasks.tender_tasks import (
    analyze_tender,
    fetch_tender_documents,
    check_tender_deadlines,
    cleanup_old_tasks,
    generate_tender_report,
    send_notification,
)

__all__ = [
    "celery_app",
    "analyze_tender",
    "fetch_tender_documents",
    "check_tender_deadlines",
    "cleanup_old_tasks",
    "generate_tender_report",
    "send_notification",
]
