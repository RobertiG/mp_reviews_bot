from mp_reviews_bot.events import ingest as ingest_module


def test_event_ingest_normalizes_fields_and_raw_payload():
    payload = {
        "id": "evt-1",
        "type": "review",
        "text": "Great product",
        "rating": 5,
        "sku": "SKU-1",
        "created_at": "2024-01-10T10:00:00Z",
    }

    event = ingest_module.ingest_event(payload)

    assert event.id == "evt-1"
    assert event.type == "review"
    assert event.text == "Great product"
    assert event.rating == 5
    assert event.sku == "SKU-1"
    assert event.status == "new"
    assert event.raw_payload == payload
