from pydantic import BaseModel, Field
from uuid import UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: UUID
    email: str
    nombre: str
    apellido_paterno: str
    role_code: str
    role_label: str
    division_id: UUID | None
    population: str  # "operativa" | "dgi"
