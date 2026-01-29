from dataclasses import dataclass
from datetime import datetime


@dataclass
class Approval:
    id: str
    status: str
    approved_by: str
    approved_at: datetime


def approve_draft(draft_id: str, approver_id: str) -> Approval:
    return Approval(
        id=draft_id,
        status="approved",
        approved_by=approver_id,
        approved_at=datetime.utcnow(),
    )
