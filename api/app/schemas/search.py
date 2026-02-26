from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    code: str | None
    name: str
    entity_type: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
