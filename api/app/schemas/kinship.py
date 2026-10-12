from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class KinshipDeclarationItem(BaseModel):
    id: UUID
    ipr_id: UUID
    person_id: UUID
    person_name: str
    person_rut: str | None
    declaration_type: str
    declares_no_conflict: bool
    related_authority_id: UUID | None
    related_authority_name: str | None = None
    relationship_type: str | None
    relationship_degree: int | None
    declared_at: datetime
    validated_by_id: UUID | None
    validated_at: datetime | None
