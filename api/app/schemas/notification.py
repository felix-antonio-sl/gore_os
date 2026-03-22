from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class NotificationItem(BaseModel):
    id: UUID
    title: str
    body: str | None
    category: str
    entity_type: str | None
    entity_id: UUID | None
    link: str | None
    read_at: datetime | None
    created_at: datetime


class NotificationUnreadCount(BaseModel):
    count: int


class NotificationCreate(BaseModel):
    title: str
    body: str | None = None
    category: str
    entity_type: str | None = None
    entity_id: UUID | None = None
    link: str | None = None
