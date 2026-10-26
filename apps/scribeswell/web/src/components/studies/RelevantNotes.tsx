import {useEffect,useRef,useState} from 'react';
import {useAuth} from '@/context/AuthContext';
import {useStudies,SavedNoteReview} from '@/context/StudiesContext';
import {useWorkspace} from '@/context/ReaderWorkspaceContext';
import {api,NotesFailure,type NoteView} from '@/lib/personal-notes';
import type {ContextNote} from '@/generated/personal-notes/types.gen';
import {referenceKey,referenceLabel,type PassageReference} from '@/lib/passage-references';

/** Inspection is a separate authorized read; only explicit Open selects a lane. */
export function RelevantNotes({reference}:{reference?:PassageReference}){
 const studies=useStudies(),owner=useWorkspace(),{session}=useAuth();
 const pane=owner.workspace.panes.find(p=>p.paneKey===owner.workspace.activePaneKey);
 const exposed=studies.tool==='analysis'&&studies.analysisTab==='Notes';
 const context=JSON.stringify([studies.accountKey,session?.access_token,owner.workspace.tabKey,owner.workspace.incarnation,pane?.paneKey,pane?.generation,reference?referenceKey(reference):null,studies.searchMasked,studies.study?.id,studies.study?.revision,studies.current,exposed]);
 const latest=useRef(context);latest.current=context;
 const sequence=useRef(0),previewSequence=useRef(0);
 const [items,setItems]=useState<ContextNote[]>([]),[cursor,setCursor]=useState<string|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[retryMore,setRetryMore]=useState(false);
 const [preview,setPreview]=useState<NoteView>(),[previewError,setPreviewError]=useState(''),[previewBusy,setPreviewBusy]=useState(false);
 const [previewTarget,setPreviewTarget]=useState<ContextNote>(),[previewUnavailable,setPreviewUnavailable]=useState(false);
 const [installed,setInstalled]=useState('');
 async function load(more=false){
  if(!exposed||!reference||!session||studies.searchMasked||more&&!cursor)return;
  const captured=context,read=++sequence.current,token=session.access_token,account=session.user.id,next=more?cursor:undefined;
  setBusy(true);setError('');setRetryMore(more);
  try{const result=await api.contextNotes(token,reference,next??undefined);
   if(latest.current!==captured||read!==sequence.current)return;
   if(result.items.some(item=>item.owner_account_id!==account))throw new NotesFailure('response_invalid');
   setItems(old=>[...new Map((more?[...old,...result.items]:result.items).map(item=>[item.note_id,item])).values()]);setCursor(result.next_cursor);setInstalled(captured);
  }catch(failure){if(latest.current!==captured||read!==sequence.current)return;
   const code=failure instanceof NotesFailure?failure.code:'';
   if(['authentication_required','studies_access_denied'].includes(code)){setItems([]);setPreview(undefined);setInstalled('');studies.privateReadFailure(failure);}
   else setError('Relevant notes could not be loaded. Reading and writing remain available.');
  }finally{if(latest.current===captured&&read===sequence.current)setBusy(false);}
 }
 useEffect(()=>{sequence.current++;previewSequence.current++;setItems([]);setCursor(null);setPreview(undefined);setPreviewTarget(undefined);setPreviewUnavailable(false);setPreviewError('');setPreviewBusy(false);setError('');setBusy(false);setInstalled('');void load();return()=>{sequence.current++;previewSequence.current++;};},[context]);
 async function inspect(item:ContextNote){
  if(!session||studies.searchMasked)return;const captured=context,read=++previewSequence.current;
  setPreviewTarget(item);setPreviewUnavailable(false);setPreview(undefined);setPreviewError('');setPreviewBusy(true);
  try{const result=await api.note(session.access_token,item.study_id,item.note_id);
   if(latest.current!==captured||read!==previewSequence.current)return;
   if(result.owner_account_id!==session.user.id)throw new NotesFailure('response_invalid');setPreview(result);
  }catch(failure){if(latest.current!==captured||read!==previewSequence.current)return;
   if(failure instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(failure.code)){setItems([]);setPreview(undefined);setInstalled('');studies.privateReadFailure(failure);}
   else {const unavailable=failure instanceof NotesFailure&&failure.code==='resource_unavailable';if(unavailable)setItems(old=>old.filter(candidate=>candidate.note_id!==item.note_id));setPreviewUnavailable(unavailable);setPreviewError(unavailable?'This note is unavailable.':'Preview could not be loaded.');}
  }finally{if(latest.current===captured&&read===previewSequence.current)setPreviewBusy(false);}
 }
 function closePreview(){previewSequence.current++;setPreview(undefined);setPreviewTarget(undefined);setPreviewError('');setPreviewBusy(false);setPreviewUnavailable(false);}
 if(!exposed||!session||studies.searchMasked||!reference)return null;
 const shown=installed===context?items:[];
 return <section aria-label="Relevant own notes" className="border-t p-3 space-y-2">
  <h3 className="font-semibold">Relevant own notes</h3><p className="text-sm">{referenceLabel(reference)} · Only you</p>
  {busy&&<p aria-live="polite">Loading relevant notes…</p>}
  {error&&<p role="alert">{error} <button className="underline" disabled={busy} onClick={()=>void load(retryMore)}>Retry relevant notes</button></p>}
  {!busy&&!error&&!shown.length&&<p>{cursor?'No readable notes on this page.':'No relevant saved notes.'}</p>}
  <ul>{shown.map(item=><li key={item.note_id} className="py-2"><p dir="auto">{item.preview||'Empty note'}</p><p dir="auto" className="text-sm">{item.study_title} · You · Saved preview</p><button className="underline mr-3" onClick={()=>void inspect(item)}>Preview</button><button className="underline" onClick={()=>void studies.openNote(item.note_id,item.study_id)}>Open</button></li>)}</ul>
  {cursor&&<button className="underline" disabled={busy} onClick={()=>void load(true)}>More relevant notes</button>}
  {previewBusy&&<p aria-live="polite">Loading preview…</p>}{installed===context&&previewError&&<p role="alert">{previewError} {!previewUnavailable&&previewTarget&&<button className="underline" onClick={()=>void inspect(previewTarget)}>Retry Preview</button>} <button className="underline" onClick={closePreview}>Close preview</button></p>}
  {installed===context&&preview&&<section aria-label="Relevant note preview"><h4>Saved note preview</h4>{studies.lane?.note.id===preview.id&&studies.lane.generation!==studies.lane.saved&&<p>Your current note also has local changes not shown in this saved preview.</p>}<SavedNoteReview value={preview.value}/><button className="underline" onClick={closePreview}>Close preview</button></section>}
 </section>;
}
