/**
 * Data-fetching hooks for the Bible reader.
 * All calls go through the api-client → FastAPI → Supabase.
 */
import { useState, useEffect, useCallback } from "react";
import {
  getBooks,
  getBook,
  getVerses,
  getWordMorphology,
} from "@/lib/api-client";
import type {
  BooksListResponse,
  BookWithChaptersResponse,
  VersesListResponse,
  WordWithMorphologyResponse,
} from "@/schemas/bible.schema";

// ── Generic async hook ────────────────────────────────────────────────────────

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useAsync<T>(
  fn: () => Promise<T>,
  deps: unknown[]
): AsyncState<T> & { refetch: () => void } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const run = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    fn()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: unknown) =>
        setState({
          data: null,
          loading: false,
          error: err instanceof Error ? err.message : "Unknown error",
        })
      );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    run();
  }, [run]);

  return { ...state, refetch: run };
}

// ── Public hooks ──────────────────────────────────────────────────────────────

export function useBooks() {
  return useAsync<BooksListResponse>(() => getBooks(), []);
}

export function useBook(osisId: string | null) {
  return useAsync<BookWithChaptersResponse | null>(
    () => (osisId ? getBook(osisId) : Promise.resolve(null)),
    [osisId]
  );
}

export function useVerses(osisId: string | null, chapterNum: number | null) {
  return useAsync<VersesListResponse | null>(
    () =>
      osisId && chapterNum
        ? getVerses(osisId, chapterNum)
        : Promise.resolve(null),
    [osisId, chapterNum]
  );
}

export function useWordMorphology(wordId: number | null) {
  return useAsync<WordWithMorphologyResponse | null>(
    () => (wordId ? getWordMorphology(wordId) : Promise.resolve(null)),
    [wordId]
  );
}
