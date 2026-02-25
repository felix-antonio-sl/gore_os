from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class InstallmentItem(BaseModel):
    id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    payment_status: str
    payment_status_label: str
    paid_at: Optional[datetime] = None
    paid_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None


class ConvenioListItem(BaseModel):
    id: UUID
    agreement_number: Optional[str] = None
    agreement_type: str
    agreement_type_label: str
    state: str
    state_label: str
    ipr_id: Optional[UUID] = None
    ipr_codigo_bip: Optional[str] = None
    ipr_name: Optional[str] = None
    giver_name: Optional[str] = None
    receiver_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    signed_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    days_to_expiry: Optional[int] = None
    installment_count: int
    paid_installments: int


class ConvenioDetail(ConvenioListItem):
    technical_referent_name: Optional[str] = None
    cgr_outcome: Optional[str] = None
    cgr_outcome_label: Optional[str] = None
    created_at: datetime
    installments: list[InstallmentItem]


class ConvenioCreate(BaseModel):
    agreement_number: Optional[str] = None
    agreement_type_id: UUID
    state_id: UUID
    ipr_id: Optional[UUID] = None
    giver_id: Optional[UUID] = None
    receiver_id: Optional[UUID] = None
    total_amount: Optional[Decimal] = None
    signed_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class ConvenioUpdate(BaseModel):
    state_id: Optional[UUID] = None
    total_amount: Optional[Decimal] = None
    valid_to: Optional[datetime] = None
    cgr_outcome_id: Optional[UUID] = None


class InstallmentCreate(BaseModel):
    installment_number: int
    amount: Decimal
    due_date: date
    payment_status_id: UUID


class InstallmentUpdate(BaseModel):
    payment_status_id: Optional[UUID] = None
    paid_at: Optional[datetime] = None
    paid_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None
