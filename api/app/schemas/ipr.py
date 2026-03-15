from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


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
    created_at: datetime


class IprCreate(BaseModel):
    codigo_bip: str
    name: str
    ipr_type_id: UUID | None = None
    status_id: UUID | None = None
    sponsor_division_id: UUID | None = None
    mechanism_id: UUID | None = None
    funding_source_id: UUID | None = None
    mcd_phase_id: UUID | None = None
    description: str | None = None


class IprAssigneeUpdate(BaseModel):
    assignee_id: UUID


class IprUpdate(BaseModel):
    name: str | None = None
    ipr_type_id: UUID | None = None
    status_id: UUID | None = None
    investment_sector_id: UUID | None = None
    funding_source_id: UUID | None = None
    mechanism_id: UUID | None = None
    mcd_phase_id: UUID | None = None
    fund_category_id: UUID | None = None
    sponsor_division_id: UUID | None = None
    assignee_id: UUID | None = None


class TrackInfo(BaseModel):
    mechanism: str | None = None
    mechanism_label: str | None = None
    evaluator: str | None = None
    evaluator_label: str | None = None
    favorable_products: list[str] = []
    unfavorable_products: list[str] = []
    terminal_negative: list[str] = []
    thresholds: dict[str, float] = {}
    sla_days: dict[str, int] = {}
    required_attrs: list[str] = []
    mechanism_attrs: dict = {}
    evaluations: list = []


class SatelliteStatus(BaseModel):
    name: str
    label: str
    count: int
    detail: dict | None = None


class TransitionReadiness(BaseModel):
    code: str
    label: str
    target_phase: str | None = None
    gates_met: int
    gates_total: int
    blocking_gates: list[str] = []


class IprReadiness(BaseModel):
    satellites: list[SatelliteStatus]
    next_transitions: list[TransitionReadiness]


class DivisionCarteraItem(BaseModel):
    division_id: str
    division_name: str
    abbreviation: str | None = None
    total_iprs: int
    by_phase: dict[str, int]
    critical_alerts: int
    open_problems: int
    overdue_commitments: int
    health_signal: str  # VERDE, AMARILLO, ROJO
    health_reasons: list[str]


class FormulacionIPR(BaseModel):
    id: str
    codigo_bip: str
    name: str
    phase: str
    days_in_phase: int
    has_mechanism: bool
    partes_count: int
    territorio_count: int
    hitos_count: int
    evaluaciones_count: int
    admisibilidad_total: int
    admisibilidad_verified: int
    eval_assigned: bool
    eval_result: str | None = None
    suggested_action: str
    suggested_tab: str


class MisFormulacionesResponse(BaseModel):
    total: int
    by_phase: dict[str, list[FormulacionIPR]]
