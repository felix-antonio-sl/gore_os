from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IPRListItem(BaseModel):
    id: UUID
    codigo_bip: str
    name: str
    ipr_type: str | None
    status: str | None
    investment_sector: str | None
    funding_source: str | None
    alert_level: str | None
    has_open_problems: bool
    executor_name: str | None
    total_budget: float | None


class IPRDetail(BaseModel):
    id: UUID
    codigo_bip: str
    name: str
    ipr_type: str | None
    ipr_type_label: str | None
    status: str | None
    status_label: str | None
    investment_sector: str | None
    funding_source: str | None
    fund_category: str | None
    mechanism: str | None
    alert_level: str | None
    has_open_problems: bool
    executor_name: str | None
    formulator_name: str | None
    max_execution_months: int | None
    intended_outcome: str | None
    requires_cgr: bool
    requires_dipres: bool
    commitment_count: int
    problem_count: int
    alert_count: int
    created_at: datetime


class IprCreate(BaseModel):
    codigo_bip: str
    name: str
    ipr_type_id: UUID | None = None
    status_id: UUID | None = None
    sponsor_division_id: UUID | None = None
    description: str | None = None


class IprAssigneeUpdate(BaseModel):
    assignee_id: UUID


class IprUpdate(BaseModel):
    name: str | None = None
    ipr_type_id: UUID | None = None
    status_id: UUID | None = None
    investment_sector_id: UUID | None = None
    funding_source_id: UUID | None = None
    sponsor_division_id: UUID | None = None
    assignee_id: UUID | None = None
