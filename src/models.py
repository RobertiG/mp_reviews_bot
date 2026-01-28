from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional


class LedgerReason(str, Enum):
    GENERATION = "generation"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    TOP_UP = "top_up"


class ReplenishmentPolicy(str, Enum):
    PROCESS_BACKLOG = "process_backlog"
    ONLY_NEW = "only_new"


@dataclass(frozen=True)
class OwnerAccount:
    owner_id: str
    balance_tokens: int = 0
    replenishment_policy: ReplenishmentPolicy = ReplenishmentPolicy.PROCESS_BACKLOG
    last_replenished_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_blocked(self) -> bool:
        return self.balance_tokens <= 0


@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    owner_id: str
    delta: int
    reason: LedgerReason
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)
    balance_before: Optional[int] = None
    balance_after: Optional[int] = None
