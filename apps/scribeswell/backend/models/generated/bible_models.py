# GENERATED — do not edit
# Source: Supabase bible schema — Phase 1
# Regenerate with: python apps/scribeswell/tools/generate_models.py

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class BookRow(BaseModel):
    id: int
    osis_id: str
    name_en: str
    name_he: str
    testament: str  # 'torah' | 'nevi_im' | 'ketuvim'
    book_order: int


class ChapterRow(BaseModel):
    id: int
    book_id: int
    chapter_num: int


class VerseRow(BaseModel):
    id: int
    chapter_id: int
    verse_num: int
    book_id: int
    chapter_num: int


class WordRow(BaseModel):
    id: int
    verse_id: int
    position: int
    surface_he: str
    display_he: Optional[str] = None
    lemma_strong: Optional[str] = None
    morph_code: Optional[str] = None


class MorphemeRow(BaseModel):
    id: int
    word_id: int
    segment_index: int
    language: str           # 'hebrew' | 'aramaic'
    part_of_speech: str
    pos_code: str
    gender: Optional[str] = None
    number: Optional[str] = None
    state: Optional[str] = None
    verb_stem: Optional[str] = None
    verb_aspect: Optional[str] = None
    person: Optional[str] = None
