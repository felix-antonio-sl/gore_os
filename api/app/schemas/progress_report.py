from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class ProgressReportCreate(BaseModel):
    report_date: date
    physical_progress: float | None = None
    financial_progress: float | None = None
    description: str | None = None
    issues_detected: str | None = None


class ProgressReportItem(BaseModel):
    id: UUID
    report_number: int
    report_date: date
    physical_progress: float | None
    financial_progress: float | None
    description: str | None
    issues_detected: str | None
    reported_by_name: str | None
    created_at: datetime
