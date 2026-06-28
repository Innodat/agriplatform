/**
 * ReaderPage — main Bible reader layout.
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────┐
 * │ Left sidebar: BookList + ChapterNav                 │
 * │ Main: VerseReader                                   │
 * │ Right panel (when word selected): MorphologyPanel   │
 * └─────────────────────────────────────────────────────┘
 */
import { useState } from "react";
import { BookList } from "@/components/bible/BookList";
import { ChapterNav } from "@/components/bible/ChapterNav";
import { VerseReader } from "@/components/bible/VerseReader";
import { MorphologyPanel } from "@/components/bible/MorphologyPanel";
import { useBooks, useBook, useVerses, useWordMorphology } from "@/hooks/useBible";
import type { WordResponse } from "@/schemas/bible.schema";

export function ReaderPage() {
  const [selectedOsisId, setSelectedOsisId] = useState<string | null>("Gen");
  const [selectedChapter, setSelectedChapter] = useState<number | null>(1);
  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);

  const books = useBooks();
  const book = useBook(selectedOsisId);
  const verses = useVerses(selectedOsisId, selectedChapter);
  const morphology = useWordMorphology(selectedWord?.id ?? null);

  function handleBookSelect(osisId: string) {
    setSelectedOsisId(osisId);
    setSelectedChapter(1);
    setSelectedWord(null);
  }

  function handleChapterSelect(chapterNum: number) {
    setSelectedChapter(chapterNum);
    setSelectedWord(null);
  }

  function handleWordClick(word: WordResponse) {
    setSelectedWord((prev: WordResponse | null) => (prev?.id === word.id ? null : word));
  }

  return (
    <div className="flex gap-6 min-h-[calc(100vh-3.5rem-3rem)]">
      {/* ── Left sidebar ─────────────────────────────────────── */}
      <aside className="w-56 shrink-0 overflow-y-auto">
        {books.loading && (
          <p className="text-sm text-stone-400 animate-pulse">Loading books…</p>
        )}
        {books.error && (
          <p className="text-sm text-red-500">Error: {books.error}</p>
        )}
        {books.data && (
          <BookList
            books={books.data.data}
            selectedOsisId={selectedOsisId}
            onSelect={handleBookSelect}
          />
        )}

        {book.data && (
          <div className="mt-4">
            <ChapterNav
              chapters={book.data.chapters}
              selectedChapter={selectedChapter}
              onSelect={handleChapterSelect}
            />
          </div>
        )}
      </aside>

      {/* ── Main reader ──────────────────────────────────────── */}
      <main className="flex-1 min-w-0">
        {/* Breadcrumb */}
        {selectedOsisId && (
          <div className="mb-4 flex items-center gap-2 text-sm text-stone-500">
            <span className="font-medium text-stone-700">
              {book.data?.name_en ?? selectedOsisId}
            </span>
            {selectedChapter && (
              <>
                <span>/</span>
                <span>Chapter {selectedChapter}</span>
              </>
            )}
          </div>
        )}

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

      {/* ── Morphology panel ─────────────────────────────────── */}
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
  );
}
