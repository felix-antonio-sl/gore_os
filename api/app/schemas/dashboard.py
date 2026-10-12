from pydantic import BaseModel
from datetime import date


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
    state: str | None = None
    state_label: str | None = None
    responsible_id: str | None = None
    responsible_name: str | None = None


class ActionItemsResponse(BaseModel):
    greeting_name: str
    today: date
    summary: str
    items: list[ActionItem]
    counts: dict[str, int]
    scope_label: str = "Atención institucional"
    limited_sources: list[str] = []
