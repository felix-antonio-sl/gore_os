from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class ActoListItem(BaseModel):
    id: UUID
    act_number: str
    act_type: str
    act_type_label: str
    subject: str
    state: str
    state_label: str
    issuer_name: Optional[str] = None
    signer_name: Optional[str] = None
    issued_at: datetime
    requires_cgr: bool
    cgr_outcome: Optional[str] = None
    cgr_outcome_label: Optional[str] = None
    # Resolution fields (only when act_type=RESOLUCION)
    resolution_type: Optional[str] = None
    resolution_type_label: Optional[str] = None
    ipr_id: Optional[UUID] = None
    ipr_codigo_bip: Optional[str] = None
    agreement_id: Optional[UUID] = None
    agreement_number: Optional[str] = None
    budget_amount: Optional[Decimal] = None


class ActoDetail(ActoListItem):
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    cgr_submitted_at: Optional[date] = None
    cgr_resolved_at: Optional[date] = None
    resolution_subtype: Optional[str] = None
    resolution_subtype_label: Optional[str] = None
    created_at: datetime


class ActoCreate(BaseModel):
    act_number: Optional[str] = None
    act_type_id: UUID
    subject: str
    issued_at: datetime
    requires_cgr: bool = False
    issuer_id: Optional[UUID] = None
    # Resolution fields (optional, for type RESOLUCION)
    resolution_type_id: Optional[UUID] = None
    resolution_subtype_id: Optional[UUID] = None
    ipr_id: Optional[UUID] = None
    agreement_id: Optional[UUID] = None
    budget_amount: Optional[Decimal] = None


class ActoUpdate(BaseModel):
    state_id: Optional[UUID] = None
    subject: Optional[str] = None
    act_number: Optional[str] = None
    issuer_id: Optional[UUID] = None
    requires_cgr: Optional[bool] = None
    cgr_outcome_id: Optional[UUID] = None
    # Resolution linkage
    ipr_id: Optional[UUID] = None
    agreement_id: Optional[UUID] = None
    budget_amount: Optional[Decimal] = None
