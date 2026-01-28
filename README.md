# mp_reviews_bot

## Audit logging

The audit log table is defined in `mp_reviews_bot.models.AuditLog` and captures sender, prompt/model/version,
KB rule references, raw payload, and processing status. Use `mp_reviews_bot.audit.record_audit_log` to persist
entries when responses are generated or sent.

Structured logging can be enabled via `mp_reviews_bot.logging.setup_structured_logging()` to emit JSON log lines
with optional audit metadata under the `audit` key.

## Retention

Celery task `audit.purge_old_logs` deletes audit log entries older than 90 days (configurable via
`AUDIT_RETENTION_DAYS`) and is scheduled daily at 03:00 UTC via Celery beat (override with
`CELERY_TIMEZONE`).
