from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db import get_db

router = APIRouter(prefix="/bot", tags=["bot"])


def _get_user(db: Session, tg_user_id: int):
    return crud.get_or_create_user(db, str(tg_user_id))


def _get_project(db: Session, project_id: int, user_id: int):
    project = crud.get_project_for_user(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/profile/{tg_user_id}", response_model=schemas.ProfileOut)
def profile(tg_user_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    return {
        "user_id": user.id,
        "telegram_user_id": user.telegram_user_id,
        "is_admin": user.is_owner,
    }


@router.get("/projects/{tg_user_id}", response_model=list[schemas.ProjectOut])
def list_projects(tg_user_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    return crud.list_projects_for_user(db, user.id)


@router.get("/projects/{tg_user_id}/{project_id}/dashboard", response_model=schemas.DashboardOut)
def project_dashboard(tg_user_id: int, project_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    counts = crud.count_event_statuses(db, project_id)
    balance = crud.get_balance(db, user.id)
    return {
        "new": counts["new"],
        "without_answer": counts["without_answer"],
        "escalated": counts["escalated"],
        "balance_tokens": balance.tokens,
    }


@router.get("/projects/{tg_user_id}/{project_id}/feed", response_model=schemas.FeedOut)
def project_feed(
    tg_user_id: int,
    project_id: int,
    status: str | None = None,
    sentiment: str | None = None,
    internal_sku: str | None = None,
    limit: int = 10,
    offset: int = 0,
    without_answer: bool = False,
    db: Session = Depends(get_db),
):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    if without_answer:
        status_filter = ["new", "drafted", "approved"]
        events = crud.list_events(
            db,
            project_id,
            status=status_filter,
            sentiment=sentiment,
            internal_sku=internal_sku,
            limit=limit,
            offset=offset,
        )
        total = crud.count_events(
            db,
            project_id,
            status=status_filter,
            sentiment=sentiment,
            internal_sku=internal_sku,
        )
    else:
        events = crud.list_events(
            db,
            project_id,
            status=status,
            sentiment=sentiment,
            internal_sku=internal_sku,
            limit=limit,
            offset=offset,
        )
        total = crud.count_events(
            db,
            project_id,
            status=status,
            sentiment=sentiment,
            internal_sku=internal_sku,
        )
    return {
        "items": events,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/events/{tg_user_id}/{event_id}", response_model=schemas.EventDetailOut)
def event_detail(tg_user_id: int, event_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    _get_project(db, event.project_id, user.id)
    kb_sources = []
    if event.kb_rule_ids:
        rules = crud.list_kb_rules_by_ids(db, list(event.kb_rule_ids))
        kb_sources = [rule.text for rule in rules]
    payload = schemas.EventOut.model_validate(event).model_dump()
    payload["kb_sources"] = kb_sources
    return payload


@router.get("/projects/{tg_user_id}/{project_id}/kb", response_model=list[schemas.KBRuleOut])
def list_kb_rules(
    tg_user_id: int,
    project_id: int,
    scope: str | None = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    rules = crud.list_kb_rules(db, project_id)
    if scope == "project":
        rules = [rule for rule in rules if not rule.internal_sku]
    if scope == "sku":
        rules = [rule for rule in rules if rule.internal_sku]
    rules = sorted(rules, key=lambda item: item.created_at, reverse=True)
    return rules[:limit]


@router.post("/projects/{tg_user_id}/{project_id}/kb", response_model=schemas.KBRuleOut)
def create_kb_rule(
    tg_user_id: int,
    project_id: int,
    payload: schemas.KBRuleCreate,
    db: Session = Depends(get_db),
):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    if payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project mismatch")
    return crud.create_kb_rule(db, payload.project_id, payload.internal_sku, payload.text)


@router.delete("/kb/{tg_user_id}/{rule_id}")
def delete_kb_rule(tg_user_id: int, rule_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    rule = db.get(models.KBRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    _get_project(db, rule.project_id, user.id)
    deleted = crud.delete_kb_rule(db, rule_id)
    return {"deleted": bool(deleted)}


@router.get("/projects/{tg_user_id}/{project_id}/cabinets", response_model=list[schemas.CabinetOut])
def list_cabinets(tg_user_id: int, project_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    return crud.list_cabinets(db, project_id)


@router.get("/projects/{tg_user_id}/{project_id}/onboarding", response_model=schemas.OnboardingOut)
def onboarding_state(tg_user_id: int, project_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    cabinets = crud.list_cabinets(db, project_id)
    return {
        "has_cabinets": bool(cabinets),
        "cabinets_count": len(cabinets),
    }


@router.get("/projects/{tg_user_id}/{project_id}/settings", response_model=schemas.SettingsOut)
def project_settings(tg_user_id: int, project_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    return crud.get_settings(db, project_id)


@router.get("/projects/{tg_user_id}/{project_id}/balance", response_model=schemas.BalanceDetailOut)
def project_balance(tg_user_id: int, project_id: int, db: Session = Depends(get_db)):
    user = _get_user(db, tg_user_id)
    _get_project(db, project_id, user.id)
    balance = crud.get_balance(db, user.id)
    ledger = crud.list_token_ledger(db, user.id)
    return {
        "owner_id": balance.owner_id,
        "tokens": balance.tokens,
        "ledger": ledger,
    }
