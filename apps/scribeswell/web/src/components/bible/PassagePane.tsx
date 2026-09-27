import { useEffect, useRef } from "react";
import { BookChapterSelector } from "./book-chapter-selector";
import { VerseReader } from "./VerseReader";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useChapterNavigation } from "@/hooks/useChapterNavigation";
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
  const navigation = useChapterNavigation(books, book, chapter);
  const scroll = useRef<HTMLElement>(null);
  useEffect(() => { if (scroll.current) scroll.current.scrollTop = 0; }, [book, chapter]);
  return (
    <section id={`passage-${number}`} aria-label={`Passage ${number}`} className={`${visible ? 'flex' : 'hidden lg:flex'} flex-col gap-3 flex-1 min-w-0 min-h-0 ${comparing ? 'lg:border-l lg:border-stone-200 lg:pl-3' : ''}`}>
      <div className="flex flex-wrap shrink-0 items-center justify-end gap-1">
        {comparing && <span className="mr-auto text-xs font-medium text-stone-500">Passage {number}</span>}
        <button type="button" aria-label="Previous chapter" title={navigation.previous ? `Previous chapter: ${navigation.previous.book} ${navigation.previous.chapter}` : 'Previous chapter'} disabled={!navigation.previous} onClick={() => { if (navigation.previous) onNavigate(navigation.previous.book, navigation.previous.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronLeft size={18} aria-hidden="true" /></button>
        {books.length > 0 && <BookChapterSelector books={books} selectedOsisId={book} selectedChapter={chapter} onSelect={onNavigate} />}
        <button type="button" aria-label="Next chapter" title={navigation.next ? `Next chapter: ${navigation.next.book} ${navigation.next.chapter}` : 'Next chapter'} disabled={!navigation.next} onClick={() => { if (navigation.next) onNavigate(navigation.next.book, navigation.next.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronRight size={18} aria-hidden="true" /></button>
      </div>
      {navigation.error && <p role="alert" className="shrink-0 text-sm text-red-700">Could not load chapter navigation. <button className="underline" onClick={navigation.retry}>Retry navigation</button></p>}
      <section data-reader-scroll ref={scroll} tabIndex={0} aria-label={comparing ? `Passage ${number} text` : 'Chapter text'} className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-1 pb-4 focus-visible:outline-2 focus-visible:outline-amber-600">
        {verses.loading && <p role="status" className="text-sm text-stone-400 animate-pulse">Loading chapter…</p>}
        {verses.error && <p role="alert" className="text-sm text-red-700">Could not load this chapter. <button className="underline" onClick={verses.refetch}>Retry chapter</button></p>}
        {verses.data && <VerseReader verses={verses.data.data} selectedWordId={selectedWordId} onWordClick={onWord} />}
      </section>
    </section>
  );
}
