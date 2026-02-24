from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProblemaListItem(BaseModel):
    id: UUID
    code: str | None
    ipr_id: UUID
    ipr_codigo_bip: str | None
    ipr_name: str | None
    problem_type: str
    problem_type_label: str
    impact: str | None
    impact_label: str | None
    description: str
    state: str
    state_label: str
    days_open: int
    detected_at: datetime


class ProblemaDetail(BaseModel):
    id: UUID
    code: str | None
    ipr_id: UUID
    ipr_codigo_bip: str | None
    ipr_name: str | None
    problem_type: str
    problem_type_label: str
    impact: str | None
    impact_label: str | None
    description: str
    impact_description: str | None
    state: str
    state_label: str
    days_open: int
    detected_by_name: str | None
    detected_at: datetime
    proposed_solution: str | None
    solution_applied: str | None
    resolved_by_name: str | None
    resolved_at: datetime | None
    created_at: datetime


class ProblemaCreate(BaseModel):
    ipr_id: UUID
    problem_type_id: UUID
    impact_id: UUID | None = None
    description: str
    impact_description: str | None = None
    proposed_solution: str | None = None


class ProblemaUpdate(BaseModel):
    state_id: UUID | None = None
    proposed_solution: str | None = None
    solution_applied: str | None = None
