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
    owner_division_id: Optional[UUID] = None
    initial_amount: Decimal
    current_amount: Optional[Decimal] = None


class PresupuestoUpdate(BaseModel):
    initial_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    committed_amount: Optional[Decimal] = None
    accrued_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None


class PresupuestoResumen(BaseModel):
    group_key: str
    group_label: str
    initial_amount: Decimal
    current_amount: Decimal
    paid_amount: Decimal
    execution_pct: float
    program_count: int
