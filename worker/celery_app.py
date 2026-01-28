from __future__ import annotations

from celery import Celery
from celery.schedules import crontab, schedule
from kombu import Queue

from worker.config import CELERY_SETTINGS


app = Celery("mp_reviews_worker")
app.conf.broker_url = CELERY_SETTINGS.broker_url
app.conf.result_backend = CELERY_SETTINGS.result_backend
app.conf.timezone = CELERY_SETTINGS.timezone
app.conf.enable_utc = CELERY_SETTINGS.enable_utc
app.conf.task_default_queue = CELERY_SETTINGS.task_default_queue
app.conf.task_acks_late = CELERY_SETTINGS.task_acks_late
app.conf.worker_prefetch_multiplier = CELERY_SETTINGS.worker_prefetch_multiplier
app.conf.task_track_started = CELERY_SETTINGS.task_track_started
app.conf.broker_connection_retry_on_startup = (
    CELERY_SETTINGS.broker_connection_retry_on_startup
)
app.conf.task_queues = (
    Queue(CELERY_SETTINGS.polling_queue),
    Queue(CELERY_SETTINGS.ingest_queue),
    Queue(CELERY_SETTINGS.llm_queue),
    Queue(CELERY_SETTINGS.autosend_queue),
    Queue(CELERY_SETTINGS.import_queue),
    Queue(CELERY_SETTINGS.maintenance_queue),
)
app.conf.task_routes = {
    "worker.tasks.poll_wb_ozon": {"queue": CELERY_SETTINGS.polling_queue},
    "worker.tasks.ingest_events": {"queue": CELERY_SETTINGS.ingest_queue},
    "worker.tasks.generate_llm_response": {"queue": CELERY_SETTINGS.llm_queue},
    "worker.tasks.auto_send_response": {"queue": CELERY_SETTINGS.autosend_queue},
    "worker.tasks.import_sku_xlsx": {"queue": CELERY_SETTINGS.import_queue},
    "worker.tasks.retention_cleanup": {"queue": CELERY_SETTINGS.maintenance_queue},
}

app.conf.beat_schedule = {
    "poll-wb-ozon-every-minute": {
        "task": "worker.tasks.poll_wb_ozon",
        "schedule": schedule(run_every=CELERY_SETTINGS.poll_interval_seconds),
        "options": {
            "queue": CELERY_SETTINGS.polling_queue,
            "expires": CELERY_SETTINGS.poll_interval_seconds,
        },
    },
    "retention-cleanup-daily": {
        "task": "worker.tasks.retention_cleanup",
        "schedule": crontab(minute=0, hour=CELERY_SETTINGS.retention_run_hour),
        "kwargs": {"retention_days": CELERY_SETTINGS.retention_days},
        "options": {"queue": CELERY_SETTINGS.maintenance_queue},
    },
}

app.autodiscover_tasks(["worker"])
