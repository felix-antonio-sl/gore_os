from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class CarryoverItem(BaseModel):
    id: UUID
    fiscal_year: int
    amount: Decimal


class BudgetCommitmentItem(BaseModel):
    id: UUID
    commitment_number: str
    amount: Decimal
    issued_at: date
    expires_at: Optional[date]
    status_label: Optional[str]
    ipr_id: Optional[UUID] = None
    ipr_codigo_bip: Optional[str]


class PresupuestoListItem(BaseModel):
    id: UUID
    code: str
    name: str
    fiscal_year: int
    division_name: Optional[str]
    subtitle_label: Optional[str]
    program_type_label: Optional[str]
    item_label: Optional[str] = None
    allocation_label: Optional[str] = None
    program_code_label: Optional[str] = None
    initial_amount: Decimal
    current_amount: Optional[Decimal]
    committed_amount: Decimal
    accrued_amount: Decimal
    paid_amount: Decimal
    execution_pct: float


class PresupuestoDetail(PresupuestoListItem):
    division_id: Optional[UUID]
    item_label: Optional[str]
    allocation_label: Optional[str]
    fndr_amount: Optional[Decimal]
    sectorial_amount: Optional[Decimal]
    created_at: datetime
    carryovers: list[CarryoverItem]
    budget_commitments: list[BudgetCommitmentItem]


class PresupuestoCreate(BaseModel):
    code: str
    name: str
    fiscal_year: int
    program_type_id: Optional[UUID] = None
    subtitle_id: Optional[UUID] = None
    item_id: Optional[UUID] = None
    allocation_id: Optional[UUID] = None
    program_code_id: Optional[UUID] = None
    owner_division_id: Optional[UUID] = None
    initial_amount: Decimal
    current_amount: Optional[Decimal] = None


class BudgetCommitmentCreate(BaseModel):
    description: Optional[str] = None
    amount: int
    ipr_id: Optional[UUID] = None
    agreement_id: Optional[UUID] = None


class PresupuestoUpdate(BaseModel):
    initial_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    committed_amount: Optional[Decimal] = None
    accrued_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    program_code_id: Optional[UUID] = None


class PresupuestoResumen(BaseModel):
    group_key: str
    group_label: str
    initial_amount: Decimal
    current_amount: Decimal
    paid_amount: Decimal
    execution_pct: float
    program_count: int


class BudgetCycleMilestoneItem(BaseModel):
    id: UUID
    phase: str
    quarter: Optional[str] = None
    ordinal: int
    month_label: str
    name: str
    responsible: str
    deliverable: Optional[str] = None


class BudgetCycleTrackingItem(BaseModel):
    id: UUID
    milestone_id: UUID
    ordinal: int
    phase: str
    quarter: Optional[str] = None
    month_label: str
    name: str
    responsible: str
    deliverable: Optional[str] = None
    fiscal_year: int
    status: str
    planned_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    completed_by_name: Optional[str] = None
    notes: Optional[str] = None


class BudgetCycleTrackingUpdate(BaseModel):
    status: Optional[str] = None
    planned_date: Optional[date] = None
    notes: Optional[str] = None


class BudgetCycleSummary(BaseModel):
    fiscal_year: int
    total_milestones: int
    completed: int
    en_curso: int
    pendiente: int
    omitido: int
    completion_pct: float
