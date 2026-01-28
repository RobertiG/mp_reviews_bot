from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, constr, validator


class Marketplace(str, Enum):
    wb = "WB"
    ozon = "OZON"


class KBLevel(str, Enum):
    project = "project"
    sku = "sku"


class ProjectBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    owner_id: int = Field(..., ge=1)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = None


class Project(ProjectBase):
    id: int
    created_at: datetime
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
    project_id: int = Field(..., ge=1)
    name: constr(min_length=1, max_length=255)
    marketplace: Marketplace
    token_masked: constr(min_length=4, max_length=255)


class CabinetCreate(CabinetBase):
    pass


class CabinetUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = None
    token_masked: Optional[constr(min_length=4, max_length=255)] = None


class Cabinet(CabinetBase):
    id: int
    created_at: datetime
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


class SkuBase(BaseModel):
    project_id: int = Field(..., ge=1)
    internal_sku: constr(min_length=1, max_length=255)
    product_name: Optional[constr(max_length=255)] = None


class SkuCreate(SkuBase):
    pass


class SkuUpdate(BaseModel):
    internal_sku: Optional[constr(min_length=1, max_length=255)] = None
    product_name: Optional[constr(max_length=255)] = None


class Sku(SkuBase):
    id: int
    created_at: datetime
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


class KBRuleBase(BaseModel):
    project_id: int = Field(..., ge=1)
    sku_id: Optional[int] = Field(None, ge=1)
    level: KBLevel
    rule_text: constr(min_length=1)

    @validator("sku_id")
    def sku_id_required_for_level(cls, value, values):
        if values.get("level") == KBLevel.sku and value is None:
            raise ValueError("sku_id required for sku-level rules")
        return value


class KBRuleCreate(KBRuleBase):
    pass


class KBRuleUpdate(BaseModel):
    level: Optional[KBLevel] = None
    rule_text: Optional[constr(min_length=1)] = None
    sku_id: Optional[int] = Field(None, ge=1)


class KBRule(KBRuleBase):
    id: int
    created_at: datetime
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
    project_id: int = Field(..., ge=1)
    cabinet_id: int = Field(..., ge=1)
    sku_id: Optional[int] = Field(None, ge=1)
    marketplace_event_id: constr(min_length=1, max_length=255)
    marketplace: Marketplace
    event_type: constr(min_length=1, max_length=50)
    text: constr(min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    status: constr(min_length=1, max_length=30) = "new"
    raw_payload: constr(min_length=2)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    status: Optional[constr(min_length=1, max_length=30)] = None
    text: Optional[constr(min_length=1)] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class Event(EventBase):
    id: int
    created_at: datetime
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


class SettingsBase(BaseModel):
    project_id: int = Field(..., ge=1)
    tone: constr(min_length=1, max_length=255)
    auto_5_4: bool = False
    auto_1_3: bool = False
    auto_questions: bool = False


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    tone: Optional[constr(min_length=1, max_length=255)] = None
    auto_5_4: Optional[bool] = None
    auto_1_3: Optional[bool] = None
    auto_questions: Optional[bool] = None


class Settings(SettingsBase):
    id: int
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


class BalanceBase(BaseModel):
    owner_id: int = Field(..., ge=1)
    tokens: int = Field(..., ge=0)


class BalanceCreate(BalanceBase):
    pass


class BalanceUpdate(BaseModel):
    tokens: int = Field(..., ge=0)


class Balance(BalanceBase):
    id: int
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


class AdminMetricBase(BaseModel):
    project_id: int = Field(..., ge=1)
    metric_name: constr(min_length=1, max_length=100)
    metric_value: int


class AdminMetricCreate(AdminMetricBase):
    pass


class AdminMetricUpdate(BaseModel):
    metric_name: Optional[constr(min_length=1, max_length=100)] = None
    metric_value: Optional[int] = None


class AdminMetric(AdminMetricBase):
    id: int
    recorded_at: datetime
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


class XlsxUploadBase(BaseModel):
    project_id: int = Field(..., ge=1)
    filename: constr(min_length=1, max_length=255)
    rows_processed: int = Field(..., ge=0)
    rows_failed: int = Field(..., ge=0)


class XlsxUploadCreate(BaseModel):
    project_id: int = Field(..., ge=1)


class XlsxUploadUpdate(BaseModel):
    rows_processed: Optional[int] = Field(None, ge=0)
    rows_failed: Optional[int] = Field(None, ge=0)


class XlsxUpload(XlsxUploadBase):
    id: int
    uploaded_at: datetime
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
