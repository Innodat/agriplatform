/** Public Hebrew reader with optional independent passage comparison. */
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Columns2, Maximize2, Minimize2, X } from "lucide-react";
import { useReaderLayout } from "@/components/layout/AppShell";
import { PassagePane } from "@/components/bible/PassagePane";
import { WordStudy } from "@/components/bible/WordStudy";
import { useBooks, useWordMorphology } from "@/hooks/useBible";
import type { WordResponse } from "@/schemas/bible.schema";

import {useStudies} from "@/context/StudiesContext";
import {StudiesPanel} from "@/components/studies/StudiesPanel";
import {NoteEditor} from "@/components/studies/NoteEditor";

import {chapterReference,makeReference,referenceBook,referenceStart,type PassageReference} from '@/lib/passage-references';
function urlReference(params:URLSearchParams,pane:1|2):PassageReference|undefined{
 const prefix=pane===1?'':'compare',book=params.get(pane===1?'book':'compareBook')??'Gen';
 function coordinate(key:string,fallback?:number){const raw=params.get(key);if(raw===null)return fallback;if(!/^[1-9][0-9]*$/.test(raw))throw Error('invalid coordinate');const value=Number(raw);if(!Number.isSafeInteger(value))throw Error('invalid coordinate');return value;}
 try{
  const chapter=coordinate(pane===1?'chapter':'compareChapter',1)!,verse=coordinate(pane===1?'verse':'compareVerse');
  const endChapter=coordinate(prefix+'EndChapter',chapter),endVerse=coordinate(prefix+'EndVerse',verse);
  if(verse===undefined){if(params.has(prefix+'EndChapter')||params.has(prefix+'EndVerse'))return undefined;return chapterReference(book,chapter);}
  return makeReference(book,{kind:'verse_range',start:{chapter,verse},end:{chapter:endChapter!,verse:endVerse!}});
 }catch{return undefined;}
}

type ScrollAnchor = { scroll: HTMLElement; word: HTMLElement; offset: number; focusedScrollTop?: number };
function captureAnchors(root: HTMLElement | null): ScrollAnchor[] {
  return Array.from(root?.querySelectorAll<HTMLElement>('[data-reader-scroll]') ?? []).flatMap(scroll => {
    if (!scroll.clientHeight) return [];
    const bounds = scroll.getBoundingClientRect();
    const word = Array.from(scroll.querySelectorAll<HTMLElement>('.word-token')).find(node => {
      const rect = node.getBoundingClientRect();
      return rect.bottom > bounds.top && rect.top < bounds.bottom;
    });
    return word ? [{ scroll, word, offset: word.getBoundingClientRect().top - bounds.top }] : [];
  });
}

type Pane = 1 | 2;
type Selection = { pane: Pane; book: string; chapter: number; verse: number; word: WordResponse };
function chapterNumber(value: string | null) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number > 0 && number <= 150 ? number : 1;
}
function verseNumber(value:string|null){const n=Number(value);return Number.isSafeInteger(n)&&n>0&&n<=176?n:null;}
const control = "inline-flex items-center justify-center gap-2 rounded-lg border border-stone-200 px-3 py-1.5 text-sm text-stone-700 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-amber-600";

export function ReaderPage() {
  const studies=useStudies();
  const [params, setParams] = useSearchParams();
  const { focused, setFocused } = useReaderLayout();
  const focusButton = useRef<HTMLButtonElement>(null);
  const reader = useRef<HTMLDivElement>(null);
  const anchors = useRef<ScrollAnchor[]>([]);
  const changeFocus = useCallback((next: boolean) => {
    if (next === focused) return;
    anchors.current = captureAnchors(reader.current).map(current => {
      const saved = anchors.current.find(item => item.scroll === current.scroll);
      // An enlarged viewport may clamp the bottom position. If the user has
      // not scrolled or navigated in focus, retain the original reading anchor.
      return !next && saved?.word.isConnected && saved.focusedScrollTop === current.scroll.scrollTop ? saved : current;
    });
    setFocused(next);
  }, [focused, setFocused]);
  useLayoutEffect(() => {
    for (const anchor of anchors.current) {
      if (!anchor.word.isConnected || !anchor.scroll.clientHeight) continue;
      anchor.scroll.scrollTop += anchor.word.getBoundingClientRect().top - anchor.scroll.getBoundingClientRect().top - anchor.offset;
      if (focused) anchor.focusedScrollTop = anchor.scroll.scrollTop;
    }
  }, [focused]);
  useEffect(() => {
    if (!focused) return;
    function escape(event: KeyboardEvent) {
      if (event.key !== 'Escape' || event.defaultPrevented) return;
      changeFocus(false);
      focusButton.current?.focus({ preventScroll: true });
    }
    window.addEventListener('keydown', escape);
    return () => window.removeEventListener('keydown', escape);
  }, [focused, changeFocus]);
  const book = params.get('book') || 'Gen';
  const chapter = chapterNumber(params.get('chapter'));
  const compareBook = params.get('compareBook') || '';
  const compareChapter = chapterNumber(params.get('compareChapter'));
  const comparing = Boolean(compareBook);
  const [targetRevision,setTargetRevision] = useState({1:0,2:0});
  const [activePane,setActivePane]=useState<Pane>(1);
  const [mobilePane, setMobilePane] = useState<Pane>(1);
  const [previewWord, setPreviewWord] = useState<WordResponse | null>(null);
  const dwell = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelPreview = useCallback(() => {if(dwell.current)clearTimeout(dwell.current);dwell.current=null;setPreviewWord(null);},[]);
  useLayoutEffect(()=>{cancelPreview();return ()=>{if(dwell.current)clearTimeout(dwell.current);};},[book,chapter,compareBook,compareChapter,focused,mobilePane,cancelPreview]);
  function preview(word:WordResponse|null){cancelPreview();if(word)dwell.current=setTimeout(()=>setPreviewWord(word),1000);}
  const [selection, setSelection] = useState<Selection | null>(null);
  // Validate against URL on every render, including history navigation. Never
  // briefly attribute the old word to the newly selected passage.
  const selected = selection && (selection.pane === 1
    ? selection.book === book && selection.chapter === chapter
    : comparing && selection.book === compareBook && selection.chapter === compareChapter) ? selection : null;
  useEffect(() => { if (!selected) setSelection(null); }, [selected]);
  useEffect(() => { if (!comparing) setMobilePane(1); }, [comparing]);
  const books = useBooks();
  const morphology = useWordMorphology(selected?.word.id ?? null);
  const bookName = (osis: string) => books.data?.data.find(b => b.osis_id === osis)?.name_en ?? referenceBook(osis)?.name_en ?? osis;
  const context = selected ? `${bookName(selected.book)} ${selected.chapter}:${selected.verse}` : '';

  function navigate(pane: Pane, nextBook: string, nextChapter: number, verse?: number,reference?:PassageReference) {
    setActivePane(pane);
    const range=reference?.target.kind==='verse_range'?reference.target:undefined;
    if(range)verse=range.start.verse;
    if(verse)setTargetRevision(previous=>({...previous,[pane]:previous[pane]+1}));
    if (selection?.pane === pane) setSelection(null);
    setParams(previous => {
      const next = new URLSearchParams(previous);
      next.set(pane === 1 ? 'book' : 'compareBook', nextBook);
      next.set(pane === 1 ? 'chapter' : 'compareChapter', String(nextChapter));
      next.delete(pane === 1 ? 'verse' : 'compareVerse');
      const prefix=pane===1?'':'compare';next.delete(prefix+'EndChapter');next.delete(prefix+'EndVerse');
      if(range){next.set(prefix+'EndChapter',String(range.end.chapter));next.set(prefix+'EndVerse',String(range.end.verse));}
      if (verse) next.set(pane === 1 ? 'verse' : 'compareVerse', String(verse));
      return next;
    });
  }
  function toggleComparison() {
    if (comparing) {
      if (selection?.pane === 2) setSelection(null);
      setMobilePane(1);
      setParams(previous => { const next = new URLSearchParams(previous); next.delete('compareBook'); next.delete('compareChapter'); next.delete('compareVerse');next.delete('compareEndChapter');next.delete('compareEndVerse');setActivePane(1); return next; });
    } else {
      setSelection(null);
      navigate(2, book, chapter);
      setMobilePane(2);
    }
  }
  function chooseWord(pane: Pane, word: WordResponse, verse: number) {
    cancelPreview();
    if(studies.enabled&&studies.current){studies.setTool('analysis');studies.setAnalysisTab('Word');}
    setMobilePane(pane);setActivePane(pane);
    changeFocus(false);
    setSelection(previous => !focused && previous?.pane === pane && previous.word.id === word.id ? null : {
      pane, word, verse, book: pane === 1 ? book : compareBook, chapter: pane === 1 ? chapter : compareChapter,
    });
  }
  function showPane(pane: Pane) {
    setMobilePane(pane);setActivePane(pane);
    // Keep analysis attached to the visible passage on narrow screens.
    if (selection?.pane !== pane) setSelection(null);
  }

  return (
    <div ref={reader} className={`flex flex-col gap-3 h-full min-h-0 mx-auto ${comparing ? 'max-w-[100rem]' : 'max-w-5xl'}`}>
      <div className="flex flex-wrap shrink-0 items-center gap-2">
        <button hidden={focused} type="button" className={focused ? "hidden" : control} onClick={toggleComparison} aria-pressed={comparing}>
          {comparing ? <X size={16} aria-hidden="true" /> : <Columns2 size={16} aria-hidden="true" />}
          {comparing ? 'Close comparison' : 'Compare passages'}
        </button>
        <button ref={focusButton} type="button" className={control} aria-label={focused ? 'Exit focus mode' : 'Enter focus mode'} aria-pressed={focused} onClick={() => changeFocus(!focused)} title={focused ? 'Exit focus mode (Escape)' : 'Hide header and word analysis'}>
          {focused ? <Minimize2 size={16} aria-hidden="true" /> : <Maximize2 size={16} aria-hidden="true" />}
          {focused ? 'Exit focus' : 'Focus mode'}
        </button>
        {books.loading && <span className="text-sm text-stone-400">Loading books…</span>}
        {books.error && <p role="alert" className="text-sm text-red-700">Could not load books. <button className="underline" onClick={books.refetch}>Retry books</button></p>}
      </div>
      {studies.enabled&&<nav aria-label="Reader tools" className="flex shrink-0 gap-2"><button className={control} aria-pressed={studies.tool==='studies'} onClick={studies.openStudies}>Studies</button><button className={control} aria-pressed={studies.tool==='analysis'} onClick={()=>studies.setTool(studies.tool==='analysis'?null:'analysis')}>Analysis</button>{studies.study&&<span className="truncate self-center">{studies.study.title}</span>}</nav>}
      {studies.enabled&&studies.error&&studies.tool==='analysis'&&<p role="alert">{studies.error} <button className="underline" onClick={()=>void studies.loadStudies()}>Retry Studies</button></p>}
      {comparing && <div role="group" aria-label="Visible passage" className="flex gap-2 shrink-0 lg:hidden">
        {([1, 2] as const).map(pane => <button key={pane} className={`${control} flex-1 min-w-0 ${mobilePane === pane ? 'bg-amber-100 border-amber-300' : ''}`} aria-controls={`passage-${pane}`} aria-label={`Show passage ${pane}: ${bookName(pane === 1 ? book : compareBook)} ${pane === 1 ? chapter : compareChapter}`} aria-pressed={mobilePane === pane} onClick={() => showPane(pane)}>
          <span className="truncate">{pane}: {bookName(pane === 1 ? book : compareBook)} {pane === 1 ? chapter : compareChapter}</span>
        </button>)}
      </div>}
      <div className={`flex flex-col gap-4 flex-1 min-h-0 ${comparing ? 'xl:flex-row' : 'md:flex-row md:justify-center'}`}>
        <div className={`${studies.enabled&&studies.tool?'hidden md:flex':'flex'} gap-4 flex-1 min-w-0 min-h-0 ${comparing ? '' : 'md:max-w-[44rem]'}`}>
          <PassagePane reference={urlReference(params,1)} onActivate={()=>setActivePane(1)} number={1} targetRevision={targetRevision[1]} targetVerse={verseNumber(params.get("verse"))} book={book} chapter={chapter} books={books.data?.data ?? []} comparing={comparing} visible={!comparing || mobilePane === 1} selectedWordId={selected?.pane === 1 ? selected.word.id : null} matchKey={(previewWord??selected?.word)?.match_key??null} onPreview={preview} onNavigate={(b,c,r) => navigate(1,b,c,undefined,r)} onWord={(w,v) => chooseWord(1,w,v)} />
          {comparing && <PassagePane reference={urlReference(params,2)} onActivate={()=>setActivePane(2)} number={2} targetRevision={targetRevision[2]} targetVerse={verseNumber(params.get("compareVerse"))} book={compareBook} chapter={compareChapter} books={books.data?.data ?? []} comparing visible={mobilePane === 2} selectedWordId={selected?.pane === 2 ? selected.word.id : null} matchKey={(previewWord??selected?.word)?.match_key??null} onPreview={preview} onNavigate={(b,c,r) => navigate(2,b,c,undefined,r)} onWord={(w,v) => chooseWord(2,w,v)} />}
        </div>
        {studies.enabled&&<aside key={studies.accountKey} hidden={!studies.tool} aria-label="Study tools" className="min-h-0 overflow-y-auto bg-white border border-stone-200 rounded-xl shrink-0 w-full md:w-80 max-h-full flex-1 md:flex-none"><button className="underline m-3 md:hidden" onClick={()=>studies.setTool(null)}>Return to reader</button><div hidden={studies.tool!=='studies'}><StudiesPanel activeReference={urlReference(params,comparing?activePane:1)} onOpen={reference=>{const pane=comparing?activePane:1,start=referenceStart(reference);navigate(pane,reference.book_id,start.chapter,start.verse,reference);setMobilePane(pane);studies.setTool(null);}}/></div><div hidden={studies.tool!=='analysis'}><div role="tablist" aria-label="Analysis" className="flex border-b">{(['Word','Occurrences','Notes'] as const).map(tab=><button key={tab} role="tab" aria-selected={studies.analysisTab===tab} disabled={tab!=='Notes'&&!selected} className="flex-1 p-2 disabled:opacity-40" onClick={()=>studies.setAnalysisTab(tab)}>{tab}</button>)}</div><div hidden={studies.analysisTab!=='Notes'}><NoteEditor/></div><div hidden={studies.analysisTab==='Notes'}>{studies.tool==='analysis'&&morphology.loading&&<p role="status">Loading word analysis…</p>}{studies.tool==='analysis'&&morphology.data&&selected&&<WordStudy hideTabs controlledTab={studies.analysisTab==='Occurrences'?'Occurrences':'Word'} currentPane={selected.pane} key={`${selected.pane}:${selected.word.id}`} word={morphology.data} context={context} books={books.data?.data??[]} onClose={()=>{setSelection(null);studies.setAnalysisTab('Notes');}} onOpen={(pane,b,c,v)=>{navigate(pane,b,c,v);setMobilePane(pane);}} />}</div></div></aside>}
        {selected && !focused && (!studies.enabled||!studies.tool) && <aside data-inspector-scroll aria-label="Word analysis panel" className={`min-h-0 max-h-[45%] overflow-y-auto overscroll-contain shrink-0 ${comparing ? 'xl:max-h-full xl:h-full xl:w-72' : 'md:max-h-full md:h-full md:w-72'}`}>
          {morphology.loading && <p role="status" className="p-4 bg-white">Loading word analysis… <button className="underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.error && <p role="alert" className="bg-white p-4 text-sm text-red-700">Could not load word analysis. <button className="underline" onClick={morphology.refetch}>Retry word analysis</button><button className="ml-2 underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.data && morphology.data.id === selected.word.id && <WordStudy currentPane={selected.pane} key={`${selected.pane}:${selected.word.id}`} word={morphology.data} context={context} books={books.data?.data ?? []} onClose={() => setSelection(null)} onOpen={(pane,b,c,v)=>{navigate(pane,b,c,v);setMobilePane(pane);}} />}
        </aside>}
      </div>
    </div>
  );
}
