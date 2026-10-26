import {useEffect,useRef,useState} from 'react';
import {useWorkspace} from '@/context/ReaderWorkspaceContext';
import {useStudies} from '@/context/StudiesContext';
import {aggregate,status,type HighlightAnchor,type Evidence} from '@/lib/own-highlights';
import {referenceLabel,makeReference} from '@/lib/passage-references';
import type {VerseWithWordsResponse} from '@/schemas/bible.schema';
export type Phrase={start:number;end:number};
export function selectedAnchor(verses:VerseWithWordsResponse[],phrase:Phrase):HighlightAnchor|null{
 const flat=verses.flatMap(verse=>verse.words.map(word=>({verse,word}))),selected=flat.slice(phrase.start,phrase.end+1);
 if(!selected.length)return null;
 const first=selected[0].verse.anchor_evidence;if(first?.status!=='ready')return null;
 const segments:HighlightAnchor['segments']=[];
 for(const {verse,word} of selected){
  const e=verse.anchor_evidence;if(e?.status!=='ready'||['source_id','source_revision','catalogue_version','versification_id','tokenization_version'].some(key=>e[key as keyof typeof e]!==first[key as keyof typeof first]))return null;
  const id=e.observed_word_ids[word.position-1];if(typeof id!=='string')return null;
  let segment=segments[segments.length-1];
  if(!segment||JSON.stringify(segment.reference)!==JSON.stringify(e.reference)){segment={reference:e.reference,start_position:word.position,end_position:word.position,observed_word_ids:[],verse_token_digest:e.verse_token_digest};segments.push(segment);}
  segment.end_position=word.position;segment.observed_word_ids.push(id);
 }
 return {version:1,source_id:first.source_id,source_revision:first.source_revision,catalogue_version:first.catalogue_version,versification_id:first.versification_id,tokenization_version:first.tokenization_version,segments};
}
export function paintFor(verses:VerseWithWordsResponse[],highlights:import('@/lib/own-highlights').NoteHighlight[]){
 const paint=new Map<string,import('@/lib/own-highlights').NoteHighlight>();
 const byPoint=new Map(verses.map(v=>[`${v.chapter_num}:${v.verse_num}`,v]));
 for(const highlight of [...highlights].sort((a,b)=>a.id.localeCompare(b.id)))for(const segment of highlight.anchor.segments){
  const target=segment.reference.target;if(target.kind!=='verse_range')continue;
  const verse=byPoint.get(`${target.start.chapter}:${target.start.verse}`);
  if(!verse||status(highlight.anchor,verse.anchor_evidence,segment)!=='valid')continue;
  for(let position=segment.start_position;position<=segment.end_position;position++){const key=`${verse.id}:${position}`;if(!paint.has(key))paint.set(key,highlight);}
 }
 return paint;
}
export function OwnHighlightActions({book,verses,phrase,origin,clear}:{book:string;verses:VerseWithWordsResponse[];phrase:Phrase|null;origin:string;clear:()=>void}){
 const studies=useStudies(),workspace=useWorkspace(),[palette,setPalette]=useState(false),[choosing,setChoosing]=useState(false),[colour,setColour]=useState('#FFE066'),[message,setMessage]=useState(''),[repair,setRepair]=useState<string|undefined>();
 const latest=useRef({studies,workspace,origin});latest.current={studies,workspace,origin};
 const captureAccount=useRef(studies.accountKey);
 const captured=useRef<{origin:string;account:string;tab:string;revision:number;source:VerseWithWordsResponse[];note?:string;generation?:number}|undefined>(undefined);
 useEffect(()=>{if(captureAccount.current!==studies.accountKey){captureAccount.current=studies.accountKey;captured.current=undefined;}else if(phrase){captured.current={origin,account:studies.accountKey,tab:workspace.workspace.tabKey,revision:workspace.read().revision,source:verses,note:studies.current??undefined,generation:studies.lane?.generation};}setPalette(false);setChoosing(false);setMessage('');},[phrase,origin,studies.accountKey]);
 const fresh=(destination=true)=>{const c=captured.current,l=latest.current;return !!c&&c.origin===l.origin&&c.source===verses&&c.account===l.studies.accountKey&&c.tab===l.workspace.read().tabKey&&c.revision===l.workspace.read().revision&&(!destination||(c.note===(l.studies.current??undefined)&&c.generation===l.studies.lane?.generation));};
 useEffect(()=>{setRepair(undefined);},[studies.current,studies.accountKey,origin]);
 const anchor=phrase?selectedAnchor(verses,phrase):null;
 function refreshDestination(id:string){const l=latest.current;if(captured.current){captured.current.note=id;captured.current.generation=l.studies.editorLanes.find(lane=>lane.note.id===id)?.generation??0;}}
 function signedIn(){if(studies.accountKey==='anonymous'){window.dispatchEvent(new Event('scribeswell-account-entry'));return false;}return true;}
 function highlight(){if(!signedIn())return;if(!fresh()){clear();return;}if(!studies.lane){setChoosing(true);return;}setPalette(true);}
 async function choose(id:string){if(!fresh(false))return;await studies.openNote(id);if(fresh(false)){refreshDestination(id);setChoosing(false);setPalette(true);}}
 async function create(mark=false){if(!fresh(false)||!studies.study)return;const first=verses.flatMap(v=>v.words.map(()=>v))[phrase?.start??0],last=verses.flatMap(v=>v.words.map(()=>v))[phrase?.end??0];if(!first||!last)return;
  const ref=makeReference(first.anchor_evidence?.status==='ready'?first.anchor_evidence.book:book,{kind:'verse_range',start:{chapter:first.chapter_num,verse:first.verse_num},end:{chapter:last.chapter_num,verse:last.verse_num}});
  const id=await studies.addNote({format_version:3,document:{version:1,blocks:[]},connections:[{id:crypto.randomUUID(),reference:ref}],highlights:[]});
  if(id&&fresh(false)){refreshDestination(id);setChoosing(false);setPalette(mark);if(!mark)clear();}
 }
 const destination=studies.lane?.value.document.blocks.flatMap(b=>b.type==='paragraph'?[b]:b.items.flat()).flatMap(p=>p.content).map(i=>i.type==='text'?i.text:i.type==='passage_link'?i.label:i.content.map(t=>t.text).join('')).join('').slice(0,60)||'Empty note';
 const all=verses.flatMap(v=>v.words.map(()=>v));
 async function collect(){if(!fresh(false)||!phrase)return;const first=all[phrase.start],last=all[phrase.end];const ref=makeReference(book,{kind:'verse_range',start:{chapter:first.chapter_num,verse:first.verse_num},end:{chapter:last.chapter_num,verse:last.verse_num}});const added=await studies.collect(ref);if(fresh(false))setMessage(added?'Passage added to study.':latest.current.studies.collection?.message??'Passage could not be added. Retry in My studies.');}
 const classifications=(studies.lane?aggregate(studies.lane.value).highlights:[]).flatMap(h=>h.anchor.segments.flatMap(s=>{const p=s.reference.target.kind==='verse_range'?s.reference.target.start:null;const v=p&&s.reference.book_id===book&&verses.find(v=>v.chapter_num===p.chapter&&v.verse_num===p.verse);if(!v)return [];return [{h,s,state:status(h.anchor,v.anchor_evidence as Evidence|undefined,s)}];}));
 const summaries=new Map<string,(typeof classifications)[number]>(),severity={valid:0,unavailable:1,needs_review:2};
 for(const item of classifications){const previous=summaries.get(item.h.id);if(!previous||severity[item.state]>severity[previous.state])summaries.set(item.h.id,item);}
 const blocked=!studies.lane||studies.lane.invalid||studies.lane.composing||!!studies.lane.deletion||studies.studyDeletionPaused;
 function dismiss(){setRepair(undefined);clear();}
 function editMark(action:Parameters<typeof studies.mark>[0]){if(!studies.lane||!studies.mark(action,studies.lane))setMessage('This highlight could not be changed. Finish editing the note or reduce its size, then try again.');}
 return <>
 {studies.enabled&&studies.lane&&<p className="text-sm p-2" aria-live="polite" data-highlight-save><span dir="auto">Current note: {destination}</span> · {studies.lane.invalid||studies.lane.status==='failed'||studies.lane.status==='conflict'?'Changes not saved':studies.lane.status==='saved'?'Draft saved':'Saving…'}{studies.lane.status==='failed'&&<button className="underline ml-2" onClick={()=>void studies.retry(studies.lane)}>Retry note save</button>}</p>}
 {studies.enabled&&classifications.length>0&&<details className="text-sm p-2"><summary>Current note highlights</summary><p dir="auto">{studies.study?.title} · {destination}</p>{[...summaries.values()].map(({h,s,state})=><div key={h.id} className="flex flex-wrap items-center gap-2 py-1"><span>{referenceLabel(s.reference)} · {state==='valid'?'Valid':state==='needs_review'?'Needs review':'Unavailable'}</span><label>Colour<input aria-label={`Colour ${h.id}`} type="color" disabled={blocked} value={h.colour} onChange={e=>editMark({kind:'colour',id:h.id,colour:e.target.value.toUpperCase()})}/></label><button disabled={blocked} className="underline" onClick={()=>editMark({kind:'remove',id:h.id})}>Remove highlight</button>{state==='needs_review'&&<button disabled={blocked} className="underline" onClick={()=>{setRepair(h.id);setColour(h.colour);setMessage('Reselect the intended words, then choose Highlight.');}}>Reselect to repair</button>}</div>)}</details>}
 {repair&&<p className="text-sm p-2">Repairing selected highlight. <button className="underline" onClick={()=>{setRepair(undefined);setPalette(false);setMessage('');}}>Cancel repair</button></p>}
 {message&&!phrase&&<p role="status">{message}</p>}
 {studies.enabled&&phrase&&<section aria-label="Selected phrase actions" onMouseDown={e=>e.preventDefault()} className="fixed bottom-2 inset-x-2 z-40 rounded-xl border bg-white p-3 shadow-lg md:sticky md:bottom-auto md:inset-x-auto md:top-0">
 <div className="flex flex-wrap gap-4"><button className="underline" onClick={highlight}>Highlight</button><button className="underline" onClick={()=>{if(!signedIn())return;if(!studies.study){setChoosing(true);return;}void create();}}>Add note</button><button className="underline" onClick={()=>{if(!signedIn())return;if(!studies.study){setChoosing(true);return;}void collect();}}>Add to study</button><button className="underline" onClick={dismiss}>Dismiss selection</button></div>
 {choosing&&<div aria-label="Choose own note" className="space-y-2"><p>Choose an own note for these words.</p>{studies.notes.map(note=><button key={note.id} className="block underline" onClick={()=>void choose(note.id)}>{note.value.document.blocks.flatMap(b=>b.type==='paragraph'?[b]:b.items.flat()).flatMap(p=>p.content).map(i=>i.type==='text'?i.text:i.type==='passage_link'?i.label:'').join('').slice(0,60)||'Empty note'}</button>)}{studies.notesCursor&&<button className="underline" disabled={studies.busy} onClick={()=>void studies.moreNotes()}>More own notes</button>}{studies.study?<button className="underline" onClick={()=>void create(true)}>Create own note</button>:<button className="underline" onClick={()=>{studies.setTool('studies');void studies.loadStudies();}}>Choose or create a study in My studies</button>}</div>}
 {palette&&<div aria-label="Highlight colour palette" className="flex flex-wrap items-center gap-3 mt-3"><span>Current note: {destination}</span><button className="underline" onClick={()=>{setPalette(false);setChoosing(true);}}>Change</button><label>Colour<input aria-label="Highlight colour" type="color" value={colour} onChange={e=>setColour(e.target.value.toUpperCase())}/></label><button className="underline" disabled={!anchor} onClick={()=>{if(!fresh()||!anchor||!studies.lane){setMessage('Select these words again before highlighting.');return;}if(studies.mark({kind:'add',anchor,colour,repair},studies.lane)){setRepair(undefined);clear();}else setMessage('Finish editing this note before adding a highlight.');}}>Apply highlight</button>{!anchor&&<p>Highlight evidence unavailable. Your reading and writing remain available.</p>}</div>}
 {message&&<p role="status">{message}</p>}
 </section>}
 </>;
}
