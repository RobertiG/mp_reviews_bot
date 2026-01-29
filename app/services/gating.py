from app import models


def is_balance_positive(balance: models.Balance) -> bool:
    return balance.tokens > 0


def can_autosend(event: models.Event) -> bool:
    return not event.conflict and (event.confidence or 0) >= 50
