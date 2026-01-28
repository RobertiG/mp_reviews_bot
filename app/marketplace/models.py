from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


RawPayload = Mapping[str, Any]


@dataclass(frozen=True)
class MarketplaceReview:
    marketplace_review_id: str
    text: str
    rating: int | None
    created_at: datetime | None
    sku: str | None
    raw_payload: RawPayload


@dataclass(frozen=True)
class MarketplaceQuestion:
    marketplace_question_id: str
    text: str
    created_at: datetime | None
    sku: str | None
    raw_payload: RawPayload


@dataclass(frozen=True)
class MarketplaceActionResult:
    success: bool
    external_id: str | None
    raw_request: RawPayload
    raw_response: RawPayload
