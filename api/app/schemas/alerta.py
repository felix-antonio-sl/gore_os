from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AlertaListItem(BaseModel):
    id: UUID
    alert_type: str
    alert_type_label: str
    severity: str | None
    severity_label: str | None
    subject_type: str
    subject_id: UUID
    subject_label: str | None
    message: str
    triggered_at: datetime
    acknowledged_at: datetime | None
    attended_at: datetime | None
    resolved_at: datetime | None


class AlertaAttendRequest(BaseModel):
    action_taken: str = "Atendida"
