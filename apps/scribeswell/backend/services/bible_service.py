"""
Bible service — data access layer for the bible schema.

All queries use the Supabase service-role client (reads from bible.* tables).
Bible data is public read-only reference data — no auth required for reads.
"""
from __future__ import annotations
from typing import Optional
from supabase import create_client, Client

from config import settings
from errors import NotFoundError
from schemas.bible_schemas import (
    BookResponse,
    BookWithChaptersResponse,
    ChapterSummary,
    ChapterWithVersesResponse,
    VerseSummary,
    VerseWithWordsResponse,
    WordResponse,
    WordWithMorphologyResponse,
    MorphemeResponse,
    BooksListResponse,
    VersesListResponse,
)


def _get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)


# ── Books ─────────────────────────────────────────────────────────────────────

def get_books() -> BooksListResponse:
    """Return all books ordered by testament + book_order."""
    sb = _get_client()
    resp = (
        sb.schema("bible")
        .table("book_read")
        .select("*")
        .order("id")
        .execute()
    )
    books = [BookResponse(**row) for row in resp.data]
    return BooksListResponse(data=books, total=len(books))


def get_book(osis_id: str) -> BookWithChaptersResponse:
    """Return a single book with its chapter list."""
    sb = _get_client()

    book_resp = (
        sb.schema("bible")
        .table("book_read")
        .select("*")
        .eq("osis_id", osis_id)
        .single()
        .execute()
    )
    if not book_resp.data:
        raise NotFoundError("Book", osis_id)

    ch_resp = (
        sb.schema("bible")
        .table("chapter_read")
        .select("id,chapter_num")
        .eq("book_id", book_resp.data["id"])
        .order("chapter_num")
        .execute()
    )

    chapters = [ChapterSummary(**row) for row in ch_resp.data]
    return BookWithChaptersResponse(**book_resp.data, chapters=chapters)


# ── Chapters ──────────────────────────────────────────────────────────────────

def get_chapter(osis_id: str, chapter_num: int) -> ChapterWithVersesResponse:
    """Return a chapter with its verse list."""
    sb = _get_client()

    # Resolve book
    book_resp = (
        sb.schema("bible")
        .table("book_read")
        .select("id")
        .eq("osis_id", osis_id)
        .single()
        .execute()
    )
    if not book_resp.data:
        raise NotFoundError("Book", osis_id)

    book_id = book_resp.data["id"]

    ch_resp = (
        sb.schema("bible")
        .table("chapter_read")
        .select("id,book_id,chapter_num")
        .eq("book_id", book_id)
        .eq("chapter_num", chapter_num)
        .single()
        .execute()
    )
    if not ch_resp.data:
        raise NotFoundError("Chapter", f"{osis_id} {chapter_num}")

    chapter_id = ch_resp.data["id"]

    v_resp = (
        sb.schema("bible")
        .table("verse_read")
        .select("id,verse_num")
        .eq("chapter_id", chapter_id)
        .order("verse_num")
        .execute()
    )

    verses = [VerseSummary(**row) for row in v_resp.data]
    return ChapterWithVersesResponse(**ch_resp.data, verses=verses)


# ── Verses ────────────────────────────────────────────────────────────────────

def get_verses(osis_id: str, chapter_num: int) -> VersesListResponse:
    """Return all verses with words for a given chapter."""
    sb = _get_client()

    # Resolve book
    book_resp = (
        sb.schema("bible")
        .table("book_read")
        .select("id")
        .eq("osis_id", osis_id)
        .single()
        .execute()
    )
    if not book_resp.data:
        raise NotFoundError("Book", osis_id)

    book_id = book_resp.data["id"]

    # Get verses for this chapter (using denorm columns for speed)
    v_resp = (
        sb.schema("bible")
        .table("verse_read")
        .select("id,verse_num,book_id,chapter_num")
        .eq("book_id", book_id)
        .eq("chapter_num", chapter_num)
        .order("verse_num")
        .execute()
    )

    if not v_resp.data:
        raise NotFoundError("Chapter", f"{osis_id} {chapter_num}")

    verse_ids = [row["id"] for row in v_resp.data]

    # Fetch all words for these verses in one query
    w_resp = (
        sb.schema("bible")
        .table("word_read")
        .select("id,verse_id,position,surface_he,display_he,lemma_strong,morph_code")
        .in_("verse_id", verse_ids)
        .order("position")
        .execute()
    )

    # Group words by verse_id
    words_by_verse: dict[int, list[WordResponse]] = {vid: [] for vid in verse_ids}
    for w in w_resp.data:
        vid = w["verse_id"]
        if vid in words_by_verse:
            words_by_verse[vid].append(WordResponse(**w))

    verses = [
        VerseWithWordsResponse(
            **row,
            words=words_by_verse.get(row["id"], []),
        )
        for row in v_resp.data
    ]

    return VersesListResponse(data=verses, total=len(verses))


# ── Word morphology ───────────────────────────────────────────────────────────

def get_word_morphology(word_id: int) -> WordWithMorphologyResponse:
    """Return a word with its decoded morpheme breakdown."""
    sb = _get_client()

    w_resp = (
        sb.schema("bible")
        .table("word_read")
        .select("id,verse_id,position,surface_he,display_he,lemma_strong,morph_code")
        .eq("id", word_id)
        .single()
        .execute()
    )
    if not w_resp.data:
        raise NotFoundError("Word", word_id)

    m_resp = (
        sb.schema("bible")
        .table("morpheme_read")
        .select(
            "segment_index,language,part_of_speech,pos_code,"
            "gender,number,state,verb_stem,verb_aspect,person"
        )
        .eq("word_id", word_id)
        .order("segment_index")
        .execute()
    )

    morphemes = [MorphemeResponse(**row) for row in m_resp.data]
    return WordWithMorphologyResponse(**w_resp.data, morphemes=morphemes)
