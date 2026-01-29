from datetime import datetime
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from app import models
from app.security import encrypt_token, mask_token


def create_project(db: Session, name: str, owner_id: int) -> models.Project:
    project = models.Project(name=name, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session):
    return db.scalars(select(models.Project)).all()


def get_or_create_user(db: Session, telegram_user_id: str) -> models.User:
    user = db.scalars(
        select(models.User).where(models.User.telegram_user_id == telegram_user_id)
    ).first()
    if user:
        return user
    user = models.User(telegram_user_id=telegram_user_id, is_owner=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_projects_for_user(db: Session, user_id: int):
    stmt = (
        select(models.Project)
        .outerjoin(
            models.ProjectMember,
            models.ProjectMember.project_id == models.Project.id,
        )
        .where(or_(models.Project.owner_id == user_id, models.ProjectMember.user_id == user_id))
        .distinct()
    )
    return db.scalars(stmt).all()


def get_project_for_user(db: Session, project_id: int, user_id: int) -> models.Project | None:
    stmt = (
        select(models.Project)
        .outerjoin(
            models.ProjectMember,
            models.ProjectMember.project_id == models.Project.id,
        )
        .where(models.Project.id == project_id)
        .where(or_(models.Project.owner_id == user_id, models.ProjectMember.user_id == user_id))
    )
    return db.scalars(stmt).first()


def create_cabinet(db: Session, project_id: int, marketplace: str, name: str, api_token: str):
    cabinet = models.Cabinet(
        project_id=project_id,
        marketplace=marketplace,
        name=name,
        api_token_encrypted=encrypt_token(api_token),
        api_token_masked=mask_token(api_token),
    )
    db.add(cabinet)
    db.commit()
    db.refresh(cabinet)
    return cabinet


def list_cabinets(db: Session, project_id: int):
    return db.scalars(select(models.Cabinet).where(models.Cabinet.project_id == project_id)).all()


def upsert_sku_map(db: Session, project_id: int, marketplace: str, seller_sku: str, marketplace_item_id: str, internal_sku: str, product_name: str | None):
    existing = db.scalars(
        select(models.SKUMap).where(
            models.SKUMap.project_id == project_id,
            models.SKUMap.marketplace == marketplace,
            models.SKUMap.seller_sku == seller_sku,
        )
    ).first()
    if existing:
        existing.marketplace_item_id = marketplace_item_id
        existing.internal_sku = internal_sku
        existing.product_name = product_name
        db.commit()
        db.refresh(existing)
        return existing
    record = models.SKUMap(
        project_id=project_id,
        marketplace=marketplace,
        seller_sku=seller_sku,
        marketplace_item_id=marketplace_item_id,
        internal_sku=internal_sku,
        product_name=product_name,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_sku_maps(db: Session, project_id: int):
    return db.scalars(select(models.SKUMap).where(models.SKUMap.project_id == project_id)).all()


def create_kb_rule(db: Session, project_id: int, internal_sku: str | None, text: str):
    rule = models.KBRule(project_id=project_id, internal_sku=internal_sku, text=text)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_kb_rules(db: Session, project_id: int):
    return db.scalars(select(models.KBRule).where(models.KBRule.project_id == project_id)).all()


def delete_kb_rule(db: Session, rule_id: int):
    rule = db.get(models.KBRule, rule_id)
    if rule:
        db.delete(rule)
        db.commit()
    return rule


def create_event(db: Session, data: dict):
    existing = db.scalars(
        select(models.Event).where(
            models.Event.marketplace_event_id == data["marketplace_event_id"],
            models.Event.marketplace == data["marketplace"],
            models.Event.cabinet_id == data["cabinet_id"],
        )
    ).first()
    if existing:
        return existing, False
    event = models.Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event, True


def list_events(
    db: Session,
    project_id: int,
    status: str | list[str] | None = None,
    sentiment: str | None = None,
    internal_sku: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    stmt = select(models.Event).where(models.Event.project_id == project_id)
    if status:
        if isinstance(status, list):
            stmt = stmt.where(models.Event.status.in_(status))
        else:
            stmt = stmt.where(models.Event.status == status)
    if sentiment:
        stmt = stmt.where(models.Event.sentiment == sentiment)
    if internal_sku:
        stmt = stmt.where(models.Event.internal_sku == internal_sku)
    stmt = stmt.order_by(models.Event.created_at.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


def count_events(
    db: Session,
    project_id: int,
    status: str | list[str] | None = None,
    sentiment: str | None = None,
    internal_sku: str | None = None,
) -> int:
    stmt = select(func.count(models.Event.id)).where(models.Event.project_id == project_id)
    if status:
        if isinstance(status, list):
            stmt = stmt.where(models.Event.status.in_(status))
        else:
            stmt = stmt.where(models.Event.status == status)
    if sentiment:
        stmt = stmt.where(models.Event.sentiment == sentiment)
    if internal_sku:
        stmt = stmt.where(models.Event.internal_sku == internal_sku)
    return db.scalar(stmt) or 0


def count_event_statuses(db: Session, project_id: int) -> dict:
    status_counts = db.execute(
        select(models.Event.status, func.count(models.Event.id))
        .where(models.Event.project_id == project_id)
        .group_by(models.Event.status)
    ).all()
    counts = {status: count for status, count in status_counts}
    without_answer = sum(
        counts.get(status, 0) for status in ["new", "drafted", "approved"]
    )
    return {
        "new": counts.get("new", 0),
        "without_answer": without_answer,
        "escalated": counts.get("escalated", 0),
    }


def list_kb_rules_by_ids(db: Session, rule_ids: list[int]):
    if not rule_ids:
        return []
    return db.scalars(select(models.KBRule).where(models.KBRule.id.in_(rule_ids))).all()


def list_token_ledger(db: Session, owner_id: int, limit: int = 10):
    stmt = (
        select(models.TokenLedger)
        .where(models.TokenLedger.owner_id == owner_id)
        .order_by(models.TokenLedger.created_at.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_settings(db: Session, project_id: int):
    settings = db.scalars(select(models.ProjectSettings).where(models.ProjectSettings.project_id == project_id)).first()
    if not settings:
        settings = models.ProjectSettings(project_id=project_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, project_id: int, updates: dict):
    settings = get_settings(db, project_id)
    for key, value in updates.items():
        if value is not None:
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


def get_balance(db: Session, owner_id: int):
    balance = db.scalars(select(models.Balance).where(models.Balance.owner_id == owner_id)).first()
    if not balance:
        balance = models.Balance(owner_id=owner_id, tokens=0)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return balance


def update_balance(db: Session, owner_id: int, delta: int, reason: str):
    balance = get_balance(db, owner_id)
    balance.tokens += delta
    balance.updated_at = datetime.utcnow()
    db.add(models.TokenLedger(owner_id=owner_id, delta=delta, reason=reason))
    db.commit()
    db.refresh(balance)
    return balance


def metrics(db: Session):
    projects = db.scalar(select(func.count(models.Project.id))) or 0
    events = db.scalar(select(func.count(models.Event.id))) or 0
    tokens_spent = db.scalar(select(func.sum(models.TokenLedger.delta)).where(models.TokenLedger.delta < 0)) or 0
    return {
        "projects": projects,
        "events": events,
        "tokens_spent": abs(tokens_spent),
    }
