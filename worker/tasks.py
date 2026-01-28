from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from celery import Task

from worker.celery_app import app

logger = logging.getLogger(__name__)


class BaseTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_jitter = True
    retry_kwargs = {"max_retries": 5}
    default_retry_delay = 5

    def on_failure(  # type: ignore[override]
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        logger.exception(
            "Task %s failed: %s | args=%s kwargs=%s", self.name, exc, args, kwargs
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(  # type: ignore[override]
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        logger.warning(
            "Task %s retrying after error: %s | args=%s kwargs=%s",
            self.name,
            exc,
            args,
            kwargs,
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


@app.task(bind=True, base=BaseTask, name="worker.tasks.poll_wb_ozon")
def poll_wb_ozon(self: BaseTask, *, project_ids: Iterable[str] | None = None) -> int:
    logger.info("Polling WB/Ozon events. project_ids=%s", project_ids)
    # TODO: call WB/Ozon APIs, normalize payloads, and enqueue ingest_events
    return 0


@app.task(bind=True, base=BaseTask, name="worker.tasks.ingest_events")
def ingest_events(self: BaseTask, *, events: list[dict[str, Any]]) -> int:
    logger.info("Ingesting %d events", len(events))
    # TODO: persist normalized events + raw payload, de-duplicate by marketplace event ID
    return len(events)


@app.task(bind=True, base=BaseTask, name="worker.tasks.generate_llm_response")
def generate_llm_response(
    self: BaseTask, *, event_id: str, project_id: str
) -> dict[str, Any]:
    logger.info(
        "Generating LLM response for event_id=%s project_id=%s",
        event_id,
        project_id,
    )
    # TODO: load KB context, invoke LLM, store draft + confidence
    return {"event_id": event_id, "status": "drafted"}


@app.task(bind=True, base=BaseTask, name="worker.tasks.auto_send_response")
def auto_send_response(
    self: BaseTask, *, event_id: str, project_id: str, response_text: str
) -> dict[str, Any]:
    logger.info(
        "Auto-sending response for event_id=%s project_id=%s", event_id, project_id
    )
    # TODO: send response to marketplace, update status/audit log
    return {"event_id": event_id, "status": "sent"}


@app.task(bind=True, base=BaseTask, name="worker.tasks.import_sku_xlsx")
def import_sku_xlsx(
    self: BaseTask, *, project_id: str, file_path: str
) -> dict[str, Any]:
    logger.info(
        "Importing SKU mapping for project_id=%s file_path=%s",
        project_id,
        file_path,
    )
    # TODO: parse XLSX, validate rows, apply mappings, log invalid rows
    return {"project_id": project_id, "status": "imported"}


@app.task(bind=True, base=BaseTask, name="worker.tasks.retention_cleanup")
def retention_cleanup(self: BaseTask, *, retention_days: int = 90) -> dict[str, Any]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    logger.info("Running retention cleanup for audit/logs older than %s", cutoff.isoformat())
    # TODO: delete audit/log records older than cutoff
    return {"status": "completed", "cutoff": cutoff.isoformat()}
