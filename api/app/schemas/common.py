from pydantic import BaseModel
from uuid import UUID


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryRef(BaseModel):
    id: UUID
    code: str
    label: str


class MessageResponse(BaseModel):
    message: str
