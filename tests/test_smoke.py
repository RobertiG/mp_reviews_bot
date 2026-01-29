from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db


def override_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_project_create_and_event_flow():
    project = client.post("/projects", json={"name": "Demo", "owner_id": 1}).json()
    assert project["name"] == "Demo"

    cabinet = client.post(
        "/cabinets",
        json={"project_id": project["id"], "marketplace": "WB", "name": "Cab", "api_token": "token"},
    ).json()
    assert cabinet["api_token_masked"]

    kb = client.post(
        "/kb",
        json={"project_id": project["id"], "internal_sku": "SKU1", "text": "Fact"},
    ).json()
    assert kb["text"] == "Fact"

    event = client.post(
        "/events",
        json={
            "project_id": project["id"],
            "cabinet_id": cabinet["id"],
            "marketplace": "WB",
            "marketplace_event_id": "evt-1",
            "event_type": "review",
            "text": "Great",
            "rating": 5,
            "sentiment": "positive",
            "internal_sku": "SKU1",
            "raw_payload": {"id": "evt-1"},
            "media_links": [],
        },
    ).json()
    assert event["status"] == "new"

    approve = client.post(f"/events/{event['id']}/approve").json()
    assert approve["status"] == "approved"
