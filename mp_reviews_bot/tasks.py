from __future__ import annotations

from datetime import datetime, timedelta, timezone

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import delete

from mp_reviews_bot.config import (
    AUDIT_RETENTION_DAYS,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CELERY_TIMEZONE,
)
from mp_reviews_bot.db import SessionLocal
from mp_reviews_bot.models import AuditLog

celery_app = Celery(
    "mp_reviews_bot",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
celery_app.conf.timezone = CELERY_TIMEZONE
celery_app.conf.beat_schedule = {
    "audit-purge-old-logs": {
        "task": "audit.purge_old_logs",
        "schedule": crontab(minute=0, hour=3),
    }
}


@celery_app.task(name="audit.purge_old_logs")
def purge_old_audit_logs() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=AUDIT_RETENTION_DAYS)
    with SessionLocal() as session:
        result = session.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
        session.commit()
        return result.rowcount or 0
