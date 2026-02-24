from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class CompromisoListItem(BaseModel):
    id: UUID
    code: str | None
    description: str
    ipr_codigo_bip: str | None
    ipr_name: str | None
    commitment_type: str | None
    responsible_name: str | None
    responsible_id: UUID
    division_name: str | None
    due_date: date
    state: str
    state_label: str
    days_remaining: int
    completed_at: datetime | None
    verified_at: datetime | None


class CompromisoDetail(BaseModel):
    id: UUID
    code: str | None
    description: str
    ipr_id: UUID | None
    ipr_codigo_bip: str | None
    ipr_name: str | None
    problem_id: UUID | None
    commitment_type: str | None
    commitment_type_label: str | None
    responsible_id: UUID
    responsible_name: str | None
    division_id: UUID | None
    division_name: str | None
    due_date: date
    state: str
    state_label: str
    days_remaining: int
    observations: str | None
    completed_at: datetime | None
    verified_by_name: str | None
    verified_at: datetime | None
    created_at: datetime
    history: list["HistoryEntry"]


class HistoryEntry(BaseModel):
    id: UUID
    previous_state: str | None
    new_state: str
    changed_by_name: str | None
    comment: str | None
    changed_at: datetime


class CompromisoCreate(BaseModel):
    description: str
    ipr_id: UUID | None = None
    problem_id: UUID | None = None
    commitment_type_id: UUID
    responsible_id: UUID
    division_id: UUID | None = None
    due_date: date
    observations: str | None = None


class StateChangeRequest(BaseModel):
    observations: str | None = None
