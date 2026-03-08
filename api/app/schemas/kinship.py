from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class KinshipDeclarationCreate(BaseModel):
    person_id: UUID
    declaration_type: str  # EVALUADOR | REPRESENTANTE_LEGAL | PERSONAL_CONTRATADO
    declares_no_conflict: bool
    related_authority_id: UUID | None = None
    relationship_type: str | None = None  # CONSANGUINIDAD | AFINIDAD
    relationship_degree: int | None = None  # 1-4


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


class KinshipDeclarationValidate(BaseModel):
    validated: bool
