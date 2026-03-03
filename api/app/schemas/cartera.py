from pydantic import BaseModel
from uuid import UUID


class CarteraIPRItem(BaseModel):
    """IPR with aggregated portfolio data for DGI monitoring."""
    id: UUID
    codigo_bip: str
    name: str
    mechanism: str | None
    mcd_phase: str | None
    division_name: str | None
    division_id: UUID | None
    monto_total: float | None

    # Health signal
    health_signal: str  # VERDE, AMARILLO, ROJO
    health_reasons: list[str]

    # Temporal
    days_since_update: int

    # Progress
    physical_progress: float | None
    financial_progress: float | None

    # Budget (CDPs)
    cdp_total: float
    cdp_paid: float
    budget_execution_pct: float | None

    # Agreements
    agreement_count: int
    agreement_latest_state: str | None
    overdue_installments: int

    # Resolutions
    resolution_count: int
    pending_cgr: int

    # Operational
    open_problems: int
    active_alerts: int
    critical_alerts: int
    overdue_commitments: int


class CarteraSummary(BaseModel):
    """Summary cards for the portfolio dashboard."""
    total: int
    verde: int
    amarillo: int
    rojo: int
    overdue_installments_total: int
    pending_cgr_total: int
    monto_total: float
    total_paid: float


class CuotaVencidaItem(BaseModel):
    """Overdue installment across all agreements."""
    id: UUID
    ipr_id: UUID | None
    ipr_codigo_bip: str | None
    agreement_id: UUID
    agreement_number: str | None
    counterpart_name: str | None
    installment_number: int
    amount: float
    due_date: str
    days_overdue: int
