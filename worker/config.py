from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CelerySettings:
    broker_url: str
    result_backend: str
    poll_interval_seconds: int = 60
    retention_days: int = 90
    retention_run_hour: int = 3
    timezone: str = "UTC"
    enable_utc: bool = True
    task_default_queue: str = "mp_reviews"
    polling_queue: str = "mp_reviews.polling"
    ingest_queue: str = "mp_reviews.ingest"
    llm_queue: str = "mp_reviews.llm"
    autosend_queue: str = "mp_reviews.autosend"
    import_queue: str = "mp_reviews.import"
    maintenance_queue: str = "mp_reviews.maintenance"
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 1
    task_track_started: bool = True
    broker_connection_retry_on_startup: bool = True

    @staticmethod
    def from_env() -> "CelerySettings":
        broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)
        poll_interval_seconds = int(os.getenv("CELERY_POLL_INTERVAL_SECONDS", "60"))
        retention_days = int(os.getenv("CELERY_RETENTION_DAYS", "90"))
        retention_run_hour = int(os.getenv("CELERY_RETENTION_RUN_HOUR", "3"))
        return CelerySettings(
            broker_url=broker_url,
            result_backend=result_backend,
            poll_interval_seconds=poll_interval_seconds,
            retention_days=retention_days,
            retention_run_hour=retention_run_hour,
        )


CELERY_SETTINGS = CelerySettings.from_env()
