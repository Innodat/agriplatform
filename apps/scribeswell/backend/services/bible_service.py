"""
Bible service — data access layer for the bible schema.

All queries use the Supabase service-role client (reads from bible.* tables).
Bible data is public read-only reference data — no auth required for reads.
"""
from __future__ import annotations

from config import settings
from errors import DataIntegrityError, NotFoundError
from pagination import fetch_all
from schemas.bible_schemas import (
    BookResponse,
    BooksListResponse,
    BookWithChaptersResponse,
    ChapterSummary,
    ChapterWithVersesResponse,
    MorphemeResponse,
    VersesListResponse,
    VerseSummary,
    VerseWithWordsResponse,
    WordResponse,
    WordWithMorphologyResponse,
)

from supabase import Client, create_client


def _get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_secret_key)


# ── Books ─────────────────────────────────────────────────────────────────────

def get_books() -> BooksListResponse:
    """Return all books ordered by testament + book_order."""
    sb = _get_client()
    resp = (
        sb.schema("scribeswell")
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
        sb.schema("scribeswell")
        .table("book_read")
        .select("*")
        .eq("osis_id", osis_id)
        .single()
        .execute()
    )
    if not book_resp.data:
        raise NotFoundError("Book", osis_id)

    ch_resp = (
        sb.schema("scribeswell")
        .table("chapter_read")
        .select("id,chapter_num")
        .eq("book_id", book_resp.data["id"])
        .order("chapter_num")
        .execute()
    )

    if not ch_resp.data:
        raise DataIntegrityError(f"Incomplete Bible data: {osis_id} has no chapters")
    chapters = [ChapterSummary(**row) for row in ch_resp.data]
    return BookWithChaptersResponse(**book_resp.data, chapters=chapters)


# ── Chapters ──────────────────────────────────────────────────────────────────

def get_chapter(osis_id: str, chapter_num: int) -> ChapterWithVersesResponse:
    """Return a chapter with its verse list."""
    sb = _get_client()

    # Resolve book
    book_resp = (
        sb.schema("scribeswell")
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
        sb.schema("scribeswell")
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
        sb.schema("scribeswell")
        .table("verse_read")
        .select("id,verse_num")
        .eq("chapter_id", chapter_id)
        .order("verse_num")
        .execute()
    )

    if not v_resp.data:
        raise DataIntegrityError(f"Incomplete Bible data: {osis_id} {chapter_num} has no verses")
    verses = [VerseSummary(**row) for row in v_resp.data]
    return ChapterWithVersesResponse(**ch_resp.data, verses=verses)


# ── Verses ────────────────────────────────────────────────────────────────────

def get_verses(osis_id: str, chapter_num: int) -> VersesListResponse:
    """Return all verses with words for a given chapter."""
    sb = _get_client()

    # Resolve book
    book_resp = (
        sb.schema("scribeswell")
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
        sb.schema("scribeswell")
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

    word_rows = fetch_all(
        sb.schema("scribeswell").table("word_read")
        .select("id,verse_id,position,surface_he,display_he,lemma_strong,morph_code", count="exact")
        .in_("verse_id", verse_ids).order("verse_id").order("position").order("id")
    )

    # Group words by verse_id
    words_by_verse: dict[int, list[WordResponse]] = {vid: [] for vid in verse_ids}
    for w in word_rows:
        vid = w["verse_id"]
        if vid in words_by_verse:
            words_by_verse[vid].append(WordResponse(**w))

    for row in v_resp.data:
        words = words_by_verse[row["id"]]
        reference = f"{osis_id} {chapter_num}:{row['verse_num']}"
        if not words or any(not w.surface_he.strip() for w in words):
            raise DataIntegrityError(f"Incomplete Bible data at {reference}: Hebrew words are missing. Run the source audit/import.")
        if [w.position for w in words] != list(range(1, len(words) + 1)):
            raise DataIntegrityError(f"Incomplete Bible data at {reference}: word positions are not contiguous. Run the source audit/import.")

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
        sb.schema("scribeswell")
        .table("word_read")
        .select("id,verse_id,position,surface_he,display_he,lemma_strong,morph_code")
        .eq("id", word_id)
        .single()
        .execute()
    )
    if not w_resp.data:
        raise NotFoundError("Word", word_id)

    m_resp = (
        sb.schema("scribeswell")
        .table("morpheme_read")
        .select(
            "segment_index,language,part_of_speech,pos_code,"
            "gender,number,state,verb_stem,verb_aspect,person"
        )
        .eq("word_id", word_id)
        .order("segment_index")
        .execute()
    )

    morph_code = w_resp.data.get("morph_code")
    if morph_code:
        expected = len(morph_code.split("/"))
        if [m["segment_index"] for m in m_resp.data] != list(range(expected)):
            raise DataIntegrityError(f"Incomplete Bible data: word {word_id} is missing morphology. Run the source audit/import.")
    morphemes = [MorphemeResponse(**row) for row in m_resp.data]
    return WordWithMorphologyResponse(**w_resp.data, morphemes=morphemes)
