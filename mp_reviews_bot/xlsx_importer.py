from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from io import BytesIO
import time
from typing import Iterable, Sequence

from openpyxl import load_workbook

DEFAULT_SHEET_NAME = "SKU_MAPPING"
DEFAULT_XLSX_HEADERS = (
    "marketplace",
    "seller_sku",
    "marketplace_item_id",
    "internal_sku",
    "product_name",
)
DEFAULT_ALLOWED_MARKETPLACES = {"WB", "OZON"}


@dataclass(frozen=True)
class SkuMappingRow:
    marketplace: str
    seller_sku: str
    marketplace_item_id: str | None
    internal_sku: str | None
    product_name: str | None


@dataclass(frozen=True)
class InvalidRow:
    row_number: int
    reason: str
    raw_values: tuple


@dataclass(frozen=True)
class SkuRebindAction:
    marketplace: str
    seller_sku: str
    old_internal_sku: str | None
    new_internal_sku: str


@dataclass
class SkuImportResult:
    valid_rows: list[SkuMappingRow] = field(default_factory=list)
    invalid_rows: list[InvalidRow] = field(default_factory=list)
    rebinds: list[SkuRebindAction] = field(default_factory=list)


class UploadRateLimiter:
    def __init__(self, window: timedelta, max_uploads: int) -> None:
        if max_uploads < 1:
            raise ValueError("max_uploads must be >= 1")
        if window.total_seconds() <= 0:
            raise ValueError("window must be positive")
        self._window_seconds = window.total_seconds()
        self._max_uploads = max_uploads
        self._events: dict[str, list[float]] = {}

    def check_and_record(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - self._window_seconds
        timestamps = self._events.get(key, [])
        timestamps = [ts for ts in timestamps if ts >= window_start]
        if len(timestamps) >= self._max_uploads:
            raise ValueError("Upload rate limit exceeded")
        timestamps.append(now)
        self._events[key] = timestamps


class SkuXlsxImporter:
    def __init__(
        self,
        *,
        max_file_size_bytes: int,
        timeout_seconds: float,
        rate_limiter: UploadRateLimiter | None = None,
        sheet_name: str = DEFAULT_SHEET_NAME,
        headers: Sequence[str] = DEFAULT_XLSX_HEADERS,
        allowed_marketplaces: Iterable[str] = DEFAULT_ALLOWED_MARKETPLACES,
    ) -> None:
        if max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._max_file_size_bytes = max_file_size_bytes
        self._timeout_seconds = timeout_seconds
        self._rate_limiter = rate_limiter
        self._sheet_name = sheet_name
        self._headers = tuple(headers)
        self._allowed_marketplaces = {value.upper() for value in allowed_marketplaces}

    def import_xlsx(
        self,
        file_bytes: bytes,
        *,
        rate_limit_key: str | None = None,
        existing_internal_by_seller: dict[tuple[str, str], str] | None = None,
    ) -> SkuImportResult:
        if len(file_bytes) > self._max_file_size_bytes:
            raise ValueError("XLSX file exceeds size limit")
        if self._rate_limiter is not None and rate_limit_key is not None:
            self._rate_limiter.check_and_record(rate_limit_key)

        start = time.monotonic()
        workbook = load_workbook(BytesIO(file_bytes), read_only=True, data_only=True)
        try:
            if time.monotonic() - start > self._timeout_seconds:
                raise TimeoutError("XLSX parsing timeout exceeded")
            if self._sheet_name not in workbook.sheetnames:
                raise ValueError(f"XLSX is missing sheet '{self._sheet_name}'")
            sheet = workbook[self._sheet_name]
            result = self._parse_sheet(sheet, existing_internal_by_seller, start)
            elapsed = time.monotonic() - start
            if elapsed > self._timeout_seconds:
                raise TimeoutError("XLSX parsing timeout exceeded")
            return result
        finally:
            workbook.close()

    def _parse_sheet(self, sheet, existing_internal_by_seller, start_time: float):
        rows = sheet.iter_rows(values_only=True)
        header_row = next(rows, None)
        if header_row is None:
            raise ValueError("XLSX is missing header row")
        normalized_header = tuple(
            str(value).strip() if value is not None else "" for value in header_row
        )
        if normalized_header[: len(self._headers)] != self._headers:
            raise ValueError(
                "XLSX headers must match template: "
                + ", ".join(self._headers)
            )
        extra_headers = normalized_header[len(self._headers) :]
        if any(value for value in extra_headers):
            raise ValueError("XLSX contains unexpected extra columns")

        result = SkuImportResult()
        existing_internal_by_seller = existing_internal_by_seller or {}

        for index, row in enumerate(rows, start=2):
            if time.monotonic() - start_time > self._timeout_seconds:
                raise TimeoutError("XLSX parsing timeout exceeded")
            row_values = tuple(row)
            parsed = self._parse_row(row_values, index)
            if isinstance(parsed, InvalidRow):
                result.invalid_rows.append(parsed)
                continue
            result.valid_rows.append(parsed)
            key = (parsed.marketplace, parsed.seller_sku)
            if parsed.internal_sku:
                previous = existing_internal_by_seller.get(key)
                if previous != parsed.internal_sku:
                    result.rebinds.append(
                        SkuRebindAction(
                            marketplace=parsed.marketplace,
                            seller_sku=parsed.seller_sku,
                            old_internal_sku=previous,
                            new_internal_sku=parsed.internal_sku,
                        )
                    )
                    existing_internal_by_seller[key] = parsed.internal_sku

        return result

    def _parse_row(self, values: tuple, row_number: int) -> SkuMappingRow | InvalidRow:
        values = values + (None,) * (len(self._headers) - len(values))
        marketplace = self._normalize_str(values[0])
        seller_sku = self._normalize_str(values[1])
        marketplace_item_id = self._normalize_optional(values[2])
        internal_sku = self._normalize_optional(values[3])
        product_name = self._normalize_optional(values[4])

        if not marketplace:
            return InvalidRow(row_number, "Missing marketplace", values)
        if marketplace not in self._allowed_marketplaces:
            return InvalidRow(row_number, "Unknown marketplace", values)
        if not seller_sku:
            return InvalidRow(row_number, "Missing seller_sku", values)

        return SkuMappingRow(
            marketplace=marketplace,
            seller_sku=seller_sku,
            marketplace_item_id=marketplace_item_id,
            internal_sku=internal_sku,
            product_name=product_name,
        )

    @staticmethod
    def _normalize_str(value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _normalize_optional(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
