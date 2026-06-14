"""
Bible router — public read-only endpoints.

All endpoints are public (no auth required).
Optional JWT is accepted for future user-settings features.

Routes:
    GET /api/bible/books                          → list all books
    GET /api/bible/books/{osis_id}                → book + chapter list
    GET /api/bible/books/{osis_id}/chapters/{n}   → chapter + verse list
    GET /api/bible/books/{osis_id}/chapters/{n}/verses → verses with words
    GET /api/bible/words/{word_id}/morphology     → word + decoded morphemes
"""
from fastapi import APIRouter, Path

from auth.jwt_optional import OptionalUser
from schemas.bible_schemas import (
    BooksListResponse,
    BookWithChaptersResponse,
    ChapterWithVersesResponse,
    VersesListResponse,
    WordWithMorphologyResponse,
)
from services import bible_service

router = APIRouter()


@router.get(
    "/books",
    response_model=BooksListResponse,
    summary="List all books",
    description="Returns all 39 Tanakh books ordered by canonical id.",
)
async def list_books(user: OptionalUser = None):
    return bible_service.get_books()


@router.get(
    "/books/{osis_id}",
    response_model=BookWithChaptersResponse,
    summary="Get book with chapters",
    description="Returns a book and its chapter list by OSIS id (e.g. Gen, Exod).",
)
async def get_book(
    osis_id: str = Path(..., description="OSIS book id, e.g. 'Gen'"),
    user: OptionalUser = None,
):
    return bible_service.get_book(osis_id)


@router.get(
    "/books/{osis_id}/chapters/{chapter_num}",
    response_model=ChapterWithVersesResponse,
    summary="Get chapter with verse list",
    description="Returns a chapter and its verse numbers.",
)
async def get_chapter(
    osis_id: str = Path(..., description="OSIS book id"),
    chapter_num: int = Path(..., ge=1, description="Chapter number"),
    user: OptionalUser = None,
):
    return bible_service.get_chapter(osis_id, chapter_num)


@router.get(
    "/books/{osis_id}/chapters/{chapter_num}/verses",
    response_model=VersesListResponse,
    summary="Get verses with words",
    description="Returns all verses in a chapter, each with their Hebrew words.",
)
async def get_verses(
    osis_id: str = Path(..., description="OSIS book id"),
    chapter_num: int = Path(..., ge=1, description="Chapter number"),
    user: OptionalUser = None,
):
    return bible_service.get_verses(osis_id, chapter_num)


@router.get(
    "/words/{word_id}/morphology",
    response_model=WordWithMorphologyResponse,
    summary="Get word morphology",
    description=(
        "Returns a word with its decoded OSHB morpheme breakdown. "
        "Each morpheme includes part of speech, gender, number, state, "
        "verb stem, verb aspect, and person where applicable."
    ),
)
async def get_word_morphology(
    word_id: int = Path(..., ge=1, description="Word id"),
    user: OptionalUser = None,
):
    return bible_service.get_word_morphology(word_id)
