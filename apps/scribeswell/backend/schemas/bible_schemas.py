"""
Bible API — Pydantic request/response schemas
These are the shapes returned by the FastAPI endpoints (not raw DB rows).
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


# ── Response schemas ──────────────────────────────────────────────────────────

class BookResponse(BaseModel):
    id: int
    osis_id: str
    name_en: str
    name_he: str
    testament: str
    division: str
    book_order: int


class ChapterSummary(BaseModel):
    id: int
    chapter_num: int


class BookWithChaptersResponse(BookResponse):
    chapters: list[ChapterSummary]


class VerseSummary(BaseModel):
    id: int
    verse_num: int


class ChapterWithVersesResponse(BaseModel):
    id: int
    book_id: int
    chapter_num: int
    verses: list[VerseSummary]


class MorphemeResponse(BaseModel):
    segment_index: int
    language: str
    part_of_speech: str
    pos_code: str
    gender: Optional[str] = None
    number: Optional[str] = None
    state: Optional[str] = None
    verb_stem: Optional[str] = None
    verb_aspect: Optional[str] = None
    person: Optional[str] = None


class WordResponse(BaseModel):
    id: int
    position: int
    surface_he: str
    display_he: Optional[str] = None
    lemma_strong: Optional[str] = None
    morph_code: Optional[str] = None
    lexical_id: Optional[str] = None
    match_key: Optional[str] = None


class WordWithMorphologyResponse(WordResponse):
    morphemes: list[MorphemeResponse]


class VerseWithWordsResponse(BaseModel):
    id: int
    verse_num: int
    book_id: int
    chapter_num: int
    words: list[WordResponse]


# ── List wrappers ─────────────────────────────────────────────────────────────

class BooksListResponse(BaseModel):
    data: list[BookResponse]
    total: int


class VersesListResponse(BaseModel):
    data: list[VerseWithWordsResponse]
    total: int


class LexiconNode(BaseModel):
    lexical_id: str | None = None
    language: str | None = None
    direction: str | None = None
    kind: str
    text: str
    children: list['LexiconNode'] = []
    book: str | None = None
    chapter: int | None = None
    verse: int | None = None


class LexiconRoot(BaseModel):
    lexical_id: str | None = None
    id: str
    text: str


class LexiconResponse(BaseModel):
    status: str
    lexical_id: str
    entry_id: str | None = None
    lemma: str = ''
    transliteration: str = ''
    definition: str = ''
    root: LexiconRoot | None = None
    pronunciation: str = ''
    strong_definition: str = ''
    strong_usage: str = ''
    strong_source: str = ''
    strong_definition_nodes: list[LexiconNode] = []
    strong_usage_nodes: list[LexiconNode] = []
    strong_source_nodes: list[LexiconNode] = []
    bdb: list[LexiconNode] = []
    bdb_status: str = 'missing'


class OccurrenceResponse(BaseModel):
    id: int
    position: int
    surface_he: str
    display_he: str | None = None
    book: str
    book_name: str
    chapter: int
    verse: int


class OccurrencesResponse(BaseModel):
    data: list[OccurrenceResponse]
    total: int
    verse_total: int
    offset: int
    limit: int
