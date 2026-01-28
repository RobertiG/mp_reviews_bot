import datetime as dt

import openpyxl

from mp_reviews_bot.importers import xlsx as xlsx_importer


def test_import_xlsx_reads_kb_rules(tmp_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["level", "sku", "type", "text", "created_at"])
    sheet.append(["project", "", "fact", "Общее правило", "2024-01-01"])
    sheet.append(["sku", "SKU-1", "fact", "Правило по SKU", "2024-02-01"])

    file_path = tmp_path / "kb.xlsx"
    workbook.save(file_path)

    rows = xlsx_importer.import_xlsx(file_path)

    assert isinstance(rows, list)
    assert len(rows) == 2

    first = rows[0]
    second = rows[1]

    assert first["level"] == "project"
    assert first["sku"] in ("", None)
    assert first["type"] == "fact"
    assert first["text"] == "Общее правило"
    assert first["created_at"] == dt.date(2024, 1, 1)

    assert second["level"] == "sku"
    assert second["sku"] == "SKU-1"
    assert second["type"] == "fact"
    assert second["text"] == "Правило по SKU"
    assert second["created_at"] == dt.date(2024, 2, 1)
