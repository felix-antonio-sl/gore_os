from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CoreSessionCreate(BaseModel):
    scheduled_at: datetime
    session_type: str = "ORDINARIA"  # ORDINARIA | EXTRAORDINARIA
    location: Optional[str] = None
    summary: Optional[str] = None


class CoreSessionListItem(BaseModel):
    id: UUID                          # session.id
    session_number: int
    session_type: str                 # ORDINARIA | EXTRAORDINARIA
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    summary: Optional[str] = None
    status: str                       # PROGRAMADA | EN_CURSO | FINALIZADA
    topic_count: int
    quorum_reached: Optional[bool] = None


class TopicCreate(BaseModel):
    subject: str
    ipr_id: Optional[UUID] = None
    quorum_type: str = "SIMPLE"       # SIMPLE | CALIFICADA


class VoteCreate(BaseModel):
    vote: str                         # A_FAVOR | EN_CONTRA | ABSTENCION


class TopicWithVotes(BaseModel):
    id: UUID
    agreement_number: int
    subject: str
    decision: Optional[str] = None
    ipr_id: Optional[UUID] = None
    ipr_codigo_bip: Optional[str] = None
    quorum_type: str                  # SIMPLE | CALIFICADA
    votes_favor: int
    votes_contra: int
    votes_abstencion: int
    votes_total: int
    required_votes: int               # 9 or 11
    result: str                       # APROBADO | RECHAZADO | PENDIENTE


class MemberAttendance(BaseModel):
    member_id: UUID
    person_name: str
    role_in_committee: Optional[str] = None
    has_voted_in_session: bool


class CoreSessionDetail(CoreSessionListItem):
    location: Optional[str] = None
    minute_id: Optional[UUID] = None
    topics: list[TopicWithVotes]
    members_present: int
    members_total: int


class FinalizarBody(BaseModel):
    summary: Optional[str] = None
