from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Indicator
# ---------------------------------------------------------------------------
class IndicatorItem(BaseModel):
    id: UUID
    code: str
    name: str
    dimension: str
    current_value: float | None
    target_value: float | None
    unit: str
    signal: str | None  # VERDE, AMARILLO, ROJO
    trend: str | None  # up, down, flat
    description: str | None
    last_updated_at: datetime | None


class DimensionSummary(BaseModel):
    dimension: str
    label: str
    signal: str  # VERDE, AMARILLO, ROJO (worst of indicators)
    indicator_count: int


class RenditionSummary(BaseModel):
    total: int
    by_state: list[dict]  # [{code, label, count}]
    amount_at_risk: float | None


# ---------------------------------------------------------------------------
# Initiative (Kanban)
# ---------------------------------------------------------------------------
class InitiativeItem(BaseModel):
    id: UUID
    code: str | None
    name: str
    description: str | None
    responsible_id: UUID | None
    responsible_name: str | None
    status: str
    dmaic_phase: str | None
    division_name: str | None
    start_date: date | None
    target_date: date | None
    current_day: int
    total_days: int | None
    progress: float
    wip_column: str | None
    sort_order: int = 0


class InitiativeCreate(BaseModel):
    name: str
    description: str | None = None
    status: str = "BACKLOG"
    dmaic_phase: str | None = None
    target_date: date | None = None
    total_days: int | None = None


class InitiativeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    dmaic_phase: str | None = None
    target_date: date | None = None
    total_days: int | None = None
    responsible_id: UUID | None = None
    division_id: UUID | None = None


class InitiativeMove(BaseModel):
    status: str  # target column


class InitiativeReorder(BaseModel):
    initiative_ids: list[UUID]  # ordered list of IDs in new position order


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
class ReportItem(BaseModel):
    id: UUID
    code: str | None
    report_type: str
    status: str
    title: str
    period_start: date | None
    period_end: date | None
    recipient: str | None
    generated_by_name: str | None
    sent_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------------------------
# BPMN Model
# ---------------------------------------------------------------------------
class BPMNModelItem(BaseModel):
    id: UUID
    code: str | None
    process_name: str
    version: str
    status: str
    description: str | None


# ---------------------------------------------------------------------------
# Data Source Status
# ---------------------------------------------------------------------------
class DataSourceItem(BaseModel):
    id: UUID
    division_name: str | None
    source_name: str
    status: str
    last_data_at: datetime | None
    days_behind: int


# ---------------------------------------------------------------------------
# Committee Session
# ---------------------------------------------------------------------------
class CommitteeSessionItem(BaseModel):
    id: UUID
    session_date: datetime
    status: str
    agenda: list
    agreements: list
    notes: str | None


# ---------------------------------------------------------------------------
# Cockpit typed sub-models
# ---------------------------------------------------------------------------
class DecisionItem(BaseModel):
    source: str  # "alert" | "rendition"
    id: str
    title: str
    severity: str


class DecreeItem(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    deadline: date | None
    days_until: int | None


class DecreeUpdate(BaseModel):
    status: str | None = None
    deadline: date | None = None
    description: str | None = None


class NormativeAlertItem(BaseModel):
    message: str
    days_until: int
    decree_code: str | None = None


class VelocityStats(BaseModel):
    current: float
    required: float
    months_remaining: int


class KBStats(BaseModel):
    module_status: str
    message: str


class AgendaItem(BaseModel):
    time: str
    activity: str
    process: str


class PortfolioStats(BaseModel):
    active: int
    completed: int
    target: int


# ---------------------------------------------------------------------------
# Cockpit Responses (role-specific)
# ---------------------------------------------------------------------------
class CockpitJefeDGI(BaseModel):
    semaforo: list[DimensionSummary]
    decisions_pending: int
    decision_items: list[DecisionItem] = []
    team_status: list[dict]
    critical_alerts: list[dict]
    report_status: dict | None
    rendition_summary: RenditionSummary | None = None


class CockpitControlGestion(BaseModel):
    data_sources: list[DataSourceItem]
    indicators_alert: list[IndicatorItem]
    trends: list[IndicatorItem]
    work_queue: list[dict]


class CockpitProcesos(BaseModel):
    initiatives: list[InitiativeItem]
    bpmn_models: list[BPMNModelItem]
    today_agenda: list[AgendaItem]
    portfolio_stats: PortfolioStats


class CockpitTD(BaseModel):
    compliance_bars: list[IndicatorItem]
    velocity: VelocityStats
    decrees: list[DecreeItem]
    kb_stats: KBStats
    committee: CommitteeSessionItem | None
    normative_alerts: list[NormativeAlertItem]


# ---------------------------------------------------------------------------
# Report content (auto-populated sections)
# ---------------------------------------------------------------------------
class ReportContentSection(BaseModel):
    section_id: str
    title: str
    content: str
    auto_populated: bool
    last_edited_at: datetime | None = None


class ReportContent(BaseModel):
    id: UUID
    code: str | None
    title: str
    report_type: str
    status: str
    period_start: date | None
    period_end: date | None
    recipient: str | None
    generated_by_name: str | None
    created_at: datetime
    sections: list[ReportContentSection]


# ---------------------------------------------------------------------------
# Explorer domain items
# ---------------------------------------------------------------------------
class OrganizacionItem(BaseModel):
    id: UUID
    code: str
    name: str
    short_name: str | None
    org_type: str | None
    parent_name: str | None
    rut: str | None
    user_count: int


class PersonaItem(BaseModel):
    id: UUID
    names: str
    paternal_surname: str
    maternal_surname: str | None
    email: str | None
    phone: str | None
    is_active: bool
    organization_name: str | None
    estamento: str | None
    position_name: str | None


class TerritorioItem(BaseModel):
    id: UUID
    code: str
    name: str
    territory_type: str | None
    parent_name: str | None
    population: int | None
    area_km2: float | None


class EventoItem(BaseModel):
    id: UUID
    occurred_at: datetime
    event_type: str
    event_type_label: str
    subject_type: str
    subject_id: UUID
    actor_name: str | None
    summary: str | None


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
    metadata: dict | None = None  # External phase timestamps


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


class RendicionPhaseEntry(BaseModel):
    phase_code: str
    phase_label: str | None = None
    entered_at: datetime
    exited_at: datetime | None = None
    duration_days: float | None = None
    sla_days: int | None = None
    is_overdue: bool = False


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


class ReportCreate(BaseModel):
    title: str
    report_type: str  # FLASH, SEMANAL, MENSUAL, TEMATICO
    period_start: date | None = None
    period_end: date | None = None
    recipient: str | None = None


class ReportSectionUpdate(BaseModel):
    section_id: str
    content: str


class ReportStatusChange(BaseModel):
    status: str  # EN_REVISION, ENVIADO, BORRADOR
