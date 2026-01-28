from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "audit"):
            log_record["audit"] = record.audit
        if hasattr(record, "context"):
            log_record["context"] = record.context
        return json.dumps(log_record, ensure_ascii=False, default=str)


class AuditLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("audit", self.extra)
        return msg, kwargs


def bind_audit_logger(logger: logging.Logger, audit: Mapping[str, Any]) -> AuditLoggerAdapter:
    return AuditLoggerAdapter(logger, dict(audit))


def setup_structured_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
