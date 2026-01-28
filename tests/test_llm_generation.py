from mp_reviews_bot.llm import generate as llm_generate


def test_llm_generation_returns_confidence_and_conflict_flag():
    event = {
        "id": "evt-2",
        "text": "Вопрос по размеру",
        "type": "question",
    }
    kb_rules = [
        {"sku": "SKU-1", "text": "Таблица размеров в карточке товара"},
    ]

    response = llm_generate.generate_response(event=event, kb_rules=kb_rules)

    assert response.text
    assert 0 <= response.confidence <= 100
    assert response.conflict is False


def test_llm_generation_marks_conflict():
    event = {
        "id": "evt-3",
        "text": "Есть ли гарантия?",
        "type": "question",
    }
    kb_rules = [
        {"sku": "SKU-2", "text": "Гарантия 1 год"},
        {"sku": "SKU-2", "text": "Гарантия 6 месяцев"},
    ]

    response = llm_generate.generate_response(event=event, kb_rules=kb_rules)

    assert response.conflict is True
    assert response.text
    assert 0 <= response.confidence <= 100
