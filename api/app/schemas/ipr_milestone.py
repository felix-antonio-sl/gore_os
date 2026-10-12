from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class IprMilestoneItem(BaseModel):
    id: UUID
    milestone_type_code: str
    milestone_type_label: str
    description: str | None
    planned_date: date
    actual_date: date | None
    deviation_days: int | None
    completed_by_name: str | None
    verification_notes: str | None
    created_at: datetime
