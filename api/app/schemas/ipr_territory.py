from pydantic import BaseModel
from uuid import UUID


class IprTerritoryItem(BaseModel):
    id: UUID
    territory_name: str
    territory_code: str | None
    impact_type_code: str
    impact_type_label: str
    is_primary: bool
    notes: str | None
