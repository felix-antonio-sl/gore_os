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


# ---------------------------------------------------------------------------
# Initiative (Kanban)
# ---------------------------------------------------------------------------
class InitiativeItem(BaseModel):
    id: UUID
    code: str | None
    name: str
    description: str | None
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


class InitiativeCreate(BaseModel):
    name: str
    description: str | None = None
    status: str = "BACKLOG"
    dmaic_phase: str | None = None
    target_date: date | None = None
    total_days: int | None = None


class InitiativeMove(BaseModel):
    status: str  # target column


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
# Cockpit Responses (role-specific)
# ---------------------------------------------------------------------------
class CockpitJefeDGI(BaseModel):
    semaforo: list[DimensionSummary]
    decisions_pending: int
    team_status: list[dict]
    critical_alerts: list[dict]
    report_status: dict | None


class CockpitControlGestion(BaseModel):
    data_sources: list[DataSourceItem]
    indicators_alert: list[IndicatorItem]
    trends: list[IndicatorItem]
    work_queue: list[dict]


class CockpitProcesos(BaseModel):
    initiatives: list[InitiativeItem]
    bpmn_models: list[BPMNModelItem]
    today_agenda: list[dict]
    portfolio_stats: dict


class CockpitTD(BaseModel):
    compliance_bars: list[IndicatorItem]
    velocity: dict
    decrees: list[dict]
    kb_stats: dict
    committee: CommitteeSessionItem | None
    normative_alerts: list[dict]
