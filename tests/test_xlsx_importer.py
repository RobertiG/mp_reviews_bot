from datetime import timedelta
from io import BytesIO

from openpyxl import Workbook
import pytest

from mp_reviews_bot.xlsx_importer import (
    DEFAULT_SHEET_NAME,
    DEFAULT_XLSX_HEADERS,
    SkuXlsxImporter,
    UploadRateLimiter,
)


def _build_workbook(rows, sheet_name=DEFAULT_SHEET_NAME):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(row)
    data = BytesIO()
    workbook.save(data)
    return data.getvalue()


def test_importer_parses_valid_rows_and_rebinds():
    file_bytes = _build_workbook(
        [
            DEFAULT_XLSX_HEADERS,
            ["WB", "sku-1", "100", "internal-1", "Name"],
            ["OZON", "sku-2", "200", "internal-2", None],
        ]
    )
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
    )
    result = importer.import_xlsx(
        file_bytes,
        existing_internal_by_seller={("WB", "sku-1"): "old"},
    )

    assert len(result.valid_rows) == 2
    assert result.rebinds[0].old_internal_sku == "old"
    assert result.rebinds[0].new_internal_sku == "internal-1"


def test_importer_collects_invalid_rows():
    file_bytes = _build_workbook(
        [
            DEFAULT_XLSX_HEADERS,
            ["", "sku-1", None, None, None],
        ]
    )
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
    )
    result = importer.import_xlsx(file_bytes)

    assert len(result.invalid_rows) == 1
    assert result.invalid_rows[0].row_number == 2


def test_importer_rejects_wrong_headers():
    file_bytes = _build_workbook([["wrong", "header"]])
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
    )
    with pytest.raises(ValueError, match="XLSX headers must match template"):
        importer.import_xlsx(file_bytes)


def test_importer_rejects_extra_columns():
    file_bytes = _build_workbook([list(DEFAULT_XLSX_HEADERS) + ["extra"]])
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
    )
    with pytest.raises(ValueError, match="unexpected extra columns"):
        importer.import_xlsx(file_bytes)


def test_importer_requires_sheet_name():
    file_bytes = _build_workbook([DEFAULT_XLSX_HEADERS], sheet_name="OTHER")
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
    )
    with pytest.raises(ValueError, match="missing sheet"):
        importer.import_xlsx(file_bytes)


def test_importer_enforces_size_limit():
    file_bytes = _build_workbook([DEFAULT_XLSX_HEADERS])
    importer = SkuXlsxImporter(max_file_size_bytes=1, timeout_seconds=5)
    with pytest.raises(ValueError, match="exceeds size limit"):
        importer.import_xlsx(file_bytes)


def test_importer_rate_limits_uploads():
    file_bytes = _build_workbook([DEFAULT_XLSX_HEADERS])
    limiter = UploadRateLimiter(window=timedelta(seconds=30), max_uploads=1)
    importer = SkuXlsxImporter(
        max_file_size_bytes=1024 * 1024,
        timeout_seconds=5,
        rate_limiter=limiter,
    )
    importer.import_xlsx(file_bytes, rate_limit_key="project-1")
    with pytest.raises(ValueError, match="rate limit"):
        importer.import_xlsx(file_bytes, rate_limit_key="project-1")
