from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    owner_id: int


class ProjectOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CabinetCreate(BaseModel):
    project_id: int
    marketplace: str
    name: str
    api_token: str


class CabinetOut(BaseModel):
    id: int
    project_id: int
    marketplace: str
    name: str
    api_token_masked: str
    created_at: datetime

    class Config:
        from_attributes = True


class SKUMapCreate(BaseModel):
    project_id: int
    marketplace: str
    seller_sku: str
    marketplace_item_id: str
    internal_sku: str
    product_name: Optional[str] = None


class SKUMapOut(BaseModel):
    id: int
    project_id: int
    marketplace: str
    seller_sku: str
    marketplace_item_id: str
    internal_sku: str
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KBRuleCreate(BaseModel):
    project_id: int
    internal_sku: Optional[str] = None
    text: str


class KBRuleOut(BaseModel):
    id: int
    project_id: int
    internal_sku: Optional[str] = None
    rule_type: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    project_id: int
    cabinet_id: int
    marketplace: str
    marketplace_event_id: str
    event_type: str
    text: str
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    internal_sku: str
    raw_payload: dict
    media_links: Optional[list] = None


class EventOut(BaseModel):
    id: int
    project_id: int
    cabinet_id: int
    marketplace: str
    marketplace_event_id: str
    event_type: str
    text: str
    rating: Optional[int]
    sentiment: Optional[str]
    internal_sku: str
    status: str
    raw_payload: dict
    media_links: Optional[list]
    suggested_reply: Optional[str]
    confidence: Optional[int]
    kb_rule_ids: Optional[list]
    conflict: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingsOut(BaseModel):
    project_id: int
    autogen_positive: bool
    autosend_positive: bool
    autogen_negative: bool
    autosend_negative: bool
    autogen_questions: bool
    autosend_questions: bool

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    autogen_positive: Optional[bool] = None
    autosend_positive: Optional[bool] = None
    autogen_negative: Optional[bool] = None
    autosend_negative: Optional[bool] = None
    autogen_questions: Optional[bool] = None
    autosend_questions: Optional[bool] = None


class BalanceOut(BaseModel):
    owner_id: int
    tokens: int

    class Config:
        from_attributes = True


class BalanceUpdate(BaseModel):
    delta: int = Field(..., description="positive or negative tokens")
    reason: str


class AdminMetricsOut(BaseModel):
    projects: int
    events: int
    tokens_spent: int


class LLMResponse(BaseModel):
    text: str
    confidence: int
    kb_rule_ids: List[int] = []
    conflict: bool = False
