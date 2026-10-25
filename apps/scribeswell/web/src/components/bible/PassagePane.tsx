import { useEffect, useRef } from "react";
import { BookChapterSelector } from "./book-chapter-selector";
import { VerseReader } from "./VerseReader";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useChapterNavigation } from "@/hooks/useChapterNavigation";
import { useVerses } from "@/hooks/useBible";
import type { BookResponse, WordResponse } from "@/schemas/bible.schema";

import {referenceBook,referenceLabel,type PassageReference} from '@/lib/passage-references';

interface PassagePaneProps {
  reference?: PassageReference;
  onActivate?:()=>void;
  number: 1 | 2;
  targetVerse?: number | null;
  targetRevision?: number;
  matchKey?: string | null;
  onPreview?: (word: WordResponse | null) => void;
  book: string;
  chapter: number;
  books: BookResponse[];
  comparing: boolean;
  visible: boolean;
  selectedWordId: number | null;
  onNavigate: (book: string, chapter: number, reference?:PassageReference) => void;
  onWord: (word: WordResponse, verse: number) => void;
}

export function PassagePane({ reference,onActivate,number, targetVerse, targetRevision, matchKey, onPreview, book, chapter, books, comparing, visible, selectedWordId, onNavigate, onWord }: PassagePaneProps) {
  const referenceOnly=referenceBook(book)?.text_support==='reference_only';
  const verses = useVerses(referenceOnly?null:book, chapter);
  const navigation = useChapterNavigation(books, book, chapter);
  const scroll = useRef<HTMLElement>(null);
  useEffect(() => { if (scroll.current) scroll.current.scrollTop = 0; }, [book, chapter]);
  const appliedTarget = useRef<string | null>(null);
  useEffect(() => {
    const key = `${book}:${chapter}:${targetVerse}:${targetRevision}`;
    if(!targetVerse){appliedTarget.current=null;return;}
    const apply = () => {
      if(appliedTarget.current===key||!scroll.current?.clientHeight||!scroll.current.getClientRects().length)return;
      if(verses.loading || !verses.data) return;
      const node=scroll.current.querySelector<HTMLElement>(`[data-verse="${targetVerse}"]`);
      if(node){scroll.current.scrollTop+=node.getBoundingClientRect().top-scroll.current.getBoundingClientRect().top;appliedTarget.current=key;}
    };
    apply();
    const observer = new ResizeObserver(apply);
    if(scroll.current)observer.observe(scroll.current);
    return ()=>observer.disconnect();
  },[book,chapter,targetVerse,targetRevision,verses.data,verses.loading,visible]);
  return (
    <section onPointerDown={onActivate} onFocusCapture={onActivate} id={`passage-${number}`} aria-label={`Passage ${number}`} className={`${visible ? 'flex' : 'hidden lg:flex'} flex-col gap-3 flex-1 min-w-0 min-h-0 ${comparing ? 'lg:border-l lg:border-stone-200 lg:pl-3' : ''}`}>
      <div className="flex flex-wrap shrink-0 items-center justify-end gap-1">
        <button type="button" aria-label="Previous chapter" title={navigation.previous ? `Previous chapter: ${navigation.previous.book} ${navigation.previous.chapter}` : 'Previous chapter'} disabled={!navigation.previous} onClick={() => { if (navigation.previous) onNavigate(navigation.previous.book, navigation.previous.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronLeft size={18} aria-hidden="true" /></button>
        {<BookChapterSelector books={books} selectedOsisId={book} selectedChapter={chapter} onSelect={onNavigate} initialReference={reference} />}
        <button type="button" aria-label="Next chapter" title={navigation.next ? `Next chapter: ${navigation.next.book} ${navigation.next.chapter}` : 'Next chapter'} disabled={!navigation.next} onClick={() => { if (navigation.next) onNavigate(navigation.next.book, navigation.next.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronRight size={18} aria-hidden="true" /></button>
      </div>
      {navigation.error && <p role="alert" className="shrink-0 text-sm text-red-700">Could not load chapter navigation. <button className="underline" onClick={navigation.retry}>Retry navigation</button></p>}
      <section data-reader-scroll ref={scroll} tabIndex={0} aria-label={comparing ? `Passage ${number} text` : 'Chapter text'} className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-1 pb-4 focus-visible:outline-2 focus-visible:outline-amber-600">
        {reference&&reference.target.kind==='verse_range'&&<p className="text-sm mb-2">{referenceLabel(reference)}</p>}
        {referenceOnly&&<p role="status">{reference?referenceLabel(reference):`${referenceBook(book)?.name_en??book} ${chapter}`} — Text unavailable</p>}
        {!referenceOnly&&verses.loading && <p role="status" className="text-sm text-stone-400 animate-pulse">Loading chapter…</p>}
        {verses.error && <p role="alert" className="text-sm text-red-700">Could not load this chapter. <button className="underline" onClick={verses.refetch}>Retry chapter</button></p>}
        {verses.data && <VerseReader verses={verses.data.data} selectedWordId={selectedWordId} onWordClick={onWord} matchKey={matchKey} onPreview={onPreview} />}
      </section>
    </section>
  );
}
