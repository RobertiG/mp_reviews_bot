from datetime import datetime, timedelta

from worker.celery_app import celery_app
from app.db import SessionLocal
from app import models
from app.services.llm import LLMAdapter
from app.services.gating import can_autosend


@celery_app.task
def poll_marketplaces():
    return "polling"


@celery_app.task
def process_event(event_id: int):
    return event_id


@celery_app.task
def generate_reply(event_id: int):
    db = SessionLocal()
    try:
        event = db.get(models.Event, event_id)
        if not event:
            return None
        llm = LLMAdapter()
        response = llm.generate(event.text)
        event.suggested_reply = response.text
        event.confidence = response.confidence
        event.kb_rule_ids = response.kb_rule_ids
        event.conflict = response.conflict
        event.status = "drafted"
        db.commit()
        return event.id
    finally:
        db.close()


@celery_app.task
def auto_send(event_id: int):
    db = SessionLocal()
    try:
        event = db.get(models.Event, event_id)
        if not event:
            return None
        if not can_autosend(event):
            event.status = "approved"
            db.commit()
            return False
        event.status = "sent"
        db.commit()
        return True
    finally:
        db.close()


@celery_app.task
def cleanup_logs():
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=90)
        db.query(models.AuditLog).filter(models.AuditLog.created_at < cutoff).delete()
        db.commit()
        return True
    finally:
        db.close()
