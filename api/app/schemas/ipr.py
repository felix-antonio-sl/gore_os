from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date


class IPRListItem(BaseModel):
    id: UUID
    codigo_bip: str
    name: str
    ipr_type: str | None
    status: str | None
    investment_sector: str | None
    funding_source: str | None
    mechanism: str | None = None
    mcd_phase: str | None = None
    alert_level: str | None
    has_open_problems: bool
    executor_name: str | None
    total_budget: float | None
    phase_entered_at: datetime | None = None


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
    fund_category_label: str | None = None
    mechanism: str | None
    mechanism_label: str | None = None
    mcd_phase: str | None = None
    mcd_phase_label: str | None = None
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
    agreement_count: int = 0
    phase_entered_at: datetime | None = None
    assignee_id: UUID | None = None
    assignee_name: str | None = None
    sponsor_division_id: UUID | None = None
    sponsor_division_name: str | None = None
    created_at: datetime


class TrackInfo(BaseModel):
    mechanism: str | None = None
    mechanism_label: str | None = None
    mechanism_attrs: dict = {}


class BudgetCommitmentItem(BaseModel):
    id: UUID
    commitment_number: str
    amount: Decimal
    issued_at: date
    expires_at: date | None
    status_label: str | None
    ipr_id: UUID | None = None
    ipr_codigo_bip: str | None
