from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class IngestedEvent:
    id: str
    type: str
    text: str
    rating: int | None
    sku: str
    status: str
    raw_payload: Dict[str, Any]


def ingest_event(payload: Dict[str, Any]) -> IngestedEvent:
    return IngestedEvent(
        id=str(payload.get("id")),
        type=str(payload.get("type")),
        text=str(payload.get("text")),
        rating=payload.get("rating"),
        sku=str(payload.get("sku")),
        status="new",
        raw_payload=payload,
    )
