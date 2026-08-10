from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Literal, Optional


class ReunionListItem(BaseModel):
    id: UUID
    session_id: UUID
    session_number: int
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    summary: Optional[str] = None
    organizer_name: Optional[str] = None
    status: str  # PROGRAMADA, EN_CURSO, FINALIZADA
    topic_count: int


class TopicItem(BaseModel):
    id: UUID
    agreement_number: int
    subject: str
    decision: Optional[str] = None
    responsible_name: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    ipr_id: Optional[UUID] = None
    ipr_codigo_bip: Optional[str] = None
    context_type: Optional[str] = None  # 'alerta', 'compromiso', 'problema'


class ReunionDetail(ReunionListItem):
    location: Optional[str] = None
    topics: list[TopicItem]


class ReunionCreate(BaseModel):
    scheduled_at: datetime
    location: Optional[str] = None
    summary: Optional[str] = None


class TopicCreate(BaseModel):
    subject: str
    ipr_id: Optional[UUID] = None
    responsible_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TopicUpdate(BaseModel):
    decision: Optional[str] = None
    status: Optional[Literal["PENDIENTE", "COMPLETADO"]] = None


class FinalizarBody(BaseModel):
    summary: Optional[str] = None


class AutoSuggestion(BaseModel):
    type: str  # 'alerta_critica', 'compromiso_vencido', 'problema_abierto'
    subject: str
    detail: str
    target_id: UUID
    ipr_codigo_bip: Optional[str] = None
