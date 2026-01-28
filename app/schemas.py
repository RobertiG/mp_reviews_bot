from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class OwnerBase(BaseModel):
    telegram_user_id: str
    display_name: Optional[str] = None
    is_active: bool = True


class OwnerCreate(OwnerBase):
    pass


class OwnerRead(OwnerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    name: str
    tone_description: Optional[str] = None
    auto_approve_enabled: bool = False


class ProjectCreate(ProjectBase):
    owner_id: int


class ProjectRead(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CabinetBase(BaseModel):
    marketplace: str
    external_id: str
    display_name: Optional[str] = None
    status: str = "active"
    api_token_encrypted: Optional[str] = None
    last_synced_at: Optional[datetime] = None


class CabinetCreate(CabinetBase):
    project_id: int


class CabinetRead(CabinetBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SkuMappingBase(BaseModel):
    marketplace: str
    seller_sku: str
    marketplace_item_id: Optional[str] = None
    internal_sku: str
    product_name: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None


class SkuMappingCreate(SkuMappingBase):
    project_id: int


class SkuMappingRead(SkuMappingBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class KbRuleBase(BaseModel):
    internal_sku: Optional[str] = None
    scope: str
    rule_type: str = "fact"
    text: str
    raw_payload: Optional[dict[str, Any]] = None


class KbRuleCreate(KbRuleBase):
    project_id: int


class KbRuleRead(KbRuleBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    marketplace_event_id: str
    event_type: str
    text: Optional[str] = None
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    status: str = "new"
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    kb_rule_ids: Optional[List[int]] = None
    media_urls: Optional[List[str]] = None
    raw_payload: Optional[dict[str, Any]] = None
    occurred_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None


class EventCreate(EventBase):
    project_id: int
    cabinet_id: int


class EventRead(EventBase):
    id: int
    project_id: int
    cabinet_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: str
    status: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    kb_rule_ids: Optional[List[int]] = None
    raw_payload: Optional[dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    project_id: int
    actor_owner_id: Optional[int] = None


class AuditLogRead(AuditLogBase):
    id: int
    project_id: int
    actor_owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BillingBalanceBase(BaseModel):
    balance_tokens: int = 0


class BillingBalanceCreate(BillingBalanceBase):
    owner_id: int


class BillingBalanceRead(BillingBalanceBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TokenLedgerBase(BaseModel):
    delta_tokens: int
    balance_after: Optional[int] = None
    reason: str
    raw_payload: Optional[dict[str, Any]] = None


class TokenLedgerCreate(TokenLedgerBase):
    owner_id: int
    project_id: Optional[int] = None
    event_id: Optional[int] = None


class TokenLedgerRead(TokenLedgerBase):
    id: int
    owner_id: int
    project_id: Optional[int] = None
    event_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    telegram_user_id: str
    display_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProjectUserBase(BaseModel):
    role: str = "viewer"
    status: str = "active"


class ProjectUserCreate(ProjectUserBase):
    project_id: int
    user_id: int


class ProjectUserRead(ProjectUserBase):
    id: int
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
