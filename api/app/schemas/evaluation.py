from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class EvaluationAssignmentCreate(BaseModel):
    evaluator_type_id: UUID | None = None
    evaluator_organization_id: UUID | None = None
    evaluator_name: str | None = None
    deadline_at: datetime | None = None


class EvaluationAssignmentUpdate(BaseModel):
    result_id: UUID | None = None
    observations: str | None = None
    completed_at: datetime | None = None
    deadline_at: datetime | None = None


class EvaluationAssignmentItem(BaseModel):
    id: UUID
    ipr_id: UUID
    evaluator_type: str
    evaluator_type_label: str | None = None
    evaluator_org_name: str | None = None
    evaluator_name: str | None = None
    assigned_at: datetime
    deadline_at: datetime | None = None
    completed_at: datetime | None = None
    result_code: str | None = None
    result_label: str | None = None
    observations: str | None = None
