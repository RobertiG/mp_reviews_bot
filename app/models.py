from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cabinets = relationship("Cabinet", back_populates="project", cascade="all, delete-orphan")
    skus = relationship("Sku", back_populates="project", cascade="all, delete-orphan")
    kb_rules = relationship("KBRule", back_populates="project", cascade="all, delete-orphan")
    settings = relationship("Settings", back_populates="project", uselist=False, cascade="all, delete-orphan")
    metrics = relationship("AdminMetric", back_populates="project", cascade="all, delete-orphan")
    uploads = relationship("XlsxUpload", back_populates="project", cascade="all, delete-orphan")


class Cabinet(Base):
    __tablename__ = "cabinets"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    marketplace = Column(String(20), nullable=False)
    token_masked = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="cabinets")
    events = relationship("Event", back_populates="cabinet", cascade="all, delete-orphan")


class Sku(Base):
    __tablename__ = "skus"
    __table_args__ = (UniqueConstraint("project_id", "internal_sku", name="uq_skus_project_internal"),)

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    internal_sku = Column(String(255), nullable=False)
    product_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="skus")
    kb_rules = relationship("KBRule", back_populates="sku", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="sku")


class KBRule(Base):
    __tablename__ = "kb_rules"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"))
    level = Column(String(20), nullable=False)
    rule_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="kb_rules")
    sku = relationship("Sku", back_populates="kb_rules")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint(
            "marketplace_event_id",
            "marketplace",
            "cabinet_id",
            name="uq_events_marketplace_unique",
        ),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"))
    marketplace_event_id = Column(String(255), nullable=False)
    marketplace = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer)
    status = Column(String(30), nullable=False, default="new")
    raw_payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cabinet = relationship("Cabinet", back_populates="events")
    sku = relationship("Sku", back_populates="events")


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = (
        UniqueConstraint("project_id", name="uq_settings_project"),
        CheckConstraint("auto_5_4 in (0, 1)", name="chk_settings_auto_5_4"),
        CheckConstraint("auto_1_3 in (0, 1)", name="chk_settings_auto_1_3"),
        CheckConstraint("auto_questions in (0, 1)", name="chk_settings_auto_questions"),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tone = Column(String(255), nullable=False)
    auto_5_4 = Column(Boolean, nullable=False, default=False)
    auto_1_3 = Column(Boolean, nullable=False, default=False)
    auto_questions = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="settings")


class Balance(Base):
    __tablename__ = "balances"
    __table_args__ = (
        UniqueConstraint("owner_id", name="uq_balances_owner"),
        CheckConstraint("tokens >= 0", name="chk_balances_tokens"),
    )

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, nullable=False)
    tokens = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AdminMetric(Base):
    __tablename__ = "admin_metrics"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="metrics")


class XlsxUpload(Base):
    __tablename__ = "xlsx_uploads"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    rows_processed = Column(Integer, nullable=False, default=0)
    rows_failed = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="uploads")
