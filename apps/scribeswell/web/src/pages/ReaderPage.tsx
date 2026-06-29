/**
 * ReaderPage — main Bible reader layout.
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────┐
 * │ Header: BookChapterSelector (compact dropdown)      │
 * │ Main: VerseReader                                   │
 * │ Right panel (when word selected): MorphologyPanel   │
 * └─────────────────────────────────────────────────────┘
 *
 * Navigation state lives in URL search params: ?book=Gen&chapter=1
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { BookChapterSelector } from "@/components/bible/book-chapter-selector";
import { VerseReader } from "@/components/bible/VerseReader";
import { MorphologyPanel } from "@/components/bible/MorphologyPanel";
import { useBooks, useVerses, useWordMorphology } from "@/hooks/useBible";
import type { WordResponse } from "@/schemas/bible.schema";

// Default navigation state — Genesis 1.
const DEFAULT_BOOK = "Gen";
const DEFAULT_CHAPTER = 1;

export function ReaderPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);

  // Derive navigation state from URL; fall back to defaults.
  const selectedOsisId: string =
    searchParams.get("book") ?? DEFAULT_BOOK;
  const selectedChapter: number =
    parseInt(searchParams.get("chapter") ?? String(DEFAULT_CHAPTER), 10) ||
    DEFAULT_CHAPTER;

  const books = useBooks();
  const verses = useVerses(selectedOsisId, selectedChapter);
  const morphology = useWordMorphology(selectedWord?.id ?? null);

  function handleSelect(osisId: string, chapterNum: number) {
    setSelectedWord(null);
    setSearchParams({ book: osisId, chapter: String(chapterNum) });
  }

  function handleWordClick(word: WordResponse) {
    setSelectedWord((prev: WordResponse | null) =>
      prev?.id === word.id ? null : word
    );
  }

  return (
    <div className="flex flex-col gap-4 min-h-[calc(100vh-3.5rem-3rem)]">
      {/* ── Navigation header ──────────────────────────────── */}
      {/* justify-end: selector sits at the right/RTL-start of the header */}
      <div className="flex items-center justify-end gap-3">
        {books.loading && (
          <span className="text-sm text-stone-400 animate-pulse">
            Loading…
          </span>
        )}
        {books.error && (
          <span className="text-sm text-red-500">Error: {books.error}</span>
        )}
        {books.data && (
          <BookChapterSelector
            books={books.data.data}
            selectedOsisId={selectedOsisId}
            selectedChapter={selectedChapter}
            onSelect={handleSelect}
          />
        )}
      </div>

      {/* ── Reader area ────────────────────────────────────── */}
      <div className="flex gap-6 flex-1">
        {/* Main content */}
        <main className="flex-1 min-w-0">
          {verses.loading && (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-8 bg-stone-200 rounded w-full" />
              ))}
            </div>
          )}
          {verses.error && (
            <p className="text-sm text-red-500">Error: {verses.error}</p>
          )}
          {verses.data && (
            <VerseReader
              verses={verses.data.data}
              selectedWordId={selectedWord?.id ?? null}
              onWordClick={handleWordClick}
            />
          )}
        </main>

        {/* Morphology panel (conditional) */}
        {selectedWord && (
          <aside className="w-72 shrink-0">
            {morphology.loading && (
              <div className="bg-white border border-stone-200 rounded-xl p-4 animate-pulse">
                <div className="h-8 bg-stone-200 rounded w-24 mb-3" />
                <div className="space-y-2">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-4 bg-stone-100 rounded" />
                  ))}
                </div>
              </div>
            )}
            {morphology.error && (
              <p className="text-sm text-red-500">Error: {morphology.error}</p>
            )}
            {morphology.data && (
              <MorphologyPanel
                word={morphology.data}
                onClose={() => setSelectedWord(null)}
              />
            )}
          </aside>
        )}
      </div>
    </div>
  );
}
