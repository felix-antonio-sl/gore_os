from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class KPICard(BaseModel):
    label: str
    value: int
    sublabel: str
    color: str  # "red" | "orange" | "amber" | "green" | "blue" | "gray"


class DashboardCommitment(BaseModel):
    id: UUID
    description: str
    ipr_codigo_bip: str | None
    responsible_name: str | None
    due_date: date
    state: str
    days_remaining: int


class DashboardAlert(BaseModel):
    id: UUID
    severity: str | None
    message: str
    subject_type: str
    subject_id: UUID
    triggered_at: datetime


class DashboardProblem(BaseModel):
    id: UUID
    ipr_codigo_bip: str | None
    problem_type: str
    days_open: int
    state: str


class DashboardResponse(BaseModel):
    kpis: list[KPICard]
    commitments: list[DashboardCommitment]
    alerts: list[DashboardAlert]
    problems: list[DashboardProblem]


class TeamMemberLoad(BaseModel):
    user_id: UUID
    name: str
    pendientes: int
    en_progreso: int
    completados: int
    vencidos: int
    total: int


class MiDivisionResponse(BaseModel):
    kpis: list[KPICard]
    team: list[TeamMemberLoad]
    commitments: list[DashboardCommitment]


class CompromisoGroup(BaseModel):
    label: str
    count: int
    items: list[DashboardCommitment]


class MisCompromisosResponse(BaseModel):
    kpis: list[KPICard]
    groups: list[CompromisoGroup]


class DivisionBreakdown(BaseModel):
    division_name: str
    vencidos: int
    total_compromisos: int
    problemas_abiertos: int
    ejecucion_pct: float


class SemaforoItem(BaseModel):
    dimension: str
    label: str
    signal: str
    indicator_count: int


class DashboardExecutivoResponse(DashboardResponse):
    divisions: list[DivisionBreakdown]
    semaforo: list[SemaforoItem] = []


class ChartDataPoint(BaseModel):
    name: str
    value: int
    color: str | None = None


class BudgetChartPoint(BaseModel):
    division: str
    ejecucion_pct: float
    pagado: float
    vigente: float


class ChartDataResponse(BaseModel):
    commitments_by_state: list[ChartDataPoint]
    alerts_by_severity: list[ChartDataPoint]
    budget_by_division: list[BudgetChartPoint]


class ActionItem(BaseModel):
    id: str
    category: str
    title: str
    subtitle: str | None = None
    deadline: date | None = None
    days_remaining: int | None = None
    temporal: str | None = None
    severity: str
    priority: int
    action_label: str
    action_route: str
    ipr_id: str | None = None
    ipr_codigo_bip: str | None = None


class ActionItemsResponse(BaseModel):
    greeting_name: str
    today: date
    summary: str
    items: list[ActionItem]
    counts: dict[str, int]
