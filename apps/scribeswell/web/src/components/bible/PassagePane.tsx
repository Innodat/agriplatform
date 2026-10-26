import { useLayoutEffect, useRef } from "react";
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
  number: number;
  paneKey?:string;
  anchor?:import("@/lib/reader-layout").Anchor;
  picker?:number;
  focused?:boolean;
  active?:boolean;
  onClose?:()=>void;
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
  onWord: (word: WordResponse, verse: number, retain?:boolean) => void;
}

export function PassagePane({ reference,onActivate,number,paneKey,anchor,picker,onClose,focused,active, targetVerse, targetRevision, matchKey, onPreview, book, chapter, books, comparing, visible, selectedWordId, onNavigate, onWord }: PassagePaneProps) {
  const referenceOnly=referenceBook(book)?.text_support==='reference_only';
  const verses = useVerses(referenceOnly?null:book, chapter);
  const navigation = useChapterNavigation(books, book, chapter);
  const scroll = useRef<HTMLElement>(null);
  const positionChanged=useRef<()=>void>(()=>{});
  // Retain a word/offset through grid resizing and temporary hidden panes. A
  // clamped layout scroll is not a new reading position.
  useLayoutEffect(()=>{
    const node=scroll.current;if(!node)return;
    let width=node.clientWidth,height=node.clientHeight;
    let lastScroll=node.scrollTop,hidden=!height;
    let held:{word:HTMLElement;offset:number}|undefined;
    let generated:number|undefined;
    let first=true;
    function capture(){
      if(!node||!node.clientHeight)return;
      lastScroll=node.scrollTop;
      const bounds=node.getBoundingClientRect(),word=Array.from(node.querySelectorAll<HTMLElement>('[data-word-position]')).find(w=>{const r=w.getBoundingClientRect();return r.bottom>bounds.top&&r.top<bounds.bottom;});
      if(word)held={word,offset:word.getBoundingClientRect().top-bounds.top};
    }
    function moved(){
      if(node!.clientWidth!==width||node!.clientHeight!==height)return;
      if(generated===node!.scrollTop)return;
      generated=undefined;
      delete node!.dataset.preservedAnchor;delete node!.dataset.preservedScroll;
      capture();
    }
    const observer=new ResizeObserver(()=>{
      if(!node.clientHeight){hidden=true;return;}
      if(first){first=false;capture();width=node.clientWidth;height=node.clientHeight;hidden=false;return;}
      // A pending scroll can arrive after dimensions change. Native clamping
      // alone yields min(lastScroll,newMax); a different position is newer input.
      const clamped=Math.min(lastScroll,Math.max(0,node.scrollHeight-node.clientHeight));
      if(!hidden&&node.scrollTop!==clamped){
        delete node.dataset.preservedAnchor;delete node.dataset.preservedScroll;
        capture();
      }
      if(held?.word.isConnected){
        node.scrollTop+=held.word.getBoundingClientRect().top-node.getBoundingClientRect().top-held.offset;
        generated=node.scrollTop;
        const position=Number(held.word.dataset.wordPosition);
        node.dataset.preservedScroll=String(generated);
        node.dataset.preservedAnchor=JSON.stringify({chapter,verse:Number(held.word.closest<HTMLElement>('[data-verse]')?.dataset.verse),...(position>=1&&position<=4096?{word:position}:{}),offset:Math.max(-512,Math.min(512,Math.round(held.offset)))});
      }else capture();
      lastScroll=node.scrollTop;
      width=node.clientWidth;height=node.clientHeight;hidden=false;
    });
    positionChanged.current=()=>{generated=undefined;delete node.dataset.preservedAnchor;delete node.dataset.preservedScroll;capture();};
    capture();observer.observe(node);node.addEventListener('scroll',moved);return()=>{observer.disconnect();node.removeEventListener('scroll',moved);delete node.dataset.preservedAnchor;delete node.dataset.preservedScroll;};
  },[book,chapter,targetRevision,verses.data,focused]);
  useLayoutEffect(() => { if (scroll.current) scroll.current.scrollTop = 0; }, [book, chapter]);
  const appliedTarget = useRef<string | null>(null);
  // Apply the one-shot target before ready text paints; a later passive effect
  // must never rewind movement made after the text became available.
  useLayoutEffect(() => {
    const key = `${book}:${chapter}:${targetVerse}:${targetRevision}`;

    const apply = () => {
      if(appliedTarget.current===key||!scroll.current?.clientHeight||!scroll.current.getClientRects().length)return;
      if(verses.loading || !verses.data) return;
      const anchorVerse=anchor?scroll.current.querySelector<HTMLElement>(`[data-verse="${anchor.verse}"]`):null;
      const anchored=(anchor?.word?anchorVerse?.querySelector<HTMLElement>(`[data-word-position="${anchor.word}"]`):null)??anchorVerse;
      const explicit=targetVerse?scroll.current.querySelector<HTMLElement>(`[data-verse="${targetVerse}"]`):null;
      const node=anchored??explicit;
      const offset=anchored?anchor?.offset??0:0;
      scroll.current.scrollTop=node?scroll.current.scrollTop+node.getBoundingClientRect().top-scroll.current.getBoundingClientRect().top-offset:0;appliedTarget.current=key;positionChanged.current();
    };
    apply();
    const observer = new ResizeObserver(apply);
    if(scroll.current)observer.observe(scroll.current);
    return ()=>observer.disconnect();
  },[book,chapter,targetVerse,targetRevision,verses.data,verses.loading,visible,anchor]);
  return (
    <section data-reader-pane data-pane-key={paneKey} aria-current={active?'true':undefined} onPointerDown={event=>{if(!(event.target as HTMLElement).closest('[data-close-pane]'))onActivate?.();}} onFocusCapture={event=>{if(!(event.target as HTMLElement).closest('[data-close-pane]'))onActivate?.();}} id={`passage-${number}`} aria-label={`Passage ${number}`} className={`${visible ? 'flex' : 'hidden'} ${active&&comparing?'ring-2 ring-inset ring-amber-300 rounded-lg':''} flex-col gap-3 flex-1 min-w-0 min-h-0 ${comparing ? 'lg:border-l lg:border-stone-200 lg:pl-3' : ''}`}>
      <div data-reader-controls className="flex flex-wrap shrink-0 items-center justify-end gap-1">
        {active&&comparing&&<span aria-hidden="true" className="mr-auto rounded border border-amber-300 px-1 text-xs text-amber-900">Active</span>}
        <button type="button" aria-label="Previous chapter" title={navigation.previous ? `Previous chapter: ${navigation.previous.book} ${navigation.previous.chapter}` : 'Previous chapter'} disabled={!navigation.previous} onClick={() => { if (navigation.previous) onNavigate(navigation.previous.book, navigation.previous.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronLeft size={18} aria-hidden="true" /></button>
        {<BookChapterSelector key={picker??0} startOpen={Boolean(picker)} books={books} selectedOsisId={book} selectedChapter={chapter} onSelect={onNavigate} initialReference={reference} />}
        <button type="button" aria-label="Next chapter" title={navigation.next ? `Next chapter: ${navigation.next.book} ${navigation.next.chapter}` : 'Next chapter'} disabled={!navigation.next} onClick={() => { if (navigation.next) onNavigate(navigation.next.book, navigation.next.chapter); }} className="p-2 rounded-lg text-stone-600 hover:bg-stone-100 disabled:opacity-30 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-amber-600"><ChevronRight size={18} aria-hidden="true" /></button>
        {onClose&&<button data-close-pane type="button" aria-label={`Close passage ${number}`} onClick={event=>{event.stopPropagation();onClose();}} className="p-2 rounded-lg hover:bg-stone-100">×</button>}
      </div>
      {navigation.error && <p data-reader-chrome role="alert" className="shrink-0 text-sm text-red-700">Could not load chapter navigation. <button className="underline" onClick={navigation.retry}>Retry navigation</button></p>}
      <section data-reader-scroll data-pane-key={paneKey} data-chapter={chapter} data-ready={!referenceOnly&&!verses.loading&&!verses.error&&Boolean(verses.data?.data.length)} ref={scroll} tabIndex={0} aria-label={comparing ? `Passage ${number} text` : 'Chapter text'} className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-1 pb-4 focus-visible:outline-2 focus-visible:outline-amber-600">
        {reference&&reference.target.kind==='verse_range'&&<p className="text-sm mb-2">{referenceLabel(reference)}</p>}
        {referenceOnly&&<p role="status">{reference?referenceLabel(reference):`${referenceBook(book)?.name_en??book} ${chapter}`} — Text unavailable</p>}
        {!referenceOnly&&verses.loading && <p role="status" className="text-sm text-stone-400 animate-pulse">Loading chapter…</p>}
        {verses.error && <p role="alert" className="text-sm text-red-700">Could not load this chapter. <button className="underline" onClick={verses.refetch}>Retry chapter</button></p>}
        {verses.data && <VerseReader book={book} active={active} origin={`${paneKey}:${book}:${chapter}:${targetRevision}`} verses={verses.data.data} selectedWordId={selectedWordId} onWordClick={onWord} matchKey={matchKey} onPreview={onPreview} />}
      </section>
    </section>
  );
}
