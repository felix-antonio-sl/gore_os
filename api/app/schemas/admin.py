from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class UserListItem(BaseModel):
    id: UUID
    email: str
    names: str
    paternal_surname: str
    maternal_surname: str | None
    role_code: str
    role_label: str
    division_name: str | None
    is_active: bool
    created_at: datetime


class UserDetail(UserListItem):
    division_id: UUID | None
    system_role_id: UUID
    phone: str | None
    rut: str | None


class UserCreate(BaseModel):
    names: str
    paternal_surname: str
    maternal_surname: str | None = None
    email: str
    password: str = Field(min_length=8)
    system_role_id: UUID
    division_id: UUID | None = None
    rut: str | None = None
    phone: str | None = None


class UserUpdate(BaseModel):
    names: str | None = None
    paternal_surname: str | None = None
    maternal_surname: str | None = None
    email: str | None = None
    system_role_id: UUID | None = None
    division_id: UUID | None = None
    phone: str | None = None


class DivisionListItem(BaseModel):
    id: UUID
    code: str
    name: str
    organization_type: str | None
    is_active: bool
    user_count: int


class DivisionCreate(BaseModel):
    code: str
    name: str
    organization_type_id: UUID | None = None


class DivisionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
