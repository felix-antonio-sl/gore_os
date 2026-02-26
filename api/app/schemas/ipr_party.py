from pydantic import BaseModel
from uuid import UUID
from datetime import date


class IprPartyCreate(BaseModel):
    organization_id: UUID
    party_role_id: UUID
    agreement_id: UUID | None = None
    is_primary: bool = False
    valid_from: date | None = None
    valid_to: date | None = None
    responsibility_description: str | None = None
    contact_person: str | None = None
    contact_email: str | None = None


class IprPartyItem(BaseModel):
    id: UUID
    organization_name: str
    organization_code: str | None
    role_code: str
    role_label: str
    is_primary: bool
    valid_from: date | None
    valid_to: date | None
    contact_person: str | None
    contact_email: str | None
    responsibility_description: str | None
    agreement_number: str | None
