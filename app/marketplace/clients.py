from __future__ import annotations

from datetime import datetime

from app.marketplace.base import MarketplaceClient
from app.marketplace.models import (
    MarketplaceActionResult,
    MarketplaceQuestion,
    MarketplaceReview,
)


class WBClient(MarketplaceClient):
    """Wildberries marketplace client stub."""

    def fetch_reviews(self, *, since: datetime | None = None) -> list[MarketplaceReview]:
        raise NotImplementedError("WBClient.fetch_reviews is not implemented yet")

    def fetch_questions(
        self, *, since: datetime | None = None
    ) -> list[MarketplaceQuestion]:
        raise NotImplementedError("WBClient.fetch_questions is not implemented yet")

    def send_review_answer(
        self, *, review_id: str, text: str
    ) -> MarketplaceActionResult:
        raise NotImplementedError("WBClient.send_review_answer is not implemented yet")

    def send_question_answer(
        self, *, question_id: str, text: str
    ) -> MarketplaceActionResult:
        raise NotImplementedError("WBClient.send_question_answer is not implemented yet")


class OzonClient(MarketplaceClient):
    """Ozon marketplace client stub."""

    def fetch_reviews(self, *, since: datetime | None = None) -> list[MarketplaceReview]:
        raise NotImplementedError("OzonClient.fetch_reviews is not implemented yet")

    def fetch_questions(
        self, *, since: datetime | None = None
    ) -> list[MarketplaceQuestion]:
        raise NotImplementedError("OzonClient.fetch_questions is not implemented yet")

    def send_review_answer(
        self, *, review_id: str, text: str
    ) -> MarketplaceActionResult:
        raise NotImplementedError("OzonClient.send_review_answer is not implemented yet")

    def send_question_answer(
        self, *, question_id: str, text: str
    ) -> MarketplaceActionResult:
        raise NotImplementedError("OzonClient.send_question_answer is not implemented yet")
