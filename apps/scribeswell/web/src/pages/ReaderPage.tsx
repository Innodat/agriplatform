import {workspaceTabId} from '@/lib/reader-layout';
/** Public Hebrew reader with optional independent passage comparison. */
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import {useTabState,useWorkspace} from "@/context/ReaderWorkspaceContext";
import {WorkspaceTabs} from "@/components/bible/WorkspaceTabs";
import { Columns2, Maximize2, Minimize2 } from "lucide-react";
import { useReaderLayout } from "@/components/layout/AppShell";
import { PassagePane } from "@/components/bible/PassagePane";
import { WordStudy } from "@/components/bible/WordStudy";
import { useBooks, useWordMorphology } from "@/hooks/useBible";
import type { WordResponse } from "@/schemas/bible.schema";

import {useStudies} from "@/context/StudiesContext";
import {StudiesPanel} from "@/components/studies/StudiesPanel";
import {RelevantNotes} from "@/components/studies/RelevantNotes";
import {NoteEditor} from "@/components/studies/NoteEditor";

import {chapterReference,makeReference,referenceBook,referenceStart,referenceLabel,type PassageReference} from '@/lib/passage-references';
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

type Selection = {key:string;pane:string;generation:number;book:string;chapter:number;verse:number;word:WordResponse};
const control = "inline-flex items-center justify-center gap-2 rounded-lg border border-stone-200 px-3 py-1.5 text-sm text-stone-700 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-amber-600";

export function ReaderPage() {
  const studies=useStudies();

  const { focused, setFocused } = useReaderLayout();
  const focusButton = useRef<HTMLButtonElement>(null);
  const controller=useWorkspace();
  const reader = controller.root;
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

  const {workspace}=controller,comparing=workspace.panes.length>1;
  const active=workspace.panes.find(p=>p.paneKey===workspace.activePaneKey)!;
  const grid=useRef<HTMLDivElement>(null);
  const [geometry,setGeometry]=useState({width:0,height:0,chrome:52});
  useLayoutEffect(() => {
    const node=grid.current;
    if(!node)return;
    const measured=new Map<string,number>();
    const dirty=new Set<string>();
    const observed=new Set<Element>();
    const measure=() => {
      const width=node.clientWidth;
      const count=node.querySelectorAll('[data-reader-pane]').length;
      const columns=count===1?1:width>=992&&count===3?3:width>=656?2:1;
      const candidateWidth=(width-16*(columns-1))/columns;
      const panes=Array.from(node.querySelectorAll<HTMLElement>('[data-reader-pane]'));
      for(const pane of panes) {
        const key=pane.dataset.paneKey!;
        const scroll=pane.querySelector<HTMLElement>('[data-reader-scroll]');
        if(!scroll?.clientHeight)continue;
        const chrome=Math.max(52,pane.clientHeight-scroll.clientHeight);
        // A single visible pane is wider than a candidate grid cell. Retain
        // measured wrapping cost until the controls themselves change, so
        // widening that fallback cannot repeatedly re-enable a too-short grid.
        if(pane.clientWidth<=candidateWidth+2||!measured.has(key)||dirty.has(key))measured.set(key,chrome);
        else measured.set(key,Math.max(measured.get(key)!,chrome));
        dirty.delete(key);
      }
      const chrome=Math.max(52,...measured.values());
      setGeometry(previous=>previous.width===width&&previous.height===node.clientHeight&&previous.chrome===chrome
        ?previous:{width,height:node.clientHeight,chrome});
    };
    const resize=new ResizeObserver(measure);
    const observe=() => {
      const next=new Set<Element>([node,...node.querySelectorAll('[data-reader-controls], [data-reader-chrome], [data-reader-scroll]')]);
      for(const element of observed)if(!next.has(element)){resize.unobserve(element);observed.delete(element);}
      for(const element of next)if(!observed.has(element)){resize.observe(element);observed.add(element);}
    };
    const changes=new MutationObserver(records=>{
      for(const record of records) {
        const target=record.target instanceof Element?record.target:record.target.parentElement;
        const chrome=target?.closest('[data-reader-controls], [data-reader-chrome]');
        const changedChrome=[...record.addedNodes,...record.removedNodes].some(n=>n instanceof Element&&n.matches('[data-reader-chrome]'));
        if(chrome||changedChrome) {
          const pane=target?.closest<HTMLElement>('[data-reader-pane]');
          if(pane?.dataset.paneKey)dirty.add(pane.dataset.paneKey);
        }
      }
      observe();
      measure();
    });
    observe();
    changes.observe(node,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['style','class']});
    measure();
    return()=>{resize.disconnect();changes.disconnect();};
  },[workspace.panes.length,studies.tool]);
  const count=workspace.panes.length;
  const columns=count===1?1:geometry.width>=992&&count===3?3:geometry.width>=656?2:1;
  const rows=Math.ceil(count/columns),single=columns===1||(rows>1&&(geometry.height-16*(rows-1))/rows-geometry.chrome<200);
  const [previewWord,setPreviewWord]=useState<WordResponse|null>(null);
  const dwell=useRef<ReturnType<typeof setTimeout>|null>(null);
  const cancelPreview=useCallback(()=>{if(dwell.current)clearTimeout(dwell.current);dwell.current=null;setPreviewWord(null);},[]);
  useLayoutEffect(()=>{cancelPreview();return()=>{if(dwell.current)clearTimeout(dwell.current);};},[workspace,focused,cancelPreview]);
  function preview(word:WordResponse|null){cancelPreview();if(word){const revision=controller.read().revision;dwell.current=setTimeout(()=>{if(revision===controller.read().revision)setPreviewWord(word);},1000);}}
  const [selection,setSelection]=useTabState<Selection|null>('readerSelection',null);
  useLayoutEffect(()=>{
    const fields=controller.views.get(workspace.tabKey);if(!fields)return;
    for(const name of fields.keys())if(name.startsWith('word:')&&(!selection||!name.startsWith(`word:${selection.key}:`)))fields.delete(name);
  },[selection?.key,workspace.tabKey]);
  const source=selection&&workspace.panes.find(p=>p.paneKey===selection.pane&&p.generation===selection.generation);
  const selected=source&&(!single||source.paneKey===workspace.activePaneKey)?selection:null;
  useEffect(()=>{if(!selected)setSelection(null);},[selected]);
  const books=useBooks(),morphology=useWordMorphology(selected?.word.id??null);
  const bookName=(osis:string)=>books.data?.data.find(b=>b.osis_id===osis)?.name_en??referenceBook(osis)?.name_en??osis;
  const context=selected?`${bookName(selected.book)} ${selected.chapter}:${selected.verse}`:'';
  const [capacity,setCapacity]=useState<{ref:PassageReference;picker:boolean;revision:number}|null>(null);
  const capacityDialog=useRef<HTMLDialogElement>(null);
  useEffect(()=>{if(capacity&&!capacityDialog.current?.open)capacityDialog.current?.showModal();},[capacity]);
  function add(ref:PassageReference,picker=false){if(!controller.add(ref,picker))setCapacity({ref,picker,revision:controller.read().revision});else if(picker&&window.matchMedia('(max-width:767px)').matches)studies.setTool(null);}
  function navigate(key:string,b:string,c:number,verse?:number,reference?:PassageReference){const ref=reference??(verse?makeReference(b,{kind:'verse_range',start:{chapter:c,verse},end:{chapter:c,verse}}):chapterReference(b,c));controller.open(ref,key);}
  function open(target:'here'|'beside'|'tab',b:string,c:number,v:number){const ref=makeReference(b,{kind:'verse_range',start:{chapter:c,verse:v},end:{chapter:c,verse:v}});if(target==='here')controller.open(ref);else if(target==='tab')controller.newTab(ref,false);else add(ref);}
  function chooseWord(key:string,word:WordResponse,verse:number,retain=false){const pane=controller.read().panes.find(p=>p.paneKey===key);if(!pane)return;cancelPreview();controller.activate(key);if(studies.enabled&&studies.current){studies.setTool('analysis');studies.setAnalysisTab('Word');}changeFocus(false);setSelection(previous=>!retain&&!focused&&previous?.pane===key&&previous.generation===pane.generation&&previous.word.id===word.id?null:{key:crypto.randomUUID(),pane:key,generation:pane.generation,word,verse,book:pane.ref.book_id,chapter:referenceStart(pane.ref).chapter});}
  return (
    <div ref={reader} className={`flex flex-col gap-3 h-full min-h-0 mx-auto ${comparing ? 'max-w-[100rem]' : 'max-w-5xl'}`}>
      <WorkspaceTabs key={studies.accountKey}/>
      <div role="group" aria-label="Workspace controls" className="flex flex-wrap shrink-0 items-center justify-between gap-2">
       <div className="flex items-center gap-1">
        <button hidden={focused} type="button" aria-label="Add reader pane" title="Add reader pane" className={focused?'hidden':control} onClick={()=>add(controller.read().panes.find(p=>p.paneKey===controller.read().activePaneKey)!.ref,true)}><Columns2 size={16} aria-hidden="true"/><span className="hidden sm:inline">Add reader pane</span></button>
        {workspace.invalid&&<p role="alert">Invalid reading link</p>}
        {capacity&&<dialog ref={capacityDialog} aria-label="Choose passage to replace" onCancel={()=>setCapacity(null)} onClose={()=>setCapacity(null)} className="rounded-xl p-4 max-w-[calc(100vw-2rem)]"><p>Choose passage to replace</p>{workspace.panes.map((p,i)=><button className="block underline p-2" key={p.paneKey} onClick={()=>{if(controller.read().revision===capacity.revision){controller.open(capacity.ref,p.paneKey,capacity.picker);if(capacity.picker&&window.matchMedia('(max-width:767px)').matches)studies.setTool(null);}capacityDialog.current?.close();setCapacity(null);}}>Replace passage {i+1}: {referenceLabel(p.ref)}</button>)}<button className="underline p-2" onClick={()=>{if(controller.read().revision===capacity.revision)controller.newTab(capacity.ref,false);capacityDialog.current?.close();setCapacity(null);}}>Open in new tab</button><button autoFocus className="underline p-2" onClick={()=>{capacityDialog.current?.close();setCapacity(null);}}>Cancel</button></dialog>}
        <button ref={focusButton} type="button" className={control} aria-label={focused ? 'Exit focus mode' : 'Enter focus mode'} aria-pressed={focused} onClick={() => changeFocus(!focused)} title={focused ? 'Exit focus mode (Escape)' : 'Hide header and word analysis'}>
          {focused ? <Minimize2 size={16} aria-hidden="true" /> : <Maximize2 size={16} aria-hidden="true" />}
          <span className="hidden sm:inline">{focused ? 'Exit focus' : 'Focus mode'}</span>
        </button>
       </div>
       {studies.enabled&&<nav aria-label="Reader tools" className="inline-flex shrink-0 items-center gap-1 rounded-lg bg-stone-200/60 p-1">{studies.study&&<span title={studies.study.title} className="hidden lg:block max-w-48 truncate px-2 text-xs text-stone-500">{studies.study.title}</span>}{(['studies','analysis'] as const).map(tool=><button key={tool} className={`rounded-md px-3 py-1 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-amber-600 ${studies.tool===tool?'bg-white text-stone-900 shadow-sm':'text-stone-600 hover:bg-white/60 hover:text-stone-900'}`} aria-pressed={studies.tool===tool} onClick={()=>tool==='studies'?studies.openStudies():studies.setTool(studies.tool==='analysis'?null:'analysis')}>{tool==='studies'?'Studies':'Analysis'}</button>)}</nav>}
        {books.loading && <span className="text-sm text-stone-400">Loading books…</span>}
        {books.error && <p role="alert" className="text-sm text-red-700">Could not load books. <button className="underline" onClick={books.refetch}>Retry books</button></p>}
      </div>
      {studies.enabled&&studies.accountError&&<p role="alert">{studies.accountError} <button className="underline" onClick={()=>void studies.loadStudies()}>Retry account access</button></p>}
      {studies.enabled&&studies.error&&studies.tool==='analysis'&&<p role="alert">{studies.error} <button className="underline" onClick={()=>void studies.loadStudies()}>Retry Studies</button></p>}
      {single&&comparing&&<div role="group" aria-label="Visible passage" className="flex flex-wrap gap-2 shrink-0">{workspace.panes.map((p,i)=><button key={p.paneKey} className={`${control} min-w-0`} aria-controls={`passage-${i+1}`} aria-label={`Show passage ${i+1}: ${referenceLabel(p.ref)}`} aria-pressed={workspace.activePaneKey===p.paneKey} onClick={()=>controller.activate(p.paneKey)}>{i+1}: {referenceLabel(p.ref)}</button>)}</div>}
      <div className="flex flex-col md:flex-row md:justify-center gap-4 flex-1 min-h-0">
        <div id="workspace-panel" role="tabpanel" aria-labelledby={workspaceTabId(workspace.tabKey)} ref={grid} className={`${studies.enabled&&studies.tool?'hidden md:grid':'grid'} gap-4 flex-1 min-w-0 min-h-0 ${!comparing?'md:max-w-[44rem]':''}`} style={{gridTemplateColumns:`repeat(${single?1:columns},minmax(0,1fr))`,gridTemplateRows:`repeat(${single?1:rows},minmax(0,1fr))`}}>
          {workspace.panes.map((p,i)=>{const start=referenceStart(p.ref);return <PassagePane active={workspace.activePaneKey===p.paneKey} focused={focused} key={p.paneKey} paneKey={p.paneKey} anchor={p.anchor} picker={p.picker} reference={p.ref} onActivate={()=>controller.activate(p.paneKey)} number={i+1} targetRevision={p.seek??p.generation} targetVerse={start.verse} book={p.ref.book_id} chapter={start.chapter} books={books.data?.data??[]} comparing={comparing} visible={!single||workspace.activePaneKey===p.paneKey} selectedWordId={selected?.pane===p.paneKey?selected.word.id:null} matchKey={(previewWord??selected?.word)?.match_key??null} onPreview={preview} onNavigate={(b,c,r)=>navigate(p.paneKey,b,c,undefined,r)} onWord={(w,v,retain)=>chooseWord(p.paneKey,w,v,retain)} onClose={comparing||controller.tabs.length>1?()=>controller.close(p.paneKey):undefined}/>;})}
        </div>
        {studies.enabled&&<aside data-inspector-scroll key={studies.accountKey} hidden={!studies.tool} aria-label="Study tools" className="min-h-0 overflow-y-auto bg-white border border-stone-200 rounded-xl shrink-0 w-full md:w-80 max-h-full flex-1 md:flex-none"><button className="underline m-3 md:hidden" onClick={()=>studies.setTool(null)}>Return to reader</button><div hidden={studies.tool!=='studies'}><StudiesPanel onOpenNewTab={reference=>controller.newTab(reference,false)} activeReference={controller.historyHeld?undefined:active.valid?active.ref:selected?.pane===active.paneKey?makeReference(selected.book,{kind:'verse_range',start:{chapter:selected.chapter,verse:selected.verse},end:{chapter:selected.chapter,verse:selected.verse}}):undefined} onOpen={reference=>{controller.open(reference);studies.setTool(null);}}/></div><div hidden={studies.tool!=='analysis'}><div role="tablist" aria-label="Analysis" className="flex border-b">{(['Word','Occurrences','Notes'] as const).map(tab=><button key={tab} role="tab" aria-selected={studies.analysisTab===tab} disabled={tab!=='Notes'&&!selected} className="flex-1 p-2 disabled:opacity-40" onClick={()=>studies.setAnalysisTab(tab)}>{tab}</button>)}</div><div hidden={studies.analysisTab!=='Notes'}><RelevantNotes reference={active.valid&&!controller.historyHeld?active.ref:undefined}/><NoteEditor onOpen={reference=>{controller.open(reference);if(window.matchMedia('(max-width:767px)').matches)studies.setTool(null);}}/></div><div hidden={studies.analysisTab==='Notes'}>{studies.tool==='analysis'&&morphology.loading&&<p role="status">Loading word analysis…</p>}{studies.tool==='analysis'&&morphology.data&&selected&&morphology.data.id===selected.word.id&&<WordStudy exposed={studies.analysisTab!=='Notes'} memoryKey={selected.key} hideTabs controlledTab={studies.analysisTab==='Occurrences'?'Occurrences':'Word'} key={`${selected.pane}:${selected.word.id}`} word={morphology.data} context={context} books={books.data?.data??[]} onClose={()=>{setSelection(null);studies.setAnalysisTab('Notes');}} onOpen={open} />}</div></div></aside>}
        {selected && !focused && (!studies.enabled||!studies.tool) && <aside data-inspector-scroll aria-label="Word analysis panel" className={`min-h-0 max-h-[45%] overflow-y-auto overscroll-contain shrink-0 md:max-h-full md:h-full md:w-72`}>
          {morphology.loading && <p role="status" className="p-4 bg-white">Loading word analysis… <button className="underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.error && <p role="alert" className="bg-white p-4 text-sm text-red-700">Could not load word analysis. <button className="underline" onClick={morphology.refetch}>Retry word analysis</button><button className="ml-2 underline" onClick={() => setSelection(null)}>Close</button></p>}
          {morphology.data && morphology.data.id === selected.word.id && <WordStudy memoryKey={selected.key} key={`${selected.pane}:${selected.word.id}`} word={morphology.data} context={context} books={books.data?.data ?? []} onClose={() => setSelection(null)} onOpen={open} />}
        </aside>}
      </div>
    </div>
  );
}
