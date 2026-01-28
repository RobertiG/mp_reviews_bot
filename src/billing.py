from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Protocol
from uuid import uuid4

from .models import LedgerEntry, LedgerReason, OwnerAccount, ReplenishmentPolicy


class InsufficientBalanceError(RuntimeError):
    def __init__(self, owner_id: str, requested: int, available: int) -> None:
        super().__init__(
            f"Owner {owner_id} has insufficient balance: requested={requested}, available={available}"
        )
        self.owner_id = owner_id
        self.requested = requested
        self.available = available


class BalanceBlockedError(RuntimeError):
    def __init__(self, owner_id: str) -> None:
        super().__init__(f"Owner {owner_id} balance is zero, operations blocked")
        self.owner_id = owner_id


class OwnerRepository(Protocol):
    def get(self, owner_id: str) -> OwnerAccount:
        ...

    def save(self, owner: OwnerAccount) -> None:
        ...


class LedgerRepository(Protocol):
    def append(self, entry: LedgerEntry) -> None:
        ...

    def list_for_owner(self, owner_id: str) -> Iterable[LedgerEntry]:
        ...


class InMemoryOwnerRepository:
    def __init__(self, owners: Optional[Dict[str, OwnerAccount]] = None) -> None:
        self._owners = owners if owners is not None else {}

    def get(self, owner_id: str) -> OwnerAccount:
        if owner_id not in self._owners:
            raise KeyError(f"Owner {owner_id} not found")
        return self._owners[owner_id]

    def save(self, owner: OwnerAccount) -> None:
        self._owners[owner.owner_id] = owner


class InMemoryLedgerRepository:
    def __init__(self, entries: Optional[List[LedgerEntry]] = None) -> None:
        self._entries = entries if entries is not None else []

    def append(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def list_for_owner(self, owner_id: str) -> Iterable[LedgerEntry]:
        return tuple(entry for entry in self._entries if entry.owner_id == owner_id)


class BillingService:
    def __init__(self, owners: OwnerRepository, ledger: LedgerRepository) -> None:
        self._owners = owners
        self._ledger = ledger

    def debit_tokens(
        self,
        owner_id: str,
        amount: int,
        *,
        reason: LedgerReason,
        metadata: Optional[dict[str, str]] = None,
        now: Optional[datetime] = None,
    ) -> OwnerAccount:
        if amount <= 0:
            raise ValueError("amount must be positive")

        owner = self._owners.get(owner_id)
        if owner.balance_tokens <= 0:
            raise BalanceBlockedError(owner.owner_id)
        if owner.balance_tokens < amount:
            raise InsufficientBalanceError(owner.owner_id, amount, owner.balance_tokens)

        new_balance = owner.balance_tokens - amount
        updated_at = now or datetime.now(timezone.utc)
        updated_owner = replace(owner, balance_tokens=new_balance, updated_at=updated_at)
        self._owners.save(updated_owner)
        self._ledger.append(
            LedgerEntry(
                entry_id=str(uuid4()),
                owner_id=owner.owner_id,
                delta=-amount,
                reason=reason,
                metadata=metadata or {},
                balance_before=owner.balance_tokens,
                balance_after=new_balance,
            )
        )
        return updated_owner

    def top_up(
        self,
        owner_id: str,
        amount: int,
        *,
        policy: Optional[ReplenishmentPolicy] = None,
        metadata: Optional[dict[str, str]] = None,
        now: Optional[datetime] = None,
    ) -> OwnerAccount:
        if amount <= 0:
            raise ValueError("amount must be positive")

        owner = self._owners.get(owner_id)
        new_balance = owner.balance_tokens + amount
        updated_at = now or datetime.now(timezone.utc)
        updated_owner = replace(
            owner,
            balance_tokens=new_balance,
            replenishment_policy=policy or owner.replenishment_policy,
            last_replenished_at=updated_at,
            updated_at=updated_at,
        )
        self._owners.save(updated_owner)
        self._ledger.append(
            LedgerEntry(
                entry_id=str(uuid4()),
                owner_id=owner.owner_id,
                delta=amount,
                reason=LedgerReason.TOP_UP,
                metadata=metadata or {},
                balance_before=owner.balance_tokens,
                balance_after=new_balance,
            )
        )
        return updated_owner
