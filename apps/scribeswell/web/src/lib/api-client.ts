/**
 * Bible API client — thin fetch wrapper over FastAPI /api/bible/*
 *
 * All endpoints are public (no auth required).
 * Base URL is proxied via Vite dev server → http://localhost:8000
 */

import {
  BooksListResponseSchema,
  BookWithChaptersResponseSchema,
  ChapterWithVersesResponseSchema,
  VersesListResponseSchema,
  WordWithMorphologyResponseSchema,
  type BooksListResponse,
  type BookWithChaptersResponse,
  type ChapterWithVersesResponse,
  type VersesListResponse,
  type WordWithMorphologyResponse,
} from "@/schemas/bible.schema";

const BASE = "/api/bible";

async function apiFetch<T>(
  url: string,
  schema: { parse: (data: unknown) => T },
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, { headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      (body as { error?: string }).error ?? `HTTP ${res.status}`
    );
  }

  const data = await res.json();
  return schema.parse(data);
}

// ── Books ─────────────────────────────────────────────────────────────────────

export async function getBooks(token?: string): Promise<BooksListResponse> {
  return apiFetch(`${BASE}/books`, BooksListResponseSchema, token);
}

export async function getBook(
  osisId: string,
  token?: string
): Promise<BookWithChaptersResponse> {
  return apiFetch(
    `${BASE}/books/${encodeURIComponent(osisId)}`,
    BookWithChaptersResponseSchema,
    token
  );
}

// ── Chapters ──────────────────────────────────────────────────────────────────

export async function getChapter(
  osisId: string,
  chapterNum: number,
  token?: string
): Promise<ChapterWithVersesResponse> {
  return apiFetch(
    `${BASE}/books/${encodeURIComponent(osisId)}/chapters/${chapterNum}`,
    ChapterWithVersesResponseSchema,
    token
  );
}

// ── Verses ────────────────────────────────────────────────────────────────────

export async function getVerses(
  osisId: string,
  chapterNum: number,
  token?: string
): Promise<VersesListResponse> {
  return apiFetch(
    `${BASE}/books/${encodeURIComponent(osisId)}/chapters/${chapterNum}/verses`,
    VersesListResponseSchema,
    token
  );
}

// ── Morphology ────────────────────────────────────────────────────────────────

export async function getWordMorphology(
  wordId: number,
  token?: string
): Promise<WordWithMorphologyResponse> {
  return apiFetch(
    `${BASE}/words/${wordId}/morphology`,
    WordWithMorphologyResponseSchema,
    token
  );
}
