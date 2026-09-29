"""
Bible service — data access layer for the bible schema.

All queries use the restricted owner-local PostgreSQL repository.
Bible data is public read-only reference data — no auth required for reads.
"""
from __future__ import annotations

from services.lexicon_service import match_metadata
from errors import DataIntegrityError, NotFoundError
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

from database import get_database


# ── Books ─────────────────────────────────────────────────────────────────────

def get_books() -> BooksListResponse:
    """Return all books ordered by testament + book_order."""
    db = get_database()
    resp = (
        db.read('book_read', order=('id',))
    )
    books = [BookResponse(**row) for row in resp]
    return BooksListResponse(data=books, total=len(books))


def get_book(osis_id: str) -> BookWithChaptersResponse:
    """Return a single book with its chapter list."""
    db = get_database()

    book_resp = (
        db.one('book_read', filters={'osis_id': osis_id}, order=())
    )
    if not book_resp:
        raise NotFoundError("Book", osis_id)

    ch_resp = (
        db.read('chapter_read', columns='id,chapter_num', filters={'book_id': book_resp['id']}, order=('chapter_num',))
    )

    if not ch_resp:
        raise DataIntegrityError(f"Incomplete Bible data: {osis_id} has no chapters")
    chapters = [ChapterSummary(**row) for row in ch_resp]
    return BookWithChaptersResponse(**book_resp, chapters=chapters)


# ── Chapters ──────────────────────────────────────────────────────────────────

def get_chapter(osis_id: str, chapter_num: int) -> ChapterWithVersesResponse:
    """Return a chapter with its verse list."""
    db = get_database()

    # Resolve book
    book_resp = (
        db.one('book_read', columns='id', filters={'osis_id': osis_id}, order=())
    )
    if not book_resp:
        raise NotFoundError("Book", osis_id)

    book_id = book_resp["id"]

    ch_resp = (
        db.one('chapter_read', columns='id,book_id,chapter_num', filters={'book_id': book_id, 'chapter_num': chapter_num}, order=())
    )
    if not ch_resp:
        raise NotFoundError("Chapter", f"{osis_id} {chapter_num}")

    chapter_id = ch_resp["id"]

    v_resp = (
        db.read('verse_read', columns='id,verse_num', filters={'chapter_id': chapter_id}, order=('verse_num',))
    )

    if not v_resp:
        raise DataIntegrityError(f"Incomplete Bible data: {osis_id} {chapter_num} has no verses")
    verses = [VerseSummary(**row) for row in v_resp]
    return ChapterWithVersesResponse(**ch_resp, verses=verses)


# ── Verses ────────────────────────────────────────────────────────────────────

def get_verses(osis_id: str, chapter_num: int) -> VersesListResponse:
    """Return all verses with words for a given chapter."""
    db = get_database()

    # Resolve book
    book_resp = (
        db.one('book_read', columns='id', filters={'osis_id': osis_id}, order=())
    )
    if not book_resp:
        raise NotFoundError("Book", osis_id)

    book_id = book_resp["id"]

    # Get verses for this chapter (using denorm columns for speed)
    v_resp = (
        db.read('verse_read', columns='id,verse_num,book_id,chapter_num', filters={'book_id': book_id, 'chapter_num': chapter_num}, order=('verse_num',))
    )

    if not v_resp:
        raise NotFoundError("Chapter", f"{osis_id} {chapter_num}")

    verse_ids = [row["id"] for row in v_resp]

    word_rows = (
        db.read('word_read', columns='id,verse_id,position,surface_he,display_he,lemma_strong,morph_code', in_filters={'verse_id': verse_ids}, order=('verse_id', 'position', 'id'))
    )

    # Group words by verse_id
    words_by_verse: dict[int, list[WordResponse]] = {vid: [] for vid in verse_ids}
    for w in word_rows:
        vid = w["verse_id"]
        if vid in words_by_verse:
            words_by_verse[vid].append(WordResponse(**w, **match_metadata(w.get('lemma_strong'), w.get('morph_code'))))

    for row in v_resp:
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
        for row in v_resp
    ]

    return VersesListResponse(data=verses, total=len(verses))


# ── Word morphology ───────────────────────────────────────────────────────────

def get_word_morphology(word_id: int) -> WordWithMorphologyResponse:
    """Return a word with its decoded morpheme breakdown."""
    db = get_database()

    w_resp = (
        db.one('word_read', columns='id,verse_id,position,surface_he,display_he,lemma_strong,morph_code', filters={'id': word_id}, order=())
    )
    if not w_resp:
        raise NotFoundError("Word", word_id)

    m_resp = (
        db.read('morpheme_read', columns='segment_index,language,part_of_speech,pos_code,gender,number,state,verb_stem,verb_aspect,person', filters={'word_id': word_id}, order=('segment_index',))
    )

    morph_code = w_resp.get("morph_code")
    if morph_code:
        expected = len(morph_code.split("/"))
        if [m["segment_index"] for m in m_resp] != list(range(expected)):
            raise DataIntegrityError(f"Incomplete Bible data: word {word_id} is missing morphology. Run the source audit/import.")
    # Preserve stored-row completeness checks, but derive presentation from the
    # immutable source code so historical imported feature errors need no writes.
    from dataclasses import asdict
    from services.oshb_morph import parse_morph_code
    morphemes = ([MorphemeResponse(segment_index=i, **asdict(segment))
                  for i, segment in enumerate(parse_morph_code(morph_code))]
                 if morph_code else [MorphemeResponse(**row) for row in m_resp])
    return WordWithMorphologyResponse(**w_resp, morphemes=morphemes, **match_metadata(w_resp.get('lemma_strong'), w_resp.get('morph_code')))


def get_occurrences(identity: str, book: str | None = None, offset: int = 0, limit: int = 25):
    """Exact content-lemma lookup over imported rows, stable canonical verse/word order.

    Fetch all matching variants directly, then join verse metadata in bounded batches.
    Counts come from stored corpus rows, without Data API row limits.
    """
    from services.lexicon_service import lemma_variants, lexical_id
    if lexical_id(identity) != identity:
        return {'data': [], 'total': 0, 'verse_total': 0, 'offset': offset, 'limit': limit}
    variants = lemma_variants().get(identity, [identity])
    db = get_database()
    words = (db.read('word_read', columns='id,verse_id,position,surface_he,display_he,lemma_strong', in_filters={'lemma_strong': variants}, order=('verse_id', 'position', 'id')))
    books = get_books().data
    by_id = {b.id: b for b in books}
    ids = sorted({w['verse_id'] for w in words})
    verses = {}
    for start in range(0, len(ids), 400):
        query = db.read('verse_read', columns='id,book_id,chapter_num,verse_num', in_filters={'id': ids[start:start + 400]}, order=('id',))
        if book:
            match = next((b for b in books if b.osis_id == book), None)
            if match is None:
                return {'data': [], 'total': 0, 'verse_total': 0, 'offset': offset, 'limit': limit}
            query = [v for v in query if v['book_id'] == match.id]
        verses.update({v['id']: v for v in query})
    result = []
    for word in words:
        verse = verses.get(word['verse_id'])
        if verse and verse['book_id'] in by_id:
            result.append({**word, 'book': by_id[verse['book_id']].osis_id, 'book_name': by_id[verse['book_id']].name_en, 'book_id': verse['book_id'], 'chapter': verse['chapter_num'], 'verse': verse['verse_num']})
    division_order = {'torah': 0, 'nevi_im': 1, 'ketuvim': 2}
    result.sort(key=lambda w: (division_order.get(by_id[w['book_id']].division, 3), by_id[w['book_id']].book_order, by_id[w['book_id']].osis_id, w['chapter'], w['verse'], w['position'], w['id']))
    return {'data': result[offset:offset + limit], 'total': len(result), 'verse_total': len({w['verse_id'] for w in result}), 'offset': offset, 'limit': limit}
