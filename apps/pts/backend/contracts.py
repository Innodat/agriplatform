from typing import Any, Literal
from pydantic import BaseModel, Field

class Selection(BaseModel):
    schema_version: str
    exported_at: str
    note: str
    poems: list[dict[str, Any]]
    witnesses: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    rights: list[dict[str, Any]]
    source_documents: list[dict[str, Any]]

class CollectionResponse(Selection):
    total: int
    collection_total: int
    filters: dict[str, list[str]]
    citations: dict[str,str]

class PoemResponse(BaseModel):
    poem: dict[str, Any]
    evidence: Selection
    citation: str

class DocumentResponse(BaseModel):
    status: Literal['stored','link_only']
    url: str
    expires_in: int | None = None
    document: dict[str, Any]

class FilterQuery(BaseModel):
    search: str = Field(default='',max_length=300)
    availability: Literal['all','text','checked','review'] = 'text'
    source: str = ''
    genre: str = ''
    origin: str = ''
    dialect: str = ''
    status: str = ''

class SourcesResponse(BaseModel):
    sources: list[dict[str, Any]]
    rights: list[dict[str, Any]]
    source_documents: list[dict[str, Any]]
