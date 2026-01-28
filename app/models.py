from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Owner(Base, TimestampMixin):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    balance: Mapped["BillingBalance"] = relationship(
        back_populates="owner", cascade="all, delete-orphan", uselist=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    project_memberships: Mapped[list["ProjectUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tone_description: Mapped[str | None] = mapped_column(Text)
    auto_approve_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")

    owner: Mapped[Owner] = relationship(back_populates="projects")
    cabinets: Mapped[list["Cabinet"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    sku_mappings: Mapped[list["SkuMapping"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    kb_rules: Mapped[list["KbRule"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    members: Mapped[list["ProjectUser"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectUser(Base, TimestampMixin):
    __tablename__ = "project_users"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default="viewer")
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="active")

    project: Mapped[Project] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="project_memberships")


class Cabinet(Base, TimestampMixin):
    __tablename__ = "cabinets"
    __table_args__ = (
        UniqueConstraint("project_id", "marketplace", "external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    marketplace: Mapped[str] = mapped_column(String(32), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    api_token_encrypted: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="active")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[Project] = relationship(back_populates="cabinets")
    events: Mapped[list["Event"]] = relationship(
        back_populates="cabinet", cascade="all, delete-orphan"
    )


class SkuMapping(Base, TimestampMixin):
    __tablename__ = "sku_mappings"
    __table_args__ = (
        UniqueConstraint("project_id", "marketplace", "seller_sku"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    marketplace: Mapped[str] = mapped_column(String(32), nullable=False)
    seller_sku: Mapped[str] = mapped_column(String(128), nullable=False)
    marketplace_item_id: Mapped[str | None] = mapped_column(String(128))
    internal_sku: Mapped[str] = mapped_column(String(128), nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(255))
    raw_payload: Mapped[dict | None] = mapped_column(JSON)

    project: Mapped[Project] = relationship(back_populates="sku_mappings")


class KbRule(Base, TimestampMixin):
    __tablename__ = "kb_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    internal_sku: Mapped[str | None] = mapped_column(String(128))
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False, server_default="fact")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)

    project: Mapped[Project] = relationship(back_populates="kb_rules")


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("cabinet_id", "marketplace_event_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    cabinet_id: Mapped[int] = mapped_column(ForeignKey("cabinets.id"), nullable=False)
    marketplace_event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(Integer)
    sentiment: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="new")
    confidence: Mapped[int | None] = mapped_column(Integer)
    kb_rule_ids: Mapped[list[int] | None] = mapped_column(JSON)
    media_urls: Mapped[list[str] | None] = mapped_column(JSON)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[Project] = relationship(back_populates="events")
    cabinet: Mapped[Cabinet] = relationship(back_populates="events")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    actor_owner_id: Mapped[int | None] = mapped_column(ForeignKey("owners.id"))
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[int | None] = mapped_column(Integer)
    kb_rule_ids: Mapped[list[int] | None] = mapped_column(JSON)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)


class BillingBalance(Base, TimestampMixin):
    __tablename__ = "billing_balances"
    __table_args__ = (
        UniqueConstraint("owner_id"),
        CheckConstraint("balance_tokens >= 0", name="ck_billing_balance_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)
    balance_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    owner: Mapped[Owner] = relationship(back_populates="balance")


class TokenLedger(Base, TimestampMixin):
    __tablename__ = "token_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"))
    delta_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
