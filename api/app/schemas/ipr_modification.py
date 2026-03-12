from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IprModificationCreate(BaseModel):
    modification_type_id: UUID
    description: str
    justification: str | None = None
    field_changed: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    amount_delta: float | None = None


class IprModificationUpdate(BaseModel):
    status_id: UUID | None = None
    description: str | None = None
    justification: str | None = None


class IprModificationItem(BaseModel):
    id: UUID
    code: str
    modification_type_code: str
    modification_type_label: str
    status_code: str
    status_label: str
    description: str
    justification: str | None
    field_changed: str | None
    old_value: str | None
    new_value: str | None
    amount_delta: float | None
    requested_by_name: str
    approved_by_name: str | None
    approved_at: datetime | None
    created_at: datetime
