from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ThresholdListItem(BaseModel):
    id: UUID
    code: str
    label: str
    value_utm: Optional[Decimal] = None
    value_pct: Optional[Decimal] = None
    enforcement_point: str
    source_normativa: Optional[str] = None
    applies_to_track: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ThresholdCreate(BaseModel):
    code: str
    label: str
    value_utm: Optional[Decimal] = None
    value_pct: Optional[Decimal] = None
    enforcement_point: str
    source_normativa: Optional[str] = None
    applies_to_track: Optional[str] = None


class ThresholdUpdate(BaseModel):
    label: Optional[str] = None
    value_utm: Optional[Decimal] = None
    value_pct: Optional[Decimal] = None
    enforcement_point: Optional[str] = None
    source_normativa: Optional[str] = None
    applies_to_track: Optional[str] = None
    is_active: Optional[bool] = None
