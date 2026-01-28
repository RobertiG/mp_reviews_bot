from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.marketplace.models import (
    MarketplaceActionResult,
    MarketplaceQuestion,
    MarketplaceReview,
)


class MarketplaceClient(ABC):
    """Base interface for marketplace integrations."""

    @abstractmethod
    def fetch_reviews(self, *, since: datetime | None = None) -> list[MarketplaceReview]:
        """Return normalized reviews with raw payloads included."""

    @abstractmethod
    def fetch_questions(
        self, *, since: datetime | None = None
    ) -> list[MarketplaceQuestion]:
        """Return normalized questions with raw payloads included."""

    @abstractmethod
    def send_review_answer(
        self, *, review_id: str, text: str
    ) -> MarketplaceActionResult:
        """Send an answer to a review and return raw request/response data."""

    @abstractmethod
    def send_question_answer(
        self, *, question_id: str, text: str
    ) -> MarketplaceActionResult:
        """Send an answer to a question and return raw request/response data."""
