from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db import Base


class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class EventStatusEnum(str, Enum):
    new = "new"
    drafted = "drafted"
    approved = "approved"
    sent = "sent"
    escalated = "escalated"
    error = "error"


class MarketplaceEnum(str, Enum):
    wb = "WB"
    ozon = "OZON"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)
    is_owner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Cabinet(Base):
    __tablename__ = "cabinets"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    marketplace = Column(String, nullable=False)
    name = Column(String, nullable=False)
    api_token_encrypted = Column(Text, nullable=False)
    api_token_masked = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SKUMap(Base):
    __tablename__ = "sku_maps"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    marketplace = Column(String, nullable=False)
    seller_sku = Column(String, nullable=False)
    marketplace_item_id = Column(String, nullable=False)
    internal_sku = Column(String, nullable=False)
    product_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class KBRule(Base):
    __tablename__ = "kb_rules"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    internal_sku = Column(String, nullable=True)
    rule_type = Column(String, default="fact")
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)
    marketplace = Column(String, nullable=False)
    marketplace_event_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    sentiment = Column(String, nullable=True)
    internal_sku = Column(String, nullable=False)
    status = Column(String, default="new")
    raw_payload = Column(JSON, nullable=False)
    media_links = Column(JSON, nullable=True)
    suggested_reply = Column(Text, nullable=True)
    confidence = Column(Integer, nullable=True)
    kb_rule_ids = Column(JSON, nullable=True)
    conflict = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ProjectSettings(Base):
    __tablename__ = "project_settings"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    autogen_positive = Column(Boolean, default=False)
    autosend_positive = Column(Boolean, default=False)
    autogen_negative = Column(Boolean, default=False)
    autosend_negative = Column(Boolean, default=False)
    autogen_questions = Column(Boolean, default=False)
    autosend_questions = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tokens = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TokenLedger(Base):
    __tablename__ = "token_ledger"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delta = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    prompt = Column(Text, nullable=True)
    model = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    kb_rule_ids = Column(JSON, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
