"""DTOs consumed by the retained decision, escalation, service and rendition journeys."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from uuid import UUID

from datetime import date, datetime

class RendicionItem(BaseModel):
    id: UUID
    agreement_number: str | None
    ipr_codigo_bip: str | None
    ipr_id: UUID | None
    renderer_name: str | None
    responsible_name: str | None = None
    state_code: str | None = None
    state_label: str | None
    period_start: date | None
    period_end: date | None
    submitted_at: datetime | None
    agreement_total_amount: float | None
    amount: float | None = None
    is_overdue: bool = False
    days_in_state: float | None = None

class RendicionUpdate(BaseModel):
    state_id: UUID | None = None
    responsible_id: UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    submitted_at: datetime | None = None
    amount: float | None = None
    comment: str | None = None
    metadata: dict | None = None

class RendicionCreate(BaseModel):
    agreement_id: UUID | None = None
    ipr_id: UUID | None = None
    renderer_id: UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    submitted_at: datetime | None = None  # default: NOW() server-side
    amount: float | None = None

class RendicionHistoryEntry(BaseModel):
    id: UUID
    previous_state: str | None
    new_state: str
    changed_by_name: str | None
    comment: str | None
    changed_at: datetime

class RendicionDetail(RendicionItem):
    agreement_id: UUID | None = None
    renderer_id: UUID | None = None
    responsible_id: UUID | None = None
    sla_days: int | None = None
    phase_entered_at: datetime | None = None
    total_cycle_days: float | None = None
    cycle_overdue: bool = False
    metadata: dict | None = None
    created_at: datetime | None = None
    history: list[RendicionHistoryEntry] = []
    allowed_transitions: list[dict] = []

class RenditionPhaseDefinition(BaseModel):
    """TP-06 parametric phase definition."""
    id: UUID
    ordinal: int
    code: str
    name: str
    responsible_role: str
    sla_days: int
    escalation_action: str | None = None
    is_internal: bool

class EscalationItem(BaseModel):
    """Rendition escalation record."""
    id: UUID
    rendition_id: UUID
    phase_id: UUID
    phase_code: str | None = None
    phase_name: str | None = None
    escalation_level: int
    detected_at: datetime
    alert_id: UUID | None = None
    resolved_at: datetime | None = None

class EscalationCheckResult(BaseModel):
    """Result of check-escalations batch operation."""
    checked: int
    new_escalations: int
    details: list[dict] = []

class CicloPhaseStatus(BaseModel):
    """Enhanced ciclo phase with TP-06 definition link."""
    ordinal: int
    code: str
    name: str
    responsible_role: str
    sla_days: int
    status: str  # completada | en_curso | pendiente | no_aplica
    entered_at: datetime | None = None
    exited_at: datetime | None = None
    duration_days: float | None = None
    is_overdue: bool = False

class ARDecisionCreate(BaseModel):
    description: str
    decision_type: str  # code: PRIORIDAD, RECURSO, ESCALAMIENTO, ESTRATEGIA
    due_date: date | None = None
    context: str | None = None
    responsible_id: UUID | None = None

class ARDecisionUpdate(BaseModel):
    description: str | None = None
    status: str | None = None  # code for transition
    due_date: date | None = None
    context: str | None = None
    responsible_id: UUID | None = None

class ARDecisionItem(BaseModel):
    id: UUID
    description: str
    decision_type: str
    decision_type_label: str
    status: str
    status_label: str
    due_date: date | None
    context: str | None
    responsible_name: str | None
    resolved_at: datetime | None
    created_at: datetime
    responsible_id: UUID | None = None
    allowed_statuses: list[str] = []
    can_edit: bool = False

class EscalationCreate(BaseModel):
    level: str  # code: NIVEL_1..NIVEL_4
    situation: str
    impact: str
    options: list[dict] | None = None  # [{option, pros, cons}]
    recommendation: str | None = None
    deadline: datetime | None = None
    subject_type: str | None = None
    subject_id: UUID | None = None

class EscalationUpdate(BaseModel):
    status: str | None = None
    situation: str | None = None
    impact: str | None = None
    options: list[dict] | None = None
    recommendation: str | None = None
    resolved_description: str | None = None

class EscalationItemWaveB(BaseModel):
    id: UUID
    code: str
    level: str
    level_label: str
    status: str
    status_label: str
    situation: str
    impact: str
    options: list[dict]
    recommendation: str | None
    deadline: datetime | None
    subject_type: str | None
    subject_id: UUID | None
    escalated_to: str | None
    resolved_description: str | None
    resolved_at: datetime | None
    alert_id: UUID | None
    created_at: datetime
    created_by_name: str | None = None
    allowed_statuses: list[str] = []
    can_edit: bool = False

class EscalationStats(BaseModel):
    total_active: int
    by_level: list[dict]
    avg_resolution_hours: float | None
    resolved_count: int

class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    area: str  # CG, MP, TD, KC
    sla_days: int | None = None
    how_to_request: str | None = None
    deliverables: str | None = None

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    area: str | None = None
    status: str | None = None
    sla_days: int | None = None
    how_to_request: str | None = None
    deliverables: str | None = None

class ServiceItem(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    area: str
    status: str
    status_label: str
    sla_days: int | None
    how_to_request: str | None
    deliverables: str | None

class ServiceRequestCreate(BaseModel):
    service_id: UUID
    description: str
    urgency: str = "NORMAL"

class ServiceRequestUpdate(BaseModel):
    status: str | None = None
    assigned_to_id: UUID | None = None
    satisfaction_score: int | None = None
    feedback_text: str | None = None

class ServiceRequestItem(BaseModel):
    id: UUID
    code: str
    service_id: UUID
    service_name: str
    status: str
    status_label: str
    requester_name: str
    division_name: str | None
    description: str
    urgency: str
    assigned_to_name: str | None
    started_at: datetime | None
    completed_at: datetime | None
    satisfaction_score: int | None
    days_elapsed: float | None
    sla_days: int | None
    is_overdue: bool = False
    created_at: datetime
    allowed_statuses: list[str] = []
    can_assign: bool = False
    can_feedback: bool = False

class SLACreate(BaseModel):
    product_type: str  # code from dgi_sla_product_type
    description: str | None = None
    target_days: int
    target_hour: str | None = None  # HH:MM format
    priority: int = 0

class SLAUpdate(BaseModel):
    description: str | None = None
    target_days: int | None = None
    target_hour: str | None = None
    priority: int | None = None

class SLAItem(BaseModel):
    id: UUID
    service_id: UUID
    product_type: str
    product_type_label: str
    description: str | None
    target_days: int
    target_hour: str | None
    priority: int
