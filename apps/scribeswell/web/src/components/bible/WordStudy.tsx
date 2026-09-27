import {useState} from 'react';
import {MorphologyPanel} from './MorphologyPanel';
import {useAsync, useVerses} from '@/hooks/useBible';
import {getLexicon, getOccurrences} from '@/lib/api-client';
import type {BookResponse, LexiconNode, WordWithMorphologyResponse} from '@/schemas/bible.schema';

type Reference = {book:string; chapter:number; verse:number};
type Props = {currentPane:1|2; word:WordWithMorphologyResponse; context:string; books:BookResponse[]; onClose:()=>void; onOpen:(pane:1|2,book:string,chapter:number,verse:number)=>void};
export function WordStudy({word,context,books,onClose,onOpen,currentPane}:Props) {
  const [tab,setTab] = useState<'Word'|'Occurrences'>('Word');
  const [book,setBook] = useState('');
  const [offset,setOffset] = useState(0);
  const [requested,setRequested] = useState(false);
  const [reference,setReference] = useState<Reference|null>(null);
  const legacyIds = word.lemma_strong?.split('/').map(s=>s.trim().replace(/^H/,'')).filter(s=>/^[1-9][0-9]*(?: [a-z])?$/.test(s))??[];
  const identity = word.lexical_id !== undefined ? word.lexical_id : legacyIds.length===1 ? legacyIds[0] : null;
  const lexical = useAsync(()=>identity?getLexicon(identity):Promise.resolve(null),[identity]);
  const occurrences = useAsync(()=>identity&&requested?getOccurrences(identity,book,offset):Promise.resolve(null),[identity,requested,book,offset]);
  const preview = useVerses(reference?.book??null,reference?.chapter??null);
  const previewVerse = preview.data?.data.find(v=>v.verse_num===reference?.verse);
  function nodes(items:LexiconNode[]) {return items.map((node,index)=>{
    if(node.kind==='language') return <bdi key={index} className={node.language==='he'?'font-hebrew':undefined} lang={node.language??undefined} dir={node.direction==='rtl'?'rtl':'auto'}>{nodes(node.children??[])}</bdi>;
    if(node.kind==='sense') return <div key={index} className="my-2 pl-3 border-l border-stone-200">{node.text&&<strong>{node.text}. </strong>}{nodes(node.children??[])}</div>;
    if(node.kind==='reference'&&node.book&&node.chapter&&node.verse&&books.some(b=>b.osis_id===node.book))return <button key={index} className="underline text-amber-800" onClick={()=>setReference({book:node.book!,chapter:node.chapter!,verse:node.verse!})}>{node.text}</button>;
    return <span key={index}>{node.text}</span>;
  });}
  return <div className="bg-white rounded-xl border border-stone-200">
    <div className="sticky top-0 z-20 bg-white rounded-t-xl"><div className="p-3 flex justify-between items-start"><div><p className="text-xs text-stone-500">{context}</p><p aria-label={`Hebrew word: ${word.display_he}`} className="font-hebrew text-3xl" dir="rtl" lang="he">{word.display_he??word.surface_he}</p></div><button aria-label="Close morphology panel" className="p-2 text-stone-500" onClick={onClose}>×</button></div>
    <div role="tablist" aria-label="Word study" className="flex bg-white border-b border-stone-200 rounded-t-xl">
      {(['Word','Occurrences'] as const).map(name=><button key={name} id={`study-tab-${name}`} role="tab" aria-controls={`study-${name}`} aria-selected={tab===name} tabIndex={tab===name?0:-1} onKeyDown={event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const next=event.key==='Home'?'Word':event.key==='End'?'Occurrences':name==='Word'?'Occurrences':'Word';setTab(next);setRequested(true);document.getElementById(`study-tab-${next}`)?.focus();}}} onClick={()=>{setTab(name);if(name==='Occurrences')setRequested(true);}} className={`flex-1 p-3 text-sm ${tab===name?'border-b-2 border-amber-600 font-semibold':''}`}>{name}</button>)}
    </div></div>
    <div role="tabpanel" id="study-Word" aria-labelledby="study-tab-Word" hidden={tab!=='Word'}>
      <div className="p-4 text-sm space-y-2">
        {identity&&<p className="text-xs font-mono text-stone-500">Strong’s {identity}</p>}
        {word.morph_code&&<p className="text-xs font-mono text-stone-500">{word.morph_code}</p>}
        {lexical.loading&&<p role="status">Loading dictionary…</p>}
        {(lexical.error||lexical.data?.status==='unavailable')&&<p>Dictionary temporarily unavailable. <button className="underline" onClick={lexical.refetch}>Retry dictionary</button></p>}
        {(!identity||lexical.data?.status==='missing')&&<p>No dictionary entry for this word.</p>}
        {lexical.data?.status==='available'&&<>
          <p className="font-hebrew text-2xl" dir="rtl" lang="he">{lexical.data.lemma}</p>
          <p>{lexical.data.transliteration||'Transliteration not supplied'}</p>
          <p>{lexical.data.definition||'Short definition not supplied'}</p>
          <p>Root: {lexical.data.root?<span lang="he" dir="rtl" className="font-hebrew">{lexical.data.root.text}</span>:'Not recorded'}</p>
          {lexical.data.pronunciation&&<p>Pronunciation: {lexical.data.pronunciation} <span className="text-stone-500">(written)</span></p>}
          <details><summary className="cursor-pointer">Strong’s definition and usage</summary><div className="space-y-2 mt-2"><p>{lexical.data.strong_definition}</p><p>{lexical.data.strong_usage}</p><p className="text-stone-500">{lexical.data.strong_source}</p><p className="text-xs text-stone-500">Dictionary senses and usage, not a translation of this verse. Strong’s may combine augmented senses.</p></div></details>
          <details><summary className="cursor-pointer">BDB outline</summary><p className="text-xs text-stone-500 my-2">Incomplete source · entry status: {lexical.data.bdb_status}</p>{lexical.data.bdb.length?nodes(lexical.data.bdb):<p>No outline supplied.</p>}</details>
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
      <MorphologyPanel hideHeader word={word} onClose={onClose}/>
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
      <button className="underline" onClick={onClose}>Close word study</button>
    </div>
  </div>;
}
