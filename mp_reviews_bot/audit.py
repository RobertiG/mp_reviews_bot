from __future__ import annotations

from typing import Any, Mapping

from mp_reviews_bot.db import SessionLocal
from mp_reviews_bot.models import AuditLog, AuditStatus


def record_audit_log(
    *,
    sender_id: str,
    prompt: str | None = None,
    model: str | None = None,
    model_version: str | None = None,
    kb_rules: Mapping[str, Any] | None = None,
    raw_payload: Mapping[str, Any] | None = None,
    status: AuditStatus = AuditStatus.NEW,
) -> AuditLog:
    entry = AuditLog(
        sender_id=sender_id,
        prompt=prompt,
        model=model,
        model_version=model_version,
        kb_rules=dict(kb_rules) if kb_rules is not None else None,
        raw_payload=dict(raw_payload) if raw_payload is not None else None,
        status=status,
    )
    with SessionLocal() as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)
    return entry
