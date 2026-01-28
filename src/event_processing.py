from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .billing import BalanceBlockedError
from .models import OwnerAccount, ReplenishmentPolicy


class EventProcessingBlockedError(RuntimeError):
    def __init__(self, owner_id: str) -> None:
        super().__init__(f"Owner {owner_id} balance is zero, event processing blocked")
        self.owner_id = owner_id


@dataclass(frozen=True)
class EventWindow:
    start_time: Optional[datetime]
    include_backlog: bool


class EventProcessingPolicy:
    @staticmethod
    def guard_parsing(owner: OwnerAccount) -> None:
        if owner.balance_tokens <= 0:
            raise EventProcessingBlockedError(owner.owner_id)

    @staticmethod
    def guard_generation(owner: OwnerAccount) -> None:
        if owner.balance_tokens <= 0:
            raise BalanceBlockedError(owner.owner_id)

    @staticmethod
    def window_after_replenishment(owner: OwnerAccount) -> EventWindow:
        replenished_at = owner.last_replenished_at
        if owner.replenishment_policy == ReplenishmentPolicy.PROCESS_BACKLOG:
            return EventWindow(start_time=None, include_backlog=True)
        return EventWindow(start_time=replenished_at, include_backlog=False)
