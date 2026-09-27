import { useEffect, useRef } from "react";
import { BookChapterSelector } from "./book-chapter-selector";
import { VerseReader } from "./VerseReader";
import { useVerses } from "@/hooks/useBible";
import type { BookResponse, WordResponse } from "@/schemas/bible.schema";

interface PassagePaneProps {
  number: 1 | 2;
  book: string;
  chapter: number;
  books: BookResponse[];
  comparing: boolean;
  visible: boolean;
  selectedWordId: number | null;
  onNavigate: (book: string, chapter: number) => void;
  onWord: (word: WordResponse, verse: number) => void;
}

export function PassagePane({ number, book, chapter, books, comparing, visible, selectedWordId, onNavigate, onWord }: PassagePaneProps) {
  const verses = useVerses(book, chapter);
  const scroll = useRef<HTMLElement>(null);
  useEffect(() => { if (scroll.current) scroll.current.scrollTop = 0; }, [book, chapter]);
  return (
    <section id={`passage-${number}`} aria-label={`Passage ${number}`} className={`${visible ? 'flex' : 'hidden lg:flex'} flex-col gap-3 flex-1 min-w-0 min-h-0 ${comparing ? 'lg:border-l lg:border-stone-200 lg:pl-3' : ''}`}>
      <div className="flex shrink-0 items-center justify-end gap-2">
        {comparing && <span className="mr-auto text-xs font-medium text-stone-500">Passage {number}</span>}
        {books.length > 0 && <BookChapterSelector books={books} selectedOsisId={book} selectedChapter={chapter} onSelect={onNavigate} />}
      </div>
      <section ref={scroll} tabIndex={0} aria-label={comparing ? `Passage ${number} text` : 'Chapter text'} className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-1 pb-4 focus-visible:outline-2 focus-visible:outline-amber-600">
        {verses.loading && <p role="status" className="text-sm text-stone-400 animate-pulse">Loading chapter…</p>}
        {verses.error && <p role="alert" className="text-sm text-red-700">Could not load this chapter. <button className="underline" onClick={verses.refetch}>Retry chapter</button></p>}
        {verses.data && <VerseReader verses={verses.data.data} selectedWordId={selectedWordId} onWordClick={onWord} />}
      </section>
    </section>
  );
}
