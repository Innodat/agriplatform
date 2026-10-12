from typing import Any, Literal
from pydantic import BaseModel, Field

class ResearchAssessment(BaseModel):
    scope: Literal['private_noncommercial_psalm_ai_training']
    status: Literal['allowed','conditional','review']
    label: str
    summary: str
    conditions: list[str]
    eligible_for_private_training: bool
    public_release_assessed: Literal[False] = False
    source_id: str
    rights_id: str

class Selection(BaseModel):
    schema_version: str
    exported_at: str
    note: str
    poems: list[dict[str, Any]]
    witnesses: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    rights: list[dict[str, Any]]
    source_documents: list[dict[str, Any]]
    research_purpose: str = ''
    research_usage: dict[str,ResearchAssessment] = Field(default_factory=dict)

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
    availability: Literal['all','text','checked','review','research'] = 'text'
    source: str = ''
    genre: str = ''
    origin: str = ''
    dialect: str = ''
    status: str = ''

class SourcesResponse(BaseModel):
    sources: list[dict[str, Any]]
    rights: list[dict[str, Any]]
    source_documents: list[dict[str, Any]]
    research_purpose: str = ''
    research_usage: dict[str,ResearchAssessment] = Field(default_factory=dict)

    acquisition: dict[str,dict[str,Any]] = Field(default_factory=dict)
    acquisition_leads: list[dict[str,Any]] = Field(default_factory=list)
