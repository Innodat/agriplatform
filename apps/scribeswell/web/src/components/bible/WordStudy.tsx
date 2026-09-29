import {useLayoutEffect, useRef, useState} from 'react';
import {MorphologyPanel} from './MorphologyPanel';
import {useAsync, useVerses} from '@/hooks/useBible';
import {getLexicon, getOccurrences} from '@/lib/api-client';
import type {BookResponse, LexiconNode, WordWithMorphologyResponse} from '@/schemas/bible.schema';

type Reference = {book:string; chapter:number; verse:number};
type Props = {currentPane:1|2; word:WordWithMorphologyResponse; context:string; books:BookResponse[]; onClose:()=>void; onOpen:(pane:1|2,book:string,chapter:number,verse:number)=>void};
type View = {identity:string|null; linked:boolean; tab:'Word'|'Occurrences'; book:string; offset:number; requested:boolean; reference:Reference|null; strong:boolean; bdb:boolean; scroll:number; focusId?:string};
function initialView(identity:string|null,linked=false):View {return {identity,linked,tab:'Word',book:'',offset:0,requested:false,reference:null,strong:false,bdb:false,scroll:0};}
// Stop at a contiguous prefix; bound both text and nested block layout. Links
// are atomic, and grapheme segmentation keeps Hebrew points with their letter.
function previewNodes(items:LexiconNode[]) {
  const Segmenter=(Intl as unknown as {Segmenter:new(locale:string,options:{granularity:string})=>{segment:(text:string)=>Iterable<{segment:string}>}}).Segmenter;
  const segmenter=new Segmenter('he',{granularity:'grapheme'});
  const graphemes=(text:string)=>Array.from(segmenter.segment(text),part=>part.segment);
  const plain=(node:LexiconNode):string=>node.children?.length?node.children.map(plain).join(''):node.text;
  let remaining=240,blocks=0,truncated=false;
  function take(nodes:LexiconNode[]):LexiconNode[] {
    const result:LexiconNode[]=[];
    for(const node of nodes){
      if(truncated)break;
      if(node.kind==='sense'&&++blocks>2){truncated=true;break;}
      if(node.kind==='reference'||node.kind==='dictionary_reference'){
        const size=graphemes(plain(node)).length;
        if(size>remaining){truncated=true;break;}
        remaining-=size;result.push(node);
      }else if(node.children?.length){
        const children=take(node.children);
        if(children.length)result.push({...node,children});
      }else{
        const text=graphemes(node.text);
        if(text.length>remaining){result.push({...node,text:text.slice(0,remaining).join('')});truncated=true;break;}
        remaining-=text.length;result.push(node);
      }
    }
    return result;
  }
  return {nodes:take(items),truncated};
}
export function WordStudy(props:Props) {
  const {word}=props;
  const legacyIds=word.lemma_strong?.split('/').map(s=>s.trim().replace(/^H/,'')).filter(s=>/^[1-9][0-9]*(?: [a-z])?$/.test(s))??[];
  const identity=word.lexical_id!==undefined?word.lexical_id:legacyIds.length===1?legacyIds[0]:null;
  const [view,setView]=useState(()=>initialView(identity));
  const [history,setHistory]=useState<View[]>([]);
  const [revision,setRevision]=useState(0);
  function follow(next:string,snapshot:View){
    if(next===view.identity)return;
    setHistory(old=>[...old,snapshot]);setView(initialView(next,true));setRevision(n=>n+1);
  }
  function back(){const previous=history[history.length-1];if(!previous)return;setHistory(old=>old.slice(0,-1));setView(previous);setRevision(n=>n+1);}
  return <StudyEntry key={revision} {...props} initial={view} canBack={history.length>0} onBack={back} onFollow={follow}/>;
}
function StudyEntry({word,context,books,onClose,onOpen,currentPane,initial,canBack,onBack,onFollow}:Props&{initial:View;canBack:boolean;onBack:()=>void;onFollow:(identity:string,view:View)=>void}) {
  const [tab,setTab]=useState(initial.tab);
  const [book,setBook]=useState(initial.book);
  const [offset,setOffset]=useState(initial.offset);
  const [requested,setRequested]=useState(initial.requested);
  const [reference,setReference]=useState(initial.reference);
  const [strong,setStrong]=useState(initial.strong);
  const strongDisclosure=useRef<HTMLDetailsElement>(null);
  const [bdb,setBdb]=useState(initial.bdb);
  const element=useRef<HTMLDivElement>(null);
  const restored=useRef(false);
  const identity=initial.identity;
  const lexical = useAsync(()=>identity?getLexicon(identity):Promise.resolve(null),[identity]);
  const occurrences = useAsync(()=>identity&&requested?getOccurrences(identity,book,offset):Promise.resolve(null),[identity,requested,book,offset]);
  const preview = useVerses(reference?.book??null,reference?.chapter??null);
  const previewVerse = preview.data?.data.find(v=>v.verse_num===reference?.verse);
  const inspector=()=>element.current?.closest<HTMLElement>('[data-inspector-scroll]');
  // Give navigation an immediate focus destination, including failed lookups.
  useLayoutEffect(()=>{
    if(initial.linked||initial.focusId)element.current?.focus({preventScroll:true});
    const scroll=inspector();
    if(scroll)scroll.scrollTop=0;
    const cancel=()=>{restored.current=true;};
    const onScroll=()=>{if(scroll&&scroll.scrollTop>0)cancel();};
    scroll?.addEventListener('wheel',cancel,{passive:true});
    scroll?.addEventListener('touchmove',cancel,{passive:true});
    scroll?.addEventListener('scroll',onScroll,{passive:true});
    return ()=>{scroll?.removeEventListener('wheel',cancel);scroll?.removeEventListener('touchmove',cancel);scroll?.removeEventListener('scroll',onScroll);};
  },[]);
  useLayoutEffect(()=>{
    if(restored.current||lexical.loading||lexical.error||lexical.data?.status==='unavailable'||(tab==='Occurrences'&&(occurrences.loading||occurrences.error))||(reference&&(preview.loading||preview.error)))return;
    restored.current=true;
    const scroll=inspector();
    if(scroll)scroll.scrollTop=initial.scroll;
    if(initial.linked||initial.focusId){
      const origin=Array.from(element.current?.querySelectorAll<HTMLElement>('[data-dictionary-link]')??[]).find(el=>el.dataset.dictionaryLink===initial.focusId);
      const target=origin??(tab==='Word'?element.current?.querySelector<HTMLElement>('[data-entry-heading]'):null);
      (target&&!target.closest('[hidden]')?target:element.current)?.focus({preventScroll:true});
    }
  },[lexical.loading,lexical.error,lexical.data,occurrences.loading,occurrences.error,preview.loading,preview.error,tab,reference,initial]);
  function changeTab(next:'Word'|'Occurrences'){restored.current=true;setTab(next);}
  function follow(next:string,origin:HTMLElement){onFollow(next,{...initial,tab,book,offset,requested,reference,strong:strongDisclosure.current?.open??strong,bdb,focusId:origin.dataset.dictionaryLink,scroll:inspector()?.scrollTop??0});}
  const outline=previewNodes(lexical.data?.bdb??[]);
  function nodes(items:LexiconNode[],path="bdb") {return items.map((node,index)=>{
    const key=`${path}.${index}`;
    if(node.kind==='dictionary_reference'&&node.lexical_id&&node.lexical_id!==identity)return <button key={index} className="cursor-pointer underline text-amber-800 break-words" aria-label={`Open dictionary entry ${node.lexical_id}`} data-dictionary-link={key} onClick={event=>follow(node.lexical_id!,event.currentTarget)}><bdi lang={node.language??undefined} dir={node.direction==='rtl'?'rtl':'auto'} className={node.language==='he'?'font-hebrew':undefined}>{node.children?.length?nodes(node.children,key):node.text}</bdi></button>;
    if(node.kind==='language'||node.kind==='dictionary_reference') return <bdi key={index} className={node.language==='he'?'font-hebrew':undefined} lang={node.language??undefined} dir={node.direction==='rtl'?'rtl':'auto'}>{node.children?.length?nodes(node.children,key):node.text}</bdi>;
    if(node.kind==='sense') return <div key={index} className="my-2 pl-3 border-l border-stone-200">{node.text&&<strong>{node.text}. </strong>}{nodes(node.children??[],key)}</div>;
    if(node.kind==='reference'&&node.book&&node.chapter&&node.verse&&books.some(b=>b.osis_id===node.book))return <button key={index} className="underline text-amber-800" onClick={()=>setReference({book:node.book!,chapter:node.chapter!,verse:node.verse!})}>{node.text}</button>;
    return <span key={index}>{node.text}</span>;
  });}
  return <div ref={element} tabIndex={-1} aria-label="Dictionary inspector" className="bg-white rounded-xl border border-stone-200 min-w-0 break-words">
    <div className="sticky top-0 z-20 bg-white rounded-t-xl"><div className="p-3 flex justify-between items-start gap-2"><div className="min-w-0">{canBack&&<button className="underline text-sm mb-1" aria-label="Back to previous dictionary entry" onClick={onBack}>← Back</button>}<p className="text-xs text-stone-500">Selected word · <span>{context}</span></p><bdi aria-label={`Hebrew word: ${word.display_he}`} className="font-hebrew text-lg" dir="rtl" lang="he">{word.display_he??word.surface_he}</bdi>{initial.linked&&<p className="text-xs text-stone-500">Dictionary entry · Strong’s {identity}</p>}</div><button aria-label="Close morphology panel" className="p-2 text-stone-500" onClick={onClose}>×</button></div>
    <div role="tablist" aria-label="Word study" className="flex bg-white border-b border-stone-200 rounded-t-xl">
      {(['Word','Occurrences'] as const).map(name=><button key={name} id={`study-tab-${name}`} role="tab" aria-controls={`study-${name}`} aria-selected={tab===name} tabIndex={tab===name?0:-1} onKeyDown={event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const next=event.key==='Home'?'Word':event.key==='End'?'Occurrences':name==='Word'?'Occurrences':'Word';changeTab(next);setRequested(true);document.getElementById(`study-tab-${next}`)?.focus();}}} onClick={()=>{changeTab(name);if(name==='Occurrences')setRequested(true);}} className={`flex-1 p-3 text-sm ${tab===name?'border-b-2 border-amber-600 font-semibold':''}`}>{name}</button>)}
    </div></div>
    <div role="tabpanel" id="study-Word" aria-labelledby="study-tab-Word" hidden={tab!=='Word'}>
      <div className="p-4 text-sm space-y-2">
        {lexical.loading&&<p role="status">Loading dictionary…</p>}
        {(lexical.error||lexical.data?.status==='unavailable')&&<p>Dictionary temporarily unavailable. <button className="underline" onClick={lexical.refetch}>Retry dictionary</button></p>}
        {(!identity||lexical.data?.status==='missing')&&<p>No dictionary entry for this word.</p>}
        {lexical.data?.status==='available'&&<>
          <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 min-w-0">
            <h2 data-entry-heading tabIndex={-1} className="font-hebrew text-3xl font-bold outline-none" dir="rtl" lang="he">{lexical.data.lemma}</h2>
            {lexical.data.transliteration&&<span className="text-stone-500">{lexical.data.transliteration}</span>}
            <span className="text-stone-700">{lexical.data.definition||'Short definition not supplied'}</span>
          </div>
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-xs text-stone-500">
            <span>Strong’s {identity}</span><span>Root: {lexical.data.root?(lexical.data.root.lexical_id&&lexical.data.root.lexical_id!==identity?<button className="cursor-pointer underline text-amber-800" aria-label={`Open dictionary entry ${lexical.data.root.lexical_id}`} data-dictionary-link="root" onClick={event=>follow(lexical.data!.root!.lexical_id!,event.currentTarget)}><bdi lang="he" dir="rtl" className="font-hebrew text-lg">{lexical.data.root.text}</bdi></button>:<bdi lang="he" dir="rtl" className="font-hebrew text-lg">{lexical.data.root.text}</bdi>):'Not recorded'}</span>
          </div>
        </>}
        {!initial.linked&&<MorphologyPanel word={word}/>}
        {lexical.data?.status==='available'&&<>
          <section aria-label="BDB outline"><h3 className="font-semibold">BDB outline</h3>
            <p className="text-xs text-stone-500 my-1">Incomplete source · entry status: {lexical.data.bdb_status}</p>
            <div data-bdb-content className="leading-relaxed">{lexical.data.bdb.length?nodes(bdb?lexical.data.bdb:outline.nodes):<p>No outline supplied.</p>}</div>
            {outline.truncated&&<button className="underline text-amber-800 mt-1" aria-expanded={bdb} onClick={()=>setBdb(!bdb)}>{bdb?'Show less':'Show more'}</button>}
          </section>
          <details ref={strongDisclosure} open={strong} onToggle={event=>setStrong(event.currentTarget.open)}><summary className="cursor-pointer">Strong’s definition and usage</summary><div className="space-y-2 mt-2">
            <p>{lexical.data.strong_definition_nodes.length?nodes(lexical.data.strong_definition_nodes,"strong-definition"):lexical.data.strong_definition}</p>
            <p>{lexical.data.strong_usage_nodes.length?nodes(lexical.data.strong_usage_nodes,"strong-usage"):lexical.data.strong_usage}</p>
            <p className="text-stone-500">{lexical.data.strong_source_nodes.length?nodes(lexical.data.strong_source_nodes,"strong-source"):lexical.data.strong_source}</p>
            <p className="text-xs text-stone-500">Dictionary senses and usage, not a translation of this verse. Strong’s may combine augmented senses.</p>
          </div></details>
          {lexical.data.pronunciation&&<p className="text-xs text-stone-500">Pronunciation: {lexical.data.pronunciation} (written)</p>}
          <p className="text-xs text-stone-500"><a className="underline" href="https://github.com/openscriptures/HebrewLexicon">Open Scriptures Hebrew Bible Project</a> · <a className="underline" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · BDB is incomplete.</p>
        </>}
        {reference&&<section aria-label="Scripture preview" className="border rounded p-2 space-y-2">
          <p>{reference.book} {reference.chapter}:{reference.verse}</p>
          {preview.loading&&<p role="status">Loading verse…</p>}
          {preview.error&&<p>Verse unavailable. <button className="underline" onClick={preview.refetch}>Retry preview</button></p>}
          {preview.data&&<p dir="rtl" lang="he" className="font-hebrew text-lg">{preview.data.data.find(v=>v.verse_num===reference.verse)?.words.map(w=>w.display_he??w.surface_he).join(' ')||'Verse not present in this collection.'}</p>}
          <button className="underline mr-3 disabled:opacity-40" disabled={!previewVerse} onClick={()=>{if(previewVerse)onOpen(currentPane,reference.book,reference.chapter,reference.verse);}}>Open in current passage</button><button className="underline disabled:opacity-40" disabled={!previewVerse} onClick={()=>{if(previewVerse)onOpen(currentPane===1?2:1,reference.book,reference.chapter,reference.verse);}}>Open in comparison</button>
          <button className="block underline" onClick={()=>setReference(null)}>Close preview</button>
        </section>}
      </div>
    </div>
    <div role="tabpanel" id="study-Occurrences" aria-labelledby="study-tab-Occurrences" hidden={tab!=='Occurrences'} className="p-4 text-sm space-y-3">
      <p>Exact lemma: {identity??'Unavailable'}</p>
      <label className="block">Book <select aria-label="Filter occurrences by book" className="w-full border rounded p-1" value={book} onChange={event=>{setBook(event.target.value);setOffset(0);}}><option value="">All books</option>{books.map(b=><option key={b.id} value={b.osis_id}>{b.name_en}</option>)}</select></label>
      {!identity&&<p>No lexical identity is available for lookup.</p>}
      {occurrences.loading&&requested&&<p role="status">Loading occurrences…</p>}
      {occurrences.error&&<p>Could not load occurrences. <button className="underline" onClick={occurrences.refetch}>Retry occurrences</button></p>}
      {occurrences.data&&<><p>{occurrences.data.total} word occurrences in {occurrences.data.verse_total} verses</p>{!occurrences.data.total&&<p>No matching occurrences.</p>}
        <ol className="space-y-3">{occurrences.data.data.map(row=><li key={row.id} className="border-b pb-2"><p>{row.book_name} {row.chapter}:{row.verse} · word {row.position}</p><p className="font-hebrew text-xl" dir="rtl" lang="he">{row.display_he??row.surface_he}</p><button className="underline mr-2" onClick={()=>onOpen(currentPane,row.book,row.chapter,row.verse)}>Open in current passage</button><button className="underline" onClick={()=>onOpen(currentPane===1?2:1,row.book,row.chapter,row.verse)}>Open in comparison</button></li>)}</ol>
        <div className="flex justify-between"><button disabled={offset===0} className="underline disabled:opacity-30" onClick={()=>setOffset(Math.max(0,offset-25))}>Previous results</button><button disabled={offset+25>=occurrences.data.total} className="underline disabled:opacity-30" onClick={()=>setOffset(offset+25)}>Next results</button></div>
      </>}
    </div>
  </div>;
}
