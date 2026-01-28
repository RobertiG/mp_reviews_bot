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

    class Config:
        orm_mode = True
