/** One in-memory account/note save lane, independent of mounted tool/editor views. */
import {createContext,useContext,useEffect,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {useWorkspace,useTabState,useTabRef} from './ReaderWorkspaceContext';
import {isReadableNoteValue} from '@/lib/note-value';
import {aggregate,noteReferences,referencesOverlap,type HighlightAnchor,type NoteHighlight} from '@/lib/own-highlights';
import {accountId,type PrivateSelection} from '@/lib/workspace-storage';
import {useAuth} from './AuthContext';
import {api,execute,NotesFailure,uuid,type NoteValue,type NoteView,type StudyView,type OperationAck,type Attempt,type PassageList} from '@/lib/personal-notes';
import {referenceKey,referenceLabel,validateReference,type PassageReference} from '@/lib/passage-references';
type PassageIntent={kind:'add';reference:PassageReference}|{kind:'remove';id:string;reference:PassageReference};
type CollectionLane={study:string;list?:PassageList;intent?:PassageIntent;attempt?:Attempt;confirmed?:OperationAck;running?:Promise<void>;status:'loading'|'ready'|'saving'|'failed'|'conflict'|'reviewed';message:string;read:number};
export type Lane={note:NoteView;value:NoteValue;generation:number;saved:number;status:'saved'|'pending'|'saving'|'failed'|'conflict';attempt?:Attempt;running?:Promise<void>;timer?:ReturnType<typeof setTimeout>;first?:number;composing:boolean;invalid:boolean;formatUnsupported?:boolean;abandoned?:boolean;deletion?:Deletion;latest?:NoteView;reviewing?:boolean};
type Deletion={lane:Lane;label:string;open:boolean;reviewing?:boolean;status:'preparing'|'ready'|'save-recovery'|'executing'|'unknown'|'conflict';message:string;review?:NoteValue;reviewRevision?:string;attempt?:Attempt};
type StudyDeletion={preparation?:number;study:StudyView;open:boolean;status:'preparing'|'ready'|'recovery'|'executing'|'unknown'|'conflict';message:string;attempt?:Attempt;review?:StudyView;running?:Promise<void>};
type TitleEdit={study:string;candidate:string;details?:boolean;introduction?:string;source_url?:string;review?:StudyView;base:string;open:boolean;status:'editing'|'saving'|'failed'|'conflict';message:string;confirmed?:OperationAck;attempt?:Attempt;running?:Promise<void>};
type Tool='studies'|'analysis'|null;
/** Match the exact note.replace JSON envelope used by flush; never accept a
 * mark that only fits when operation/revision fields are omitted. */
export function noteCommandFits(value:NoteValue,expected_revision:string){
 const payload={operation_id:'11111111-1111-4111-8111-111111111111',expected_revision,value};
 if(new TextEncoder().encode(JSON.stringify(payload)).length>262144)return false;
 const pending:[unknown,number][]=[[payload,1]];let nodes=0;
 while(pending.length){const [item,depth]=pending.pop()!;if(++nodes>32768||depth>16)return false;if(item&&typeof item==='object')for(const child of Object.values(item))pending.push([child,depth+1]);}
 return true;
}
function useStatefulStudies(){
 const workspace=useWorkspace();
 const {session}=useAuth();const account=session?.user.id,token=session?.access_token;
 const currentToken=useRef(token);currentToken.current=token;
 const identity=useRef(account);identity.current=account;
 const dataAccount=useRef(account);const [authority,setAuthority]=useState(true);
 const [accountError,setAccountError]=useState('');
 const epoch=useRef(0);const previous=useRef(account);
 if(previous.current!==account){previous.current=account;epoch.current++;workspace.views.clear();workspace.latest.current.workspace.label=undefined;for(const tab of workspace.latest.current.tabs){tab.label=undefined;tab.labelGeneration=0;}}
 const [analysisTab,setAnalysisTab]=useTabState<'Word'|'Occurrences'|'Notes'>('analysisTab','Notes');
 const [tool,setTool]=useTabState<Tool>('tool',null),[studies,setStudies]=useTabState<StudyView[]>('studies',[]),[study,setStudy]=useTabState<StudyView|null>('study',null,true),[notes,setNotes]=useTabState<NoteView[]>('notes',[],true),[current,setCurrent]=useTabState<string|null>('current',null,true),[error,setError]=useTabState('error',''),[busy,setBusy]=useTabState('busy',false);
 useTabState('restoredOutline',false,true);
 const [studyCursor,setStudyCursor]=useTabState<string|null>('studyCursor',null),[notesCursor,setNotesCursor]=useTabState<string|null>('notesCursor',null,true);
 const [searchCandidate,setSearchCandidate]=useTabState('searchCandidate',''),[libraryBusy,setLibraryBusy]=useTabState('libraryBusy',false),[libraryError,setLibraryError]=useTabState('libraryError',''),[libraryInputInvalid,setLibraryInputInvalid]=useTabState('libraryInputInvalid',false),[libraryVerified,setLibraryVerified]=useTabState('libraryVerified',false),[libraryRestore,setLibraryRestore]=useTabState('libraryRestore',0);
 // Passive scroll events from a collapsed list must not replace its saved return anchor.
 const library=useTabRef('library',{query:'',generation:0,depth:1,cursor:null as string|null,pending:false,positionLocked:false,position:{scroll:0,focus:''}});
 const lanes=useRef(new Map<string,Lane>()),[,render]=useState(0);const update=()=>render(x=>x+1);
 const [exitPrompt,setExitPrompt]=useState<{action:()=>void|Promise<void>;switching:boolean;discard?:Lane;fresh:()=>boolean;lane?:Lane;key:string}|null>(null);
 const collectionNavigation=useTabRef('collectionNavigation',0);
 const navigation=useTabRef('navigation',0),selectedStudy=useTabRef<string|undefined>('selectedStudy',undefined),notesPosition=useTabRef<string|null>('notesPosition',notesCursor),pendingPages=useTabRef('pendingPages',new Set<string>());
 selectedStudy.current=study?.id;
 const titles=useRef(new Map<string,TitleEdit>()),titleReads=useRef(new Map<string,number>());
 const activeTool=useTabRef('activeTool',tool);activeTool.current=tool;const lastFocused=useRef<HTMLElement|null>(null);
 useEffect(()=>{const remember=(event:FocusEvent)=>{if(event.target instanceof HTMLElement&&event.target!==document.body)lastFocused.current=event.target;};document.addEventListener('focusin',remember);return()=>document.removeEventListener('focusin',remember);},[]);
 const selectedNote=useTabRef('selectedNote',current);selectedNote.current=current;const deletionSequence=useRef(0);
 const [deletionFocus,setDeletionFocus]=useState<{epoch:number;navigation:number;study:string;source:HTMLElement}|null>(null);
 const deleted=useRef(new Set<string>()),deletions=useRef(new Map<string,Deletion>());const [deleteTarget,setDeleteTarget]=useState<string|null>(null);
 const childDeleteRunning=useRef(new Map<string,Promise<OperationAck>>());
 const [studyDeletedFocus,setStudyDeletedFocus]=useState<{captured:number;source:HTMLElement;navigation:number}|null>(null);
 const collections=useRef(new Map<string,CollectionLane>());
 const deletedStudies=useRef(new Set<string>()),studyDeletions=useRef(new Map<string,StudyDeletion>());
 const [studyDeleteTarget,setStudyDeleteTarget]=useState<string|null>(null);
 const creationRunning=useRef<Promise<OperationAck>|undefined>(undefined),creationConfirmed=useRef<OperationAck|undefined>(undefined);
 const metadataReads=useRef(new Map<string,Set<Promise<StudyView|undefined>>>());
 const studyBlocked=(id:string)=>deletedStudies.current.has(id)||studyDeletions.current.has(id);
 const liveStudy=(id:string)=>!deletedStudies.current.has(id);
 const creationOrigin=useRef<{key:string;navigation:{current:number};generation:number;tool:Tool;source?:Lane;resume:()=>Promise<unknown>}|undefined>(undefined);
 const creation=useRef<Attempt|undefined>(undefined);const enrollment=useRef<string|undefined>(undefined);
 useEffect(()=>{hydrated.current.clear();for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;childDeleteRunning.current.clear();setStudyDeletedFocus(null);deletedStudies.current.clear();studyDeletions.current.clear();setStudyDeleteTarget(null);creationRunning.current=undefined;creationConfirmed.current=undefined;metadataReads.current.clear();setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();navigation.current++;pendingPages.current.clear();notesPosition.current=null;creation.current=undefined;creationOrigin.current=undefined;enrollment.current=undefined;setStudies([]);setStudy(null);setNotes([]);setCurrent(null);setError('');setBusy(false);setExitPrompt(null);setStudyCursor(null);setNotesCursor(null);dataAccount.current=account;setAuthority(true);setAccountError('');library.current={query:'',generation:library.current.generation+1,depth:1,cursor:null,pending:false,positionLocked:false,position:{scroll:0,focus:''}};setSearchCandidate('');setLibraryError('');setLibraryInputInvalid(false);setLibraryBusy(false);setLibraryVerified(false);},[account]);
 // Remember selections only from acknowledged owner-owned resources. Pending records
 // remain separate from live empty views while verification or a service is unavailable.
 const hydrated=useRef(new Set<string>());
 workspace.privateProjection.current=()=>{
  if(!account)return [];
  const result:PrivateSelection[]=[];
  for(const tab of workspace.latest.current.tabs){
   const fields=workspace.views.get(tab.tabKey),selected=fields?.get('study') as StudyView|null|undefined,id=fields?.get('current') as string|null|undefined;
   const pending=workspace.remembered?.account===account?workspace.remembered.tabs.find(t=>t.tabKey===tab.tabKey&&t.incarnation===tab.incarnation):undefined;
   const owned=selected?.owner_account_id===account&&accountId(selected.id)?selected:undefined;
   const acknowledged=id?lanes.current.get(id)?.note:undefined;
   const association=owned?{study:owned.id,...(acknowledged?.owner_account_id===account&&acknowledged.study_id===owned.id&&accountId(acknowledged.id)?{note:acknowledged.id}:{})}:{};
   if(!owned&&pending&&!hydrated.current.has(JSON.stringify([account,tab.tabKey,tab.incarnation]))){const {label,...selection}=pending;result.push(tab.labelGeneration>0?{...selection,...(tab.label?{label:tab.label}:{})}:pending);continue;}
   if(owned||tab.label)result.push({tabKey:tab.tabKey,incarnation:tab.incarnation,...association,...(tab.label?{label:tab.label}:{})});
  }
  return result;
 };
 useEffect(()=>{
  const saved=workspace.remembered;
  if(!saved||!account||!token||workspace.verifiedAccount!==account||saved.account!==account||!workspace.deviceReady)return;
  if(workspace.privateIntent!==workspace.latest.current.deviceIntent.current){workspace.privateRestoreFailure();return;}
  const captured=epoch.current,capturedToken=token,cancel=new AbortController(),end=setTimeout(()=>cancel.abort(),30000);
  let finished=0;
  const queue=saved.tabs.slice().sort((a,b)=>Number(b.tabKey===workspace.workspace.tabKey)-Number(a.tabKey===workspace.workspace.tabKey));
  const worker=async()=>{while(queue.length&&!cancel.signal.aborted){
   const candidate=queue.shift()!,tab=workspace.latest.current.tabs.find(t=>t.tabKey===candidate.tabKey&&t.incarnation===candidate.incarnation);
   if(!tab||hydrated.current.has(JSON.stringify([account,tab.tabKey,tab.incarnation])))continue;
   let fields=workspace.views.get(tab.tabKey);if(!fields){fields=new Map();workspace.views.set(tab.tabKey,fields);}
   const capturedFields=fields,nav=fields.get('ref:navigation') as {current:number}|undefined,navigationGeneration=nav?.current;
   const initialStudy=fields.get('study'),initialNote=fields.get('current'),intent=workspace.latest.current.deviceIntent.current;
   const laneAtStart=candidate.note?lanes.current.get(candidate.note):undefined,laneInput=laneAtStart?.generation;
   const fresh=()=>!cancel.signal.aborted&&valid(captured)&&currentToken.current===capturedToken&&workspace.views.get(tab.tabKey)===capturedFields&&workspace.latest.current.tabs.some(t=>t.tabKey===tab.tabKey&&t.incarnation===candidate.incarnation)&&workspace.latest.current.deviceIntent.current===intent&&capturedFields.get('study')===initialStudy&&capturedFields.get('current')===initialNote&&(nav?.current===navigationGeneration);
   let requestedNote=false;
   try{
    const selected=candidate.study?await api.study(capturedToken,candidate.study,cancel.signal):undefined;
    if(candidate.study&&(!selected||selected.id!==candidate.study||selected.owner_account_id!==account))throw new NotesFailure('response_invalid');
    requestedNote=!!(candidate.note&&candidate.study);
    const note=candidate.note&&candidate.study?await api.note(capturedToken,candidate.study,candidate.note,cancel.signal):undefined;
    if(candidate.note&&(!note||note.id!==candidate.note||note.study_id!==candidate.study||note.owner_account_id!==account))throw new NotesFailure('response_invalid');
    if(!selected)await api.studies(capturedToken,undefined,cancel.signal);
    if(!fresh()){if(!cancel.signal.aborted)workspace.privateRestoreFailure();continue;}
    if(note){
     const existing=lanes.current.get(note.id);
     if(existing){
      // Fresh authority can reattach an unchanged retained lane, including its
      // dirty buffer/original command. Input arriving during this read wins.
      if(laneAtStart&&(existing!==laneAtStart||existing.generation!==laneInput)||!laneAtStart&&(existing.generation!==existing.saved||existing.attempt||existing.composing||existing.invalid)){workspace.privateRestoreFailure();continue;}
      if(existing.status==='saved'&&existing.generation===existing.saved&&!existing.attempt&&!existing.composing&&!existing.invalid&&BigInt(note.revision)>=BigInt(existing.note.revision)){existing.note=note;existing.value=note.value;}
     }else lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});
    }
    if(selected){capturedFields.set('study',selected);capturedFields.set('notes',note?[note]:[]);capturedFields.set('current',note?.id??null);capturedFields.set('restoredOutline',true);}
    if(candidate.label&&tab.labelGeneration===0)tab.label=candidate.label;
    hydrated.current.add(JSON.stringify([account,tab.tabKey,tab.incarnation]));setAuthority(true);workspace.redraw();workspace.checkpoint();
   }catch(error){
    const code=error instanceof NotesFailure?error.code:'';
    // Current account admission denial invalidates every private view, even
    // after the originating tab's navigation or tool intent has changed.
    if((code==='studies_access_denied'||code==='authentication_required')&&!cancel.signal.aborted&&valid(captured)&&currentToken.current===capturedToken){fail(error,code==='authentication_required');continue;}
    if(candidate.study&&['resource_unavailable','study_not_found','note_not_found','resource_not_found','scribeswell_study_not_found','scribeswell_note_not_found','resource_access_denied'].includes(code)&&!cancel.signal.aborted&&valid(captured)&&currentToken.current===capturedToken){
     const deniedNote=requestedNote?candidate.note:undefined;
     clearResourceContexts(candidate.study,deniedNote);
     for(let i=queue.length-1;i>=0;i--)if(queue[i].study===candidate.study&&(!deniedNote||queue[i].note===deniedNote))queue.splice(i,1);
     continue;
    }
    if(!fresh())continue;
    workspace.privateRestoreFailure();
   }
  }};
  void Promise.all([worker(),worker()]).finally(()=>{finished=1;clearTimeout(end);});
  cancel.signal.addEventListener('abort',()=>{if(!finished)workspace.privateRestoreFailure();},{once:true});
  return()=>{finished=1;clearTimeout(end);cancel.abort();};
 },[workspace.remembered,workspace.verifiedAccount,workspace.deviceReady,workspace.deviceInstalled,workspace.privateIntent,account,token]);
 /** Confirmed resource unavailability fans out through this existing owner registry.
  * A note denial retains its authorized study and independently selected notes. */
 function clearResourceContexts(parent:string,note?:string){
  for(const tab of workspace.latest.current.tabs){
   const fields=workspace.views.get(tab.tabKey),selected=fields?.get('study') as StudyView|undefined;
   const affected=note?fields?.get('current')===note:selected?.id===parent;
   if(fields){
    const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.filter(item=>note?item.id!==note:item.study_id!==parent));
    const studies=fields.get('studies') as StudyView[]|undefined;if(!note&&studies)fields.set('studies',studies.filter(item=>item.id!==parent));
    if(affected){fields.set('current',null);if(!note){fields.set('study',null);fields.set('notes',[]);}const navigation=fields.get('ref:navigation') as {current:number}|undefined;if(navigation)navigation.current++;}
   }
   if(affected){tab.label=undefined;tab.labelGeneration=0;hydrated.current.delete(JSON.stringify([account,tab.tabKey,tab.incarnation]));}
  }
  for(const lane of lanes.current.values())if(note?lane.note.id===note:lane.note.study_id===parent){clearTimeout(lane.timer);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);setDeleteTarget(current=>current===lane.note.id?null:current);}
  if(!note){titles.current.delete(parent);titleReads.current.delete(parent);collections.current.delete(parent);studyDeletions.current.delete(parent);setStudyDeleteTarget(current=>current===parent?null:current);}
  workspace.clearRememberedResource(parent,note);workspace.redraw();workspace.checkpoint();
 }
 function authorizedToken(){if(identity.current!==account||!currentToken.current)throw new NotesFailure('authentication_required');return currentToken.current;}
 function valid(captured:number){return epoch.current===captured&&identity.current===account;}
 function fail(failure:unknown,restoreMask=false){
  const code=failure instanceof NotesFailure?failure.code:'studies_storage_unavailable';
  if((code==='authentication_required'||code==='studies_access_denied')&&!workspace.latest.current.tabs.some(tab=>tab.tabKey===workspace.workspace.tabKey))setAccountError(code==='authentication_required'?'Sign in to use My studies.':'Studies access is unavailable for this account.');
  if(code==='authentication_required'){
   if(restoreMask){workspace.retainPrivateForRetry();hydrated.current.clear();
   // Keep actual buffers/unknown attempts in the account lanes. Live private
   // selections and labels stay empty until their own current GET succeeds.
   for(const tab of workspace.latest.current.tabs){tab.label=undefined;tab.labelGeneration=0;const fields=workspace.views.get(tab.tabKey);if(!fields)continue;fields.set('study',null);fields.set('current',null);fields.set('notes',[]);fields.set('studies',[]);fields.set('libraryVerified',false);const navigation=fields.get('ref:navigation') as {current:number}|undefined;if(navigation)navigation.current++;}
   workspace.redraw();}
   setStudyDeleteTarget(null);for(const target of studyDeletions.current.values()){target.open=false;if(target.status==='executing'){target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}}setDeleteTarget(null);for(const target of deletions.current.values()){target.open=false;if(target.status==='executing'){target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}}epoch.current++;library.current.pending=false;setLibraryBusy(false);setLibraryVerified(false);setAuthority(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);}
  if(code==='studies_access_denied'){
   workspace.forgetRemembered();
   workspace.views.clear();if(workspace.latest.current.tabs.some(tab=>tab.tabKey===workspace.workspace.tabKey))workspace.views.set(workspace.workspace.tabKey,new Map<string,unknown>([['tool',activeTool.current],['error','Studies access is unavailable for this account.']]));workspace.latest.current.workspace.label=undefined;for(const tab of workspace.latest.current.tabs){tab.label=undefined;tab.labelGeneration=0;}setAuthority(false);workspace.redraw();
   epoch.current++;library.current.generation++;library.current.query='';library.current.depth=1;library.current.cursor=null;library.current.position={scroll:0,focus:''};library.current.positionLocked=false;setSearchCandidate('');setLibraryVerified(false);setLibraryBusy(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;childDeleteRunning.current.clear();setStudyDeletedFocus(null);deletedStudies.current.clear();studyDeletions.current.clear();setStudyDeleteTarget(null);creationRunning.current=undefined;creationConfirmed.current=undefined;metadataReads.current.clear();setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();setStudies([]);setNotes([]);setStudy(null);setCurrent(null);creation.current=undefined;creationOrigin.current=undefined;enrollment.current=undefined;
  }
  setBusy(false);setError(code==='studies_access_denied'?'Studies access is unavailable for this account.':code==='authentication_required'?'Sign in to use My studies.':'Studies could not be loaded. Try again.');
 }
 async function loadStudies(more=false,query=library.current.query,changed=false){
  if(!more&&!changed&&workspace.views.get(workspace.workspace.tabKey)?.get('restoredOutline')&&workspace.views.get(workspace.workspace.tabKey)?.get('study')){await loadRestoredOutline();return;}
  const state=library.current;
  if(more&&(state.pending||!state.cursor))return;
  if(more)state.positionLocked=false;
  const captured=epoch.current,requestNavigation=navigation.current;
  const generation=more?state.generation:++state.generation;
  // A refreshed return keeps that anchor protected until the visible restoration finishes.
  if(!more)state.positionLocked=!changed;
  if(changed){state.query=query;state.depth=1;state.cursor=null;state.position={scroll:0,focus:''};setStudies([]);setStudyCursor(null);}
  const currentRead=()=>valid(captured)&&generation===library.current.generation&&requestNavigation===navigation.current;
  state.pending=true;setLibraryBusy(true);setLibraryError('');setLibraryInputInvalid(false);
  if(!more)setLibraryVerified(false);
  try{
   if(!token)throw new NotesFailure('authentication_required');
   let cursor=more?state.cursor:undefined,items:StudyView[]=[],pages=0;
   const depth=more?1:state.depth;
   do{
    const result=await api.search(authorizedToken(),query,cursor??undefined);
    if(!currentRead())return;
    items.push(...result.items);cursor=result.next_cursor;pages++;
   }while(cursor&&pages<depth);
   if(!currentRead())return;
   setAuthority(true);setAccountError('');setLibraryVerified(true);setError('');
   setStudies(old=>{const existing=new Map(old.map(item=>[item.id,item])),unique=new Map<string,StudyView>();for(const item of more?[...old,...items]:items){if(!liveStudy(item.id))continue;const known=existing.get(item.id);unique.set(item.id,known&&BigInt(known.revision)>BigInt(item.revision)?known:item);}return [...unique.values()];});
   state.cursor=cursor??null;state.depth=more?state.depth+pages:pages;setStudyCursor(state.cursor);if(!more&&!changed)setLibraryRestore(x=>x+1);
  }catch(failure){
   if(!currentRead())return;
   setLibraryVerified(false);
   const code=failure instanceof NotesFailure?failure.code:'studies_storage_unavailable';
   if(code==='studies_access_denied'||code==='authentication_required')fail(failure);
   setLibraryInputInvalid(code==='scribeswell_personal_notes_input_invalid');
   setLibraryError(code==='scribeswell_personal_notes_input_invalid'?'Enter a valid search of up to 200 characters.':code==='studies_access_denied'?'Studies access is unavailable for this account.':code==='authentication_required'?'Sign in to use My studies.':'Studies could not be loaded. Try again.');
  }finally{if(currentRead()){state.pending=false;setLibraryBusy(false);}}
 }
 function changeSearchCandidate(value:string){if(identity.current===account&&dataAccount.current===account&&authority)setSearchCandidate(value);}
 function searchStudies(){if(!authority)return;return loadStudies(false,searchCandidate,true);}
 function clearSearch(){if(!authority)return;setSearchCandidate('');return loadStudies(false,'',true);}
 function rememberLibrary(scroll:number,focus?:string){if(library.current.positionLocked)return;library.current.position={scroll,focus:focus??library.current.position.focus};}
 function openStudies(){setTool(tool==='studies'?null:'studies');if(tool!=='studies'&&!study)void loadStudies();}
 useEffect(()=>{
  if(tool!=='studies'||!study||!authority||!workspace.deviceReady)return;
  const fields=workspace.views.get(workspace.workspace.tabKey);void loadRestoredOutline();
  return()=>{const active=fields?.get('restoredOutlineRead') as AbortController|undefined;active?.abort();fields?.delete('restoredOutlineRead');};
 },[tool,study,authority,workspace.deviceReady,workspace.workspace.tabKey,account,token]);
 async function flush(lane:Lane,retry=false):Promise<void>{
  if(lane.running)return lane.running;
  if(lane.deletion||studyBlocked(lane.note.study_id))return;
  if(!token||lane.invalid||lane.composing||lane.generation===lane.saved||lane.status==='conflict'||(lane.status==='failed'&&!retry))return;
  clearTimeout(lane.timer);lane.first=undefined;
  const captured=epoch.current;
  if(!lane.attempt){const operation_id=uuid();lane.attempt={operation_id,command:'note.replace',path:`/api/studies/${lane.note.study_id}/notes/${lane.note.id}`,method:'PUT',payload:{operation_id,expected_revision:lane.note.revision,value:structuredClone(lane.value)},study:lane.note.study_id,note:lane.note.id,generation:lane.generation};}
  const attempt=lane.attempt;lane.status='saving';update();
  lane.running=(async()=>{
   try{const result=await execute(authorizedToken(),attempt);if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane||deleted.current.has(lane.note.id))return;lane.note={...lane.note,revision:result.revision,value:attempt.payload.value as NoteValue};lane.saved=attempt.generation;for(const fields of workspace.views.values()){const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.map(note=>note.id===lane.note.id?lane.note:note));}lane.attempt=undefined;lane.status=lane.saved===lane.generation?'saved':'pending';}
   catch(e){if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane)return;const code=e instanceof NotesFailure?e.code:'';lane.status=['note_revision_conflict','note_format_unsupported','operation_payload_mismatch','resource_unavailable'].includes(code)?'conflict':'failed';if(code==='note_format_unsupported')lane.formatUnsupported=true;if(['scribeswell_personal_notes_input_invalid','highlight_proof_invalid','highlight_proof_unavailable'].includes(code))lane.attempt=undefined;if(['authentication_required','studies_access_denied'].includes(code))fail(e);}
   finally{lane.running=undefined;if(valid(captured)&&liveStudy(lane.note.study_id)&&lanes.current.get(lane.note.id)===lane){update();if(lane.status==='pending'&&!lane.deletion)schedule(lane);}}
  })();return lane.running;
 }
 function schedule(lane:Lane){clearTimeout(lane.timer);if(lane.abandoned||studyBlocked(lane.note.study_id)||lane.deletion||lane.composing||lane.running||lane.status==='failed'||lane.status==='conflict')return;const now=Date.now();lane.first??=now;lane.timer=setTimeout(()=>void flush(lane),Math.min(500,Math.max(0,2000-(now-lane.first))));}
 function change(value:NoteValue,bound?:Lane){const lane=bound??(current?lanes.current.get(current):undefined);if(!lane||lanes.current.get(lane.note.id)!==lane||dataAccount.current!==account||!authority||lane.deletion?.attempt||studyDeletions.current.get(lane.note.study_id)?.attempt)return;lane.value=value;lane.invalid=false;lane.generation++;if(lane.status!=='failed'&&lane.status!=='conflict')lane.status='pending';update();schedule(lane);}
 function mark(action:{kind:'add';anchor:HighlightAnchor;colour:string;repair?:string}|{kind:'colour';id:string;colour:string}|{kind:'remove';id:string},expected:Lane){
  const target=current?lanes.current.get(current):undefined;
  if(!target||target!==expected||target.invalid||target.composing||target.deletion||studyBlocked(target.note.study_id)||!authority||dataAccount.current!==account)return false;
  const value=aggregate(target.value);
  if(action.kind==='add'){
   const highlight:NoteHighlight={id:action.repair??uuid(),colour:action.colour,anchor:action.anchor};
   if(action.repair&&!value.highlights.some(h=>h.id===action.repair))return false;
   value.highlights=action.repair?value.highlights.map(h=>h.id===action.repair?highlight:h):[...value.highlights,highlight];
  }else if(action.kind==='remove')value.highlights=value.highlights.filter(h=>h.id!==action.id);
  else value.highlights=value.highlights.map(h=>h.id===action.id?{...h,colour:action.colour}:h);
  if(!isReadableNoteValue(value)||!noteCommandFits(value,target.note.revision))return false;
  change(value,target);return true;
 }
 function composition(active:boolean,bound?:Lane){const lane=bound??(current?lanes.current.get(current):undefined);if(lane&&lanes.current.get(lane.note.id)===lane&&dataAccount.current===account&&authority){lane.composing=active;if(active)clearTimeout(lane.timer);else schedule(lane);update();}}
 function contexts(lane:Lane,except?:string){return workspace.latest.current.tabs.filter(tab=>tab.tabKey!==except&&workspace.views.get(tab.tabKey)?.get('current')===lane.note.id);}
 async function exit(action:()=>void|Promise<void>,switching=false,key=workspace.workspace.tabKey,actionFresh=()=>true,forceLane?:Lane,deferBackground=false){
  const captured=epoch.current,fields=workspace.views.get(key),note=fields?.get('current') as string|undefined;
  const lane=forceLane??(note?lanes.current.get(note):undefined),nav=(fields?.get('ref:navigation') as {current:number}|undefined)?.current;
  const fresh=()=>valid(captured)&&workspace.views.get(key)===fields&&workspace.latest.current.tabs.some(tab=>tab.tabKey===key)&&fields?.get('current')===note&&(fields?.get('ref:navigation') as {current:number}|undefined)?.current===nav&&actionFresh();
  if(lane&&!lane.abandoned&&(forceLane||!contexts(lane,key).length)&&!lane.deletion&&!studyBlocked(lane.note.study_id)){
   const end=Date.now()+5000;
   while(lane.generation!==lane.saved&&!lane.invalid&&!lane.composing&&lane.status!=='failed'&&lane.status!=='conflict'&&Date.now()<end){
    await Promise.race([flush(lane),new Promise<void>(resolve=>setTimeout(resolve,Math.max(1,end-Date.now())))]);
    if(!fresh())return;
   }
   if(!fresh())return;
   if((forceLane||!contexts(lane,key).length)&&(lane.composing||lane.invalid||lane.generation!==lane.saved)){
    if(deferBackground&&workspace.latest.current.workspace.tabKey!==key){fields?.set('error','Changes not saved. Return to this note before switching.');workspace.redraw();return;}
    const input=lane.generation,composing=lane.composing,deletion=lane.deletion;
    setExitPrompt({action,switching,lane,key,fresh:()=>fresh()&&lane.generation===input&&lane.composing===composing&&lane.deletion===deletion&&lanes.current.get(lane.note.id)===lane&&!deleted.current.has(lane.note.id)&&liveStudy(lane.note.study_id),discard:forceLane?undefined:lane});return;
   }
  }
  if(fresh())await action();
 }
 /** One departure transaction against the final survivor set. Consent is staged;
  * buffers are abandoned only once every affected lane is approved and still fresh. */
 function exitDevice(survivors:string[],action:()=>void,actionFresh:()=>boolean){
  const captured=epoch.current,surviving=new Set(survivors);
  const removed=workspace.latest.current.tabs.filter(tab=>!surviving.has(tab.tabKey)).map(tab=>{
   const fields=workspace.views.get(tab.tabKey),note=fields?.get('current'),nav=fields?.get('ref:navigation') as {current:number}|undefined;
   return {tab,fields,note,nav,navigation:nav?.current};
  });
  const fresh=()=>valid(captured)&&actionFresh()&&removed.every(item=>workspace.latest.current.tabs.includes(item.tab)&&workspace.views.get(item.tab.tabKey)===item.fields&&item.fields?.get('current')===item.note&&item.nav?.current===item.navigation);
  const affected=[...new Set(removed.map(item=>typeof item.note==='string'?lanes.current.get(item.note):undefined).filter((lane):lane is Lane=>!!lane))].filter(lane=>!workspace.latest.current.tabs.some(tab=>surviving.has(tab.tabKey)&&workspace.views.get(tab.tabKey)?.get('current')===lane.note.id));
  const approved=new Map<Lane,{generation:number;composing:boolean;invalid:boolean;deletion:Lane['deletion']}>();
  const unchanged=()=>[...approved].every(([lane,state])=>lanes.current.get(lane.note.id)===lane&&lane.generation===state.generation&&lane.composing===state.composing&&lane.invalid===state.invalid&&lane.deletion===state.deletion&&!deleted.current.has(lane.note.id)&&liveStudy(lane.note.study_id));
  const next=async():Promise<void>=>{
   if(!fresh()||!unchanged())return;
   const lane=affected.find(lane=>!approved.has(lane));
   if(lane){const origin=removed.find(item=>item.note===lane.note.id)!;
    await exit(()=>{approved.set(lane,{generation:lane.generation,composing:lane.composing,invalid:lane.invalid,deletion:lane.deletion});return next();},false,origin.tab.tabKey,()=>fresh()&&unchanged(),lane);return;
   }
   if(!fresh()||!unchanged())return;
   for(const lane of approved.keys())if(lane.generation!==lane.saved||lane.composing||lane.invalid)abandonLane(lane);
   action();
  };
  void next();
 }
 function abandonLane(lane:Lane){
  clearTimeout(lane.timer);lane.abandoned=true;lane.composing=false;lane.invalid=false;
  if(lane.attempt){lane.value=structuredClone(lane.attempt.payload.value as NoteValue);lane.generation=lane.attempt.generation;}
  else lanes.current.delete(lane.note.id);
 }
 useLayoutEffect(()=>{
  workspace.departure.current=(key,action,fresh)=>{void exit(action,false,key,fresh);};
  workspace.deviceDeparture.current=exitDevice;
 });

 async function openStudy(id:string){
  if(!token||!liveStudy(id))return;const requestLibrary=++library.current.generation;library.current.pending=false;setLibraryBusy(false);const requestNavigation=++navigation.current;
  await exit(async()=>{if(requestNavigation!==navigation.current||requestLibrary!==library.current.generation)return;collectionNavigation.current++;const captured=epoch.current;setBusy(true);
   try{const [selected,page]=await Promise.all([api.study(authorizedToken(),id),api.notes(authorizedToken(),id)]);
    if(valid(captured)&&liveStudy(id)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation){await exit(()=>{if(!valid(captured)||requestNavigation!==navigation.current||requestLibrary!==library.current.generation)return;library.current.positionLocked=true;selectedStudy.current=selected.id;notesPosition.current=page.next_cursor;setStudy(selected);workspace.views.get(workspace.workspace.tabKey)?.set('restoredOutline',false);if(['study.create','study.copy'].includes(creation.current?.command??'')&&creation.current?.study===selected.id)retireCreation(creation.current);setNotes(page.items.filter(note=>!deleted.current.has(note.id)));setNotesCursor(page.next_cursor);setCurrent(null);setTool('studies');setError('');void loadPassages(selected.id);},true,workspace.workspace.tabKey,()=>requestNavigation===navigation.current&&requestLibrary===library.current.generation,undefined,true);}
   }catch(e){if(valid(captured)&&liveStudy(id)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation)fail(e);}finally{if(valid(captured)&&requestNavigation===navigation.current)setBusy(false);}
  },true);
 }
 // Restored selections attach without navigation. Read the visible outline only
 // when Studies is explicitly opened, preserving the single note/collection lanes.
 async function loadRestoredOutline(){
  const key=workspace.workspace.tabKey,fields=workspace.views.get(key),tab=workspace.latest.current.tabs.find(tab=>tab.tabKey===key);
  const selected=fields?.get('study') as StudyView|undefined,id=selected?.id;
  if(!fields||!tab||!id||!token||!authority||!fields.get('restoredOutline')||fields.get('restoredOutlineRead'))return;
  const captured=epoch.current,capturedToken=token,incarnation=tab.incarnation,intent=workspace.latest.current.deviceIntent.current,note=fields.get('current'),nav=fields.get('ref:navigation') as {current:number}|undefined,generation=nav?.current;
  const attempt=new AbortController(),end=setTimeout(()=>attempt.abort(),30000),lane=collectionLane(id);
  fields.set('restoredOutlineRead',attempt);
  const currentRead=()=>valid(captured)&&currentToken.current===capturedToken&&workspace.views.get(key)===fields&&workspace.latest.current.tabs.includes(tab)&&workspace.latest.current.workspace.tabKey===key&&workspace.latest.current.deviceIntent.current===intent&&fields.get('study')===selected&&fields.get('current')===note&&nav?.current===generation&&fields.get('restoredOutlineRead')===attempt&&!studyBlocked(id);
  const fresh=()=>!attempt.signal.aborted&&currentRead();
  try{
   const page=await api.notes(capturedToken,id,undefined,attempt.signal);
   if(!fresh())return;
   if(!page||!Array.isArray(page.items)||!page.items.every(item=>item&&accountId(item.id)&&item.study_id===id&&item.owner_account_id===account)||new Set(page.items.map(item=>item.id)).size!==page.items.length||page.next_cursor!==null&&typeof page.next_cursor!=='string')throw new NotesFailure('response_invalid');
   if(lane.attempt||lane.running||lane.intent)return;
   const read=lane.read+1,collectionFresh=()=>fresh()&&collections.current.get(id)===lane&&lane.read===read&&!lane.attempt&&!lane.running&&!lane.intent;
   const latest=await refreshPassages(lane,captured,collectionFresh,attempt.signal);
   if(!latest||!collectionFresh())return;
   fields.set('notes',page.items.filter(item=>!deleted.current.has(item.id)));fields.set('notesCursor',page.next_cursor);
   const position=fields.get('ref:notesPosition') as {current:string|null}|undefined;if(position)position.current=page.next_cursor;
   fields.set('restoredOutline',false);fields.set('error','');lane.status='ready';lane.message='';workspace.redraw();
  }catch(error){
   if(valid(captured)&&currentToken.current===capturedToken&&!attempt.signal.aborted){const code=error instanceof NotesFailure?error.code:'';
    if(['authentication_required','studies_access_denied'].includes(code)){fail(error,code==='authentication_required');return;}
    if(['resource_unavailable','resource_access_denied','study_not_found','resource_not_found','scribeswell_study_not_found'].includes(code)){clearResourceContexts(id);return;}
   }
   if(currentRead()){fields.set('error','Study outline could not be loaded. Retry.');workspace.redraw();}
  }finally{
   clearTimeout(end);
   if(fields.get('restoredOutlineRead')===attempt){
    fields.delete('restoredOutlineRead');
    // New input wins over this read, but the still-visible partial outline must
    // have an explicit recovery path after a cancelled rename/delete dialog.
    if(fields.get('restoredOutline')&&!fields.get('error')&&valid(captured)&&currentToken.current===capturedToken&&workspace.views.get(key)===fields&&workspace.latest.current.tabs.some(live=>live.tabKey===key&&live.incarnation===incarnation)&&workspace.latest.current.workspace.tabKey===key&&(fields.get('study') as StudyView|undefined)?.id===id&&fields.get('current')===note&&fields.get('tool')==='studies'&&!studyBlocked(id)){
     fields.set('error','Study outline could not be loaded. Retry.');workspace.redraw();
    }
   }
  }
 }
 // Collection authority/revisions/recovery are independent of notes and metadata.
 function collectionLane(id:string){let lane=collections.current.get(id);if(!lane){lane={study:id,status:'loading',message:'',read:0};collections.current.set(id,lane);}return lane;}
 async function refreshPassages(lane:CollectionLane,captured:number,currentRead=()=>true,signal?:AbortSignal){
  if(!token)return;const read=++lane.read;const latest=await api.passages(authorizedToken(),lane.study,signal);
  if(!valid(captured)||!liveStudy(lane.study)||collections.current.get(lane.study)!==lane||read!==lane.read||!currentRead())return;
  const identifier=(value:unknown)=>typeof value==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value)&&value!=='00000000-0000-0000-0000-000000000000';
  if(!latest||Object.keys(latest).sort().join(',')!=='items,revision,study_id'||latest.study_id!==lane.study||!Array.isArray(latest.items)||latest.items.length>200||!latest.items.every(item=>item&&Object.keys(item).sort().join(',')==='id,reference'&&identifier(item.id)&&validateReference(item.reference))||new Set(latest.items.map(item=>item.id)).size!==latest.items.length||new Set(latest.items.map(item=>referenceKey(item.reference))).size!==latest.items.length||typeof latest.revision!=='string'||!(/^[1-9][0-9]{0,18}$/).test(latest.revision)||BigInt(latest.revision)>9223372036854775807n)throw new NotesFailure('response_invalid');
  if(!lane.list||BigInt(latest.revision)>=BigInt(lane.list.revision))lane.list=latest;
  update();return latest;
 }
 async function loadPassages(id:string){
  const lane=collectionLane(id),captured=epoch.current,requestNavigation=collectionNavigation.current;if(lane.attempt||lane.running)return;
  const read=lane.read+1,currentRead=()=>valid(captured)&&collections.current.get(id)===lane&&lane.read===read&&selectedStudy.current===id&&collectionNavigation.current===requestNavigation&&!lane.attempt&&!lane.running;
  try{const latest=await refreshPassages(lane,captured,currentRead);if(!latest||!currentRead())return;lane.status=lane.intent?'reviewed':'ready';lane.message=lane.intent?'Current passages loaded. Review the list, then explicitly try your change.':'';update();}
  catch(e){if(!currentRead())return;lane.status='failed';lane.message='Passages could not be loaded. Retry loading them.';update();if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}
 }
 async function savePassages(lane:CollectionLane){
  if(!token||studyBlocked(lane.study)||lane.running||lane.status==='conflict')return;
  if(!lane.attempt){if(!lane.list||!lane.intent)return;const intent=lane.intent;let items=structuredClone(lane.list.items);
   if(intent.kind==='add'){
    if(items.some(item=>referenceKey(item.reference)===referenceKey(intent.reference))){lane.message='Already in this study';lane.intent=undefined;lane.status='ready';update();return;}
    if(items.length>=200){lane.message='This study has 200 passages. Remove one before adding another.';update();return;}
    items.push({id:uuid(),reference:intent.reference});
   }else items=items.filter(item=>item.id!==intent.id);
   const operation_id=uuid();lane.attempt={operation_id,command:'study.passages.replace',path:`/api/studies/${lane.study}/passages`,method:'PUT',payload:{operation_id,expected_revision:lane.list.revision,items},study:lane.study,generation:0};
  }
  const captured=epoch.current,requestNavigation=navigation.current,attempt=lane.attempt;lane.read++;lane.status='saving';lane.message=lane.confirmed?'Passages saved. Refreshing current list…':'Saving passages…';update();
  lane.running=(async()=>{
   try{if(!lane.confirmed){lane.confirmed=await execute(authorizedToken(),attempt);if(!valid(captured)||!liveStudy(lane.study)||collections.current.get(lane.study)!==lane)return;}
    await refreshPassages(lane,captured);if(!valid(captured)||!liveStudy(lane.study)||collections.current.get(lane.study)!==lane)return;
    lane.attempt=undefined;lane.confirmed=undefined;lane.intent=undefined;lane.status='ready';lane.message='';
   }catch(e){if(!valid(captured)||!liveStudy(lane.study)||collections.current.get(lane.study)!==lane)return;const code=e instanceof NotesFailure?e.code:'';
    if(lane.confirmed){lane.status='failed';lane.message='Passages saved. Current list could not be refreshed. Retry loading it.';}
    else if(code==='passage_revision_conflict'){lane.status='conflict';lane.attempt=undefined;lane.message='Passages changed elsewhere. Load and review current passages before trying your change.';}
    else if(code==='scribeswell_personal_notes_input_invalid'){lane.status='ready';lane.attempt=undefined;lane.message='This passage could not be added. Check the reference.';}
    else{lane.status='failed';lane.message='Passages not saved. Retry the original change.';}
    if(selectedStudy.current===lane.study&&navigation.current===requestNavigation&&['authentication_required','studies_access_denied'].includes(code))fail(e);
   }finally{lane.running=undefined;if(valid(captured))update();}
  })();return lane.running;
 }
 async function collect(reference:PassageReference){if(!study||studyBlocked(study.id))return false;const lane=collectionLane(study.id);if(lane.attempt||lane.running||!lane.list||['conflict','reviewed'].includes(lane.status))return false;lane.intent={kind:'add',reference};await savePassages(lane);return !['This passage could not be added. Check the reference.','Already in this study'].includes(lane.message);}
 function removePassage(id:string){if(!study||studyBlocked(study.id))return;const lane=collectionLane(study.id);if(lane.attempt||lane.running||!lane.list||['conflict','reviewed'].includes(lane.status))return;const item=lane.list.items.find(item=>item.id===id);if(!item)return;lane.intent={kind:'remove',id,reference:item.reference};void savePassages(lane);}
 function retryPassages(){if(!study||studyBlocked(study.id))return;const lane=collectionLane(study.id);if(lane.attempt||lane.intent&&lane.status==='reviewed')void savePassages(lane);else void loadPassages(study.id);}
 function reviewPassages(){if(study)void loadPassages(study.id);}
 function cancelPassageIntent(){const lane=study?collections.current.get(study.id):undefined;if(lane&&!lane.attempt&&!lane.running){lane.intent=undefined;lane.status='ready';lane.message='';update();}}
 // Metadata has its own operation lane and never flushes/replaces a note buffer.
 async function readTitle(id:string,captured:number){
  if(!token)return;
  const latest=await api.study(authorizedToken(),id);
  if(!valid(captured)||!liveStudy(id))return;
  setStudies(old=>old.map(item=>item.id===id&&BigInt(item.revision)<=BigInt(latest.revision)?latest:item));
  for(const fields of workspace.views.values()){const shown=fields.get('study') as StudyView|undefined;if(shown?.id===id&&BigInt(shown.revision)<=BigInt(latest.revision))fields.set('study',latest);const list=fields.get('studies') as StudyView[]|undefined;if(list)fields.set('studies',list.map(item=>item.id===id&&BigInt(item.revision)<=BigInt(latest.revision)?latest:item));}
  if(selectedStudy.current===id)setStudy(old=>old?.id!==id||BigInt(old.revision)>BigInt(latest.revision)?old:latest);
  return latest;
 }
 function refreshTitle(id:string,captured:number){
  const reads=metadataReads.current.get(id)??new Set<Promise<StudyView|undefined>>();metadataReads.current.set(id,reads);
  const promise=readTitle(id,captured);reads.add(promise);void promise.then(()=>reads.delete(promise),()=>reads.delete(promise));return promise;
 }
 async function beginRename(details=false){
  if(!token||!study||busy||studyBlocked(study.id))return;
  const id=study.id,existing=titles.current.get(id);
  if(existing){existing.open=true;update();return;}
  const captured=epoch.current,requestNavigation=navigation.current,read=(titleReads.current.get(id)??0)+1;titleReads.current.set(id,read);setBusy(true);
  try{const latest=await refreshTitle(id,captured);
   if(!latest||!valid(captured)||requestNavigation!==navigation.current||selectedStudy.current!==id||titleReads.current.get(id)!==read)return;
   titles.current.set(id,{study:id,candidate:latest.title,details,introduction:latest.introduction??'',source_url:latest.source_url??'',base:latest.revision,open:true,status:'editing',message:''});update();
  }catch(e){if(valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===id&&titleReads.current.get(id)===read)fail(e);}
  finally{if(valid(captured)&&(requestNavigation===navigation.current||selectedStudy.current===id)&&titleReads.current.get(id)===read)setBusy(false);}
 }
 function changeTitle(candidate:string){const edit=study?titles.current.get(study.id):undefined;if(!edit||studyBlocked(edit.study)||edit.attempt||edit.running)return;edit.candidate=candidate;edit.message='';update();}
 function changeDetails(field:'introduction'|'source_url',value:string){const edit=study?titles.current.get(study.id):undefined;if(!edit||studyBlocked(edit.study)||edit.attempt||edit.running)return;edit[field]=value;edit.message='';update();}
 function cancelRename(){if(study)titleReads.current.set(study.id,(titleReads.current.get(study.id)??0)+1);const edit=study?titles.current.get(study.id):undefined;if(!edit)return;if(edit.attempt||edit.running)edit.open=false;else titles.current.delete(edit.study);update();}
 async function reloadTitle(){
  if(!study||!token)return;const edit=titles.current.get(study.id);if(!edit||edit.running)return;
  const captured=epoch.current,requestNavigation=navigation.current,read=(titleReads.current.get(edit.study)??0)+1;titleReads.current.set(edit.study,read);
  const currentRead=()=>valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===edit.study&&titles.current.get(edit.study)===edit&&titleReads.current.get(edit.study)===read&&!edit.attempt&&!edit.running;
  try{const latest=await refreshTitle(edit.study,captured);if(!latest||!currentRead())return;
   edit.base=latest.revision;edit.status='editing';edit.message=edit.details?'Current study details loaded for review. Your entered details are kept. Select Save to replace them.':'Current title: '+latest.title+'. Your entered title is kept. Select Save to rename.';if(edit.details)edit.review=latest;update();
  }catch(e){if(currentRead()){edit.message='Current title could not be loaded. Retry loading it.';update();if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}}
 }
 async function saveTitle(){
  if(!token||!study)return;const edit=titles.current.get(study.id);if(!edit||studyBlocked(edit.study)||edit.running||edit.status==='conflict')return;
  const captured=epoch.current;
  if(!edit.attempt){const operation_id=uuid();edit.attempt={operation_id,command:edit.details?'study.details.replace':'study.rename',path:`/api/studies/${edit.study}`+(edit.details?'':'/title'),method:'PUT',payload:{operation_id,expected_revision:edit.base,title:edit.candidate,...(edit.details?{introduction:edit.introduction||null,source_url:edit.source_url||null}:{})},study:edit.study,generation:0};}
  const attempt=edit.attempt;edit.status='saving';edit.message=edit.details?(edit.confirmed?'Study details saved. Refreshing current details…':'Saving study details…'):(edit.confirmed?'Title saved. Refreshing current title…':'Saving title…');update();
  edit.running=(async()=>{
   try{if(!edit.confirmed){const outcome=await execute(authorizedToken(),attempt);if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;edit.confirmed=outcome;}
    if(!valid(captured))return;
    // A receipt may describe an older rename; only a current read supplies the heading.
    await refreshTitle(edit.study,captured);if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;
    titles.current.delete(edit.study);
   }catch(e){if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;const code=e instanceof NotesFailure?e.code:'';
    if(edit.confirmed){edit.status='failed';edit.message=edit.details?'Study details saved. Current details could not be refreshed. Retry loading them.':'Title saved. Current title could not be refreshed. Retry loading it.';}
    else if(code==='study_revision_conflict'){edit.status='conflict';edit.attempt=undefined;edit.message=edit.details?'This study changed elsewhere. Load current details before saving.':'This study title changed elsewhere. Load current title before saving.';}
    else if(code==='scribeswell_personal_notes_input_invalid'){edit.status='editing';edit.attempt=undefined;edit.message=edit.details?'Check title (1–200 characters), introduction (up to 10000 characters) and safe HTTP or HTTPS source URL. Your entered details are kept.':'Enter a title of 1–200 characters without control characters.';}
    else {edit.status='failed';edit.message=edit.details?'Study details not saved. Retry the original save.':'Title not saved. Retry the original rename.';}
    if(['authentication_required','studies_access_denied'].includes(code))fail(e);
   }finally{edit.running=undefined;if(valid(captured))update();}
  })();return edit.running;
 }
 async function moreNotes(){
  if(!token||!study||!notesCursor)return;
  const captured=epoch.current,parent=study.id,cursor=notesCursor,requestNavigation=navigation.current,key=JSON.stringify([captured,parent,cursor]);
  if(pendingPages.current.has(key))return;pendingPages.current.add(key);
  const currentPage=()=>valid(captured)&&liveStudy(parent)&&requestNavigation===navigation.current&&selectedStudy.current===parent&&notesPosition.current===cursor;
  try{const result=await api.notes(authorizedToken(),parent,cursor);if(currentPage()){notesPosition.current=result.next_cursor;setNotes(old=>[...old,...result.items.filter(note=>!deleted.current.has(note.id))]);setNotesCursor(result.next_cursor);}}
  catch(e){if(currentPage())fail(e);}finally{pendingPages.current.delete(key);}
 }
 function revealNote(value:NoteValue){
  const layout=workspace.latest.current.read(),refs=noteReferences(value);
  if(!refs.length)return;
  const matches=layout.panes.filter(p=>p.valid&&refs.some(ref=>referencesOverlap(ref,p.ref)));
  if(matches.some(p=>p.paneKey===layout.activePaneKey||Array.from(workspace.root.current?.querySelectorAll<HTMLElement>('[data-reader-pane]')??[]).some(node=>node.dataset.paneKey===p.paneKey&&node.getClientRects().length)))return;
  if(matches.length){workspace.latest.current.activate(matches[0].paneKey);return;}
  const segment=aggregate(value).highlights[0]?.anchor.segments[0],ref=segment?.reference??refs[0];
  const point=segment?.reference.target.kind==='verse_range'?segment.reference.target.start:undefined;
  workspace.latest.current.open(ref,layout.activePaneKey,false,point?{chapter:point.chapter,verse:point.verse,word:segment!.start_position,offset:0}:undefined);
 }
 async function openNote(id:string,parentId=study?.id){
  if(!token||!parentId||!liveStudy(parentId)||deleted.current.has(id))return;
  const currentLane=lanes.current.get(id);
  const reopening=id===current&&parentId===study?.id&&currentLane?.status==='conflict'&&!contexts(currentLane,workspace.workspace.tabKey).length?currentLane:undefined;
  if(id===current&&parentId===study?.id&&!reopening){navigation.current++;setTool('analysis');setAnalysisTab('Notes');const lane=lanes.current.get(id);if(lane)revealNote(lane.value);return;}
  const parent=parentId,origin=selectedStudy.current,requestNavigation=++navigation.current,originLayout=workspace.latest.current.read(),originTool=activeTool.current;
  const fresh=()=>requestNavigation===navigation.current&&selectedStudy.current===origin&&liveStudy(parent)&&!deleted.current.has(id)&&workspace.latest.current.read().tabKey===originLayout.tabKey&&workspace.latest.current.read().revision===originLayout.revision&&activeTool.current===originTool;
  await exit(async()=>{if(!fresh())return;const captured=epoch.current;
   try{
    const selected=parent===study?.id?study:await api.study(authorizedToken(),parent);
    if(!valid(captured)||!fresh()||selected?.owner_account_id!==account)return;
    let lane=lanes.current.get(id);
    // Only explicit last-context consent abandons this definitive conflict.
    if(lane===reopening&&lane?.abandoned&&!contexts(lane,workspace.workspace.tabKey).length){lanes.current.delete(id);lane=undefined;}
    if(!lane){const note=await api.note(authorizedToken(),parent,id);if(!valid(captured)||!fresh()||note.owner_account_id!==account)return;lane={note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false};lanes.current.set(id,lane);}
    await exit(()=>{if(!valid(captured)||!fresh())return;
     if(parent!==origin){collectionNavigation.current++;selectedStudy.current=parent;setStudy(selected);setNotes([lane!.note]);setNotesCursor(null);notesPosition.current=null;workspace.views.get(workspace.workspace.tabKey)?.set('restoredOutline',true);void loadPassages(parent);}
     lane!.abandoned=false;setCurrent(id);setTool('analysis');setAnalysisTab('Notes');setError('');revealNote(lane!.value);
     if(creation.current&&['note.create','note.duplicate','note.conflict_copy'].includes(creation.current.command)&&creationConfirmed.current?.note_id===id)retireCreation(creation.current);update();
    },true,workspace.workspace.tabKey,fresh,undefined,true);
   }catch(e){if(valid(captured)&&fresh())fail(e);}
  },true);
 }
 async function reviewLatest(lane:Lane){
  if(!token||lane.reviewing||lane.status!=='conflict')return;
  const captured=epoch.current;lane.reviewing=true;update();
  try{const latest=await api.note(authorizedToken(),lane.note.study_id,lane.note.id);
   if(valid(captured)&&lanes.current.get(lane.note.id)===lane&&liveStudy(lane.note.study_id)&&!deleted.current.has(lane.note.id)){lane.latest=latest;update();}
  }catch(e){if(valid(captured))fail(e);}finally{lane.reviewing=false;if(valid(captured))update();}
 }
 function useLatest(lane:Lane){
  if(!authority||lanes.current.get(lane.note.id)!==lane||studyBlocked(lane.note.study_id)||deleted.current.has(lane.note.id)||!lane.latest||lane.running||lane.composing||creation.current?.command==='note.conflict_copy')return;
  clearTimeout(lane.timer);const note=lane.latest;
  // Replacing the shared object explicitly resets every mounted editor of this
  // note together. Review alone never mutates the lane or its DOM.
  lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});
  for(const fields of workspace.views.values()){const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.map(item=>item.id===note.id?note:item));}
  workspace.redraw();update();
 }
 function retireForkBranch(original:Attempt,source:Lane|undefined,key:string){
  if(original.command!=='note.conflict_copy'||creation.current!==original||!creationConfirmed.current?.note_id||!source||lanes.current.get(source.note.id)!==source||source.generation!==original.generation||source.running||source.invalid||source.composing||source.deletion||deleted.current.has(source.note.id)||studyBlocked(source.note.study_id)||contexts(source,key).length)return;
  clearTimeout(source.timer);lanes.current.delete(source.note.id);
 }
 async function copyOwn(kind:'note.duplicate'|'note.conflict_copy'|'study.copy',source?:Lane){
  if(!token||!authority||!study||studyBlocked(study.id))return;
  if(creation.current){setError('Recover the original creation before starting another copy.');return;}
  const parent=study.id,captured=epoch.current,originKey=workspace.workspace.tabKey,originNavigation=navigation,requestNavigation=navigation.current,originTool=tool;
  const sourceGeneration=source?.generation;
  const sourceReady=()=>!source||lanes.current.get(source.note.id)===source&&!deleted.current.has(source.note.id)&&!source.deletion&&workspace.views.get(originKey)?.get('current')===source.note.id;
  const fresh=()=>valid(captured)&&!studyBlocked(parent)&&workspace.latest.current.workspace.tabKey===originKey&&originNavigation.current===requestNavigation&&selectedStudy.current===parent;
  const lanesToConfirm=kind==='study.copy'?targetLanes(parent):source?[source]:[];
  setBusy(true);setError('');
  try{
   if(source&&(source.invalid||source.composing||source.deletion||!isReadableNoteValue(source.value)))throw new NotesFailure('copy_input_unresolved');
   if(kind!=='note.conflict_copy'){
    const end=Date.now()+5000;
    for(const lane of lanesToConfirm){
     if(lane.invalid||lane.composing||lane.status==='conflict'||lane.deletion)throw new NotesFailure('copy_input_unresolved');
     await withinStudyPreparation(()=>flush(lane,true),end);
     if(lane.running||lane.attempt||lane.invalid||lane.composing||lane.generation!==lane.saved||lane.status!=='saved')throw new NotesFailure('copy_input_unresolved');
    }
    if(kind==='study.copy'){
     const title=titles.current.get(parent),collection=collections.current.get(parent);
     if(title&&(title.attempt||title.running||title.open)||collection&&(collection.attempt||collection.running||collection.intent)||creation.current)throw new NotesFailure('copy_input_unresolved');
    }
   }else if(!source||source.status!=='conflict'||source.running||source.attempt&&source.status!=='conflict')throw new NotesFailure('copy_input_unresolved');
   if(!fresh()||!sourceReady()||source&&source.generation!==sourceGeneration)return;
   if(creation.current)throw new NotesFailure('copy_input_unresolved');
   if(kind!=='note.conflict_copy'&&lanesToConfirm.some(lane=>lane.running||lane.attempt||lane.invalid||lane.composing||lane.generation!==lane.saved||lane.status!=='saved'))throw new NotesFailure('copy_input_unresolved');
   const operation_id=uuid();
   const payload=kind==='study.copy'?{operation_id,expected_revision:study.revision}:kind==='note.duplicate'?{operation_id,expected_revision:source!.note.revision}:{operation_id,base_revision:source!.note.revision,value:structuredClone(source!.value)};
   if(kind==='note.conflict_copy'&&!noteCommandFits(source!.value,source!.note.revision))throw new NotesFailure('copy_input_unresolved');
   const original:Attempt={operation_id,command:kind,sourceStudy:parent,sourceNote:source?.note.id,path:`/api/studies/${parent}`+(kind==='study.copy'?'/copy':`/notes/${source!.note.id}/${kind==='note.duplicate'?'duplicate':'conflict-copy'}`),method:'POST',payload,generation:source?.generation??0,...(kind==='study.copy'?{}:{study:parent})};
   creation.current=original;
   const inputAtRequest=new Map(targetLanes(parent).map(lane=>[lane,lane.generation])),titleAtRequest=titles.current.get(parent);
   const metadataFresh=()=>fresh()&&workspace.views.get(originKey)?.get('tool')===originTool&&titles.current.get(parent)===titleAtRequest&&!titleAtRequest&&targetLanes(parent).every(lane=>inputAtRequest.get(lane)===lane.generation&&!lane.composing&&!lane.invalid);
   const run=async()=>{
    // A returned session never resumes this command automatically: this function
    // is invoked only by a deliberate copy/recovery click.
    const runEpoch=epoch.current;if(creation.current!==original||identity.current!==account)return;
    const promise=creationConfirmed.current?Promise.resolve(creationConfirmed.current):creationRunning.current??execute(authorizedToken(),original);creationRunning.current=promise;setBusy(true);
    try{const result=creationConfirmed.current??await promise;
     if(!valid(runEpoch)||creation.current!==original)return;
     creationConfirmed.current=result;original.study=result.study_id;update();
     if(!fresh()||!sourceReady()||source&&(source.generation!==sourceGeneration||source.invalid||source.composing)||workspace.views.get(originKey)?.get('tool')!==originTool)return;
     if(result.note_id){
      const note=await api.note(authorizedToken(),result.study_id,result.note_id);
      if(!valid(runEpoch)||!fresh()||!sourceReady()||workspace.views.get(originKey)?.get('tool')!==originTool||creation.current!==original||source&&(source.generation!==sourceGeneration||source.invalid||source.composing))return;
      if(!lanes.current.has(note.id))lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});
      setNotes(old=>[note,...old.filter(item=>item.id!==note.id)]);setCurrent(note.id);setTool('analysis');setAnalysisTab('Notes');
      // This captured branch is acknowledged in its independent destination.
      // Drop only its last unchanged context; never claim the source was saved.
      retireForkBranch(original,source,originKey);
      retireCreation(original);update();
     }else{await openStudy(result.study_id);if(valid(runEpoch)&&selectedStudy.current===result.study_id)retireCreation(original);}
    }catch(e){if(valid(runEpoch)&&creation.current===original){
     if(e instanceof NotesFailure&&['note_revision_conflict','study_revision_conflict','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch','copy_limit_exceeded','note_base_unavailable','note_format_unsupported','highlight_proof_invalid','highlight_proof_unavailable'].includes(e.code))retireCreation(original);
     if(e instanceof NotesFailure&&e.code==='study_revision_conflict'&&metadataFresh()){
      try{const latest=await api.study(authorizedToken(),parent);if(valid(runEpoch)&&metadataFresh())setStudy(old=>old?.id===parent&&BigInt(old.revision)<=BigInt(latest.revision)?latest:old);}
      catch(failure){if(valid(runEpoch)&&failure instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(failure.code))fail(failure);}
     }
     if(e instanceof NotesFailure&&e.code==='note_revision_conflict'&&source){source.status='conflict';source.latest=undefined;}
     setError(e instanceof NotesFailure&&e.code==='note_base_unavailable'?'This note’s original base is unavailable. Your input is kept.':e instanceof NotesFailure&&e.code==='copy_limit_exceeded'?'This study is too large to copy.': creation.current===original?'Copy not confirmed. Your input is kept. Recover the original creation to retry.':'Copy was not saved. Your input is kept. Review the source before trying again.');
     if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);
    }}finally{if(creationRunning.current===promise)creationRunning.current=undefined;if(valid(runEpoch)){setBusy(false);update();}}
   };
   creationOrigin.current={key:originKey,navigation:originNavigation,generation:requestNavigation,tool:originTool,source:kind==='note.conflict_copy'?source:undefined,resume:run};
   await run();
  }catch(e){if(valid(captured)){setError('Copy not started. Confirm or recover all pending writing first. Your input is kept.');if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}}
  finally{if(valid(captured))setBusy(false);}
 }
 async function prepareDeletion(target:Deletion){
  const lane=target.lane,captured=epoch.current;target.status='preparing';target.message='Waiting for the previous save…';update();
  if(lane.running)await Promise.race([lane.running,new Promise<void>(resolve=>setTimeout(resolve,5000))]);
  if(!valid(captured)||lanes.current.get(lane.note.id)!==lane||lane.deletion!==target)return;
  if(lane.running||lane.attempt||lane.status==='conflict'){
   target.status=lane.status==='conflict'?'conflict':'save-recovery';target.message=lane.status==='conflict'?'This note changed. Review the current note before confirming deletion.':'The previous save is not confirmed. Recover that save first.';
  }else {target.status='ready';target.message='';}update();
 }
 function beginDelete(){const lane=current?lanes.current.get(current):undefined;if(!lane||!authority||studyBlocked(lane.note.study_id))return;
  let target=deletions.current.get(lane.note.id);if(!target){target={lane,label:`${study?.title??'Study'} — Note ${++deletionSequence.current}: ${noteDescription(lane.value)}`,open:true,status:'preparing',message:''};lane.deletion=target;deletions.current.set(lane.note.id,target);clearTimeout(lane.timer);void prepareDeletion(target);}target.open=true;setDeleteTarget(lane.note.id);update();
 }
 function closeDelete(){const target=deleteTarget?deletions.current.get(deleteTarget):undefined;if(!target)return;target.open=false;setDeleteTarget(null);
  if(!target.attempt&&target.status!=='executing'){target.lane.deletion=undefined;deletions.current.delete(target.lane.note.id);if(target.lane.status==='pending')schedule(target.lane);}update();
 }
 async function recoverDeleteSave(){const target=deleteTarget?deletions.current.get(deleteTarget):undefined;if(!target||target.status!=='save-recovery')return;
  const lane=target.lane;target.status='preparing';target.message='Recovering the previous save…';update();lane.deletion=undefined;void flush(lane,true);lane.deletion=target;await prepareDeletion(target);
 }
 async function reviewDelete(){const target=deleteTarget?deletions.current.get(deleteTarget):undefined;if(!token||!target||target.status!=='conflict'||target.reviewing)return;
  const captured=epoch.current,lane=target.lane;target.reviewing=true;update();
  const currentReview=()=>valid(captured)&&lanes.current.get(lane.note.id)===lane&&deletions.current.get(lane.note.id)===target&&lane.deletion===target;
  try{const latest=await api.note(authorizedToken(),lane.note.study_id,lane.note.id);if(!currentReview())return;
   target.reviewRevision=latest.revision;target.status='ready';target.review=latest.value;target.message='Current note loaded. Review its saved writing below, then confirm again. Your local writing is kept.';update();
  }catch(e){if(currentReview()){target.message='Current note could not be loaded. Your input is kept.';update();if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}}
  finally{target.reviewing=false;if(currentReview())update();}
 }
 function deletionFocusSource(note:string){
  if(activeTool.current===null)return null;
  const active=document.activeElement,focused=active instanceof HTMLElement&&active!==document.body?active:lastFocused.current;
  const dialog=focused?.closest<HTMLDialogElement>('dialog[data-deleting-note]');
  if(dialog)return dialog.dataset.deletingNote===note?dialog:null;
  // Selection is checked by the caller. A body focus after Back to Studies may
  // replace a hidden editor button; a deliberate surviving public focus does not.
  return focused?.closest<HTMLElement>('[aria-label="Note editor"]')??null;
 }
 function stillReplacingFocus(source:HTMLElement){const active=document.activeElement;return !active||active===document.body||!active.getClientRects().length||source.contains(active);}
 async function confirmDelete(){const target=deleteTarget?deletions.current.get(deleteTarget):undefined;if(!token||!target||!['ready','unknown'].includes(target.status))return;
  const lane=target.lane,captured=epoch.current;if(lane.running||lane.attempt&&lane.status!=='conflict')return;
  // A reviewed deletion never advances the autosave lane's authority. Only this
  // explicit consequential confirmation retires a definitively failed save.
  if(lane.status==='conflict')lane.attempt=undefined;
  if(!target.attempt){const operation_id=uuid();target.attempt={operation_id,command:'note.delete',path:`/api/studies/${lane.note.study_id}/notes/${lane.note.id}`,method:'DELETE',payload:{operation_id,expected_revision:target.reviewRevision??lane.note.revision},study:lane.note.study_id,note:lane.note.id,generation:lane.generation};}
  target.status='executing';target.message='Deleting note…';update();
  try{const pending=execute(authorizedToken(),target.attempt);childDeleteRunning.current.set(lane.note.id,pending);await pending;if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane)return;
   if(selectedNote.current===lane.note.id&&selectedStudy.current===lane.note.study_id){const source=deletionFocusSource(lane.note.id);setDeletionFocus(source?{epoch:captured,navigation:navigation.current,study:lane.note.study_id,source}:null);}
   for(const fields of workspace.views.values()){if(fields.get('current')===lane.note.id)fields.set('current',null);const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.filter(note=>note.id!==lane.note.id));}
   for(const candidate of workspace.remembered?.tabs??[])if(candidate.note===lane.note.id)workspace.forgetRemembered(candidate.tabKey);
   deleted.current.add(lane.note.id);clearTimeout(lane.timer);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);setNotes(old=>old.filter(note=>note.id!==lane.note.id));setCurrent(old=>old===lane.note.id?null:old);setDeleteTarget(old=>old===lane.note.id?null:old);
  }catch(e){if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane)return;const code=e instanceof NotesFailure?e.code:'';
   if(['note_revision_conflict','resource_unavailable','operation_payload_mismatch','scribeswell_personal_notes_input_invalid'].includes(code)){lane.status='conflict';target.status='conflict';target.attempt=undefined;target.reviewRevision=undefined;target.review=undefined;target.message='Deletion not confirmed. Your input is kept. Review the current note before confirming again.';}
   else {target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}
   if(['authentication_required','studies_access_denied'].includes(code)){target.open=false;setDeleteTarget(null);fail(e);}
  }finally{childDeleteRunning.current.delete(lane.note.id);if(valid(captured))update();}
 }
 function studyTargetLive(target:StudyDeletion,captured:number){return valid(captured)&&liveStudy(target.study.id)&&studyDeletions.current.get(target.study.id)===target;}
 function targetLanes(id:string){return [...lanes.current.values()].filter(lane=>lane.note.study_id===id);}
 async function withinStudyPreparation<T>(action:()=>Promise<T>,end:number):Promise<T>{
  if(Date.now()>=end)throw new NotesFailure('request_deadline_exceeded');
  let timer:ReturnType<typeof setTimeout>|undefined;
  try{const result=await Promise.race([action(),new Promise<never>((_,reject)=>{timer=setTimeout(()=>reject(new NotesFailure('request_deadline_exceeded')),Math.max(1,end-Date.now()));})]);if(Date.now()>=end)throw new NotesFailure('request_deadline_exceeded');return result;}
  finally{clearTimeout(timer);}
 }
 function retireCreation(original:Attempt){if(creation.current!==original)return;creationOrigin.current=undefined;creation.current=undefined;creationConfirmed.current=undefined;creationRunning.current=undefined;}
 function materializeCreation(note:NoteView,original:Attempt,captured:number,requestNavigation:number,retire=true){
  if(!valid(captured)||creation.current!==original||!original.study||!liveStudy(original.study)||selectedStudy.current!==original.study||navigation.current!==requestNavigation||note.study_id!==original.study)return false;
  const acknowledged=lanes.current.get(note.id)?.note??note;
  setNotes(old=>{const existing=old.find(item=>item.id===note.id);return existing?old.map(item=>item.id===note.id&&BigInt(item.revision)<=BigInt(acknowledged.revision)?acknowledged:item):[acknowledged,...old];});
  if(retire)retireCreation(original);return true;
 }
 async function prepareStudyDelete(target:StudyDeletion,end=Date.now()+5000,preparation?:number){
  const id=target.study.id,captured=epoch.current,requestNavigation=navigation.current,run=preparation??(target.preparation??0)+1;target.preparation=run;
  const current=()=>studyTargetLive(target,captured)&&target.preparation===run;
  target.status='preparing';target.message='Preparing deletion…';update();
  try{
   const pending=[...targetLanes(id).map(lane=>lane.running),titles.current.get(id)?.running,collections.current.get(id)?.running,...(metadataReads.current.get(id)??[]),...targetLanes(id).map(lane=>childDeleteRunning.current.get(lane.note.id)),...(creation.current?.study===id?[creationRunning.current]:[])].filter(Boolean) as Promise<unknown>[];
   await withinStudyPreparation(()=>Promise.allSettled(pending),end);if(!current())return;
   if(creation.current?.study===id&&creationConfirmed.current){const original=creation.current,outcome=creationConfirmed.current;const note=await withinStudyPreparation(()=>api.note(authorizedToken(),id,outcome.note_id!),end);if(!current())return;if(creation.current===original&&!materializeCreation(note,original,captured,requestNavigation))throw new NotesFailure('operation_unresolved');}
   const title=titles.current.get(id),collection=collections.current.get(id);
   const unknown=targetLanes(id).some(lane=>lane.running||childDeleteRunning.current.has(lane.note.id)||lane.attempt&&lane.status!=='conflict'||lane.deletion?.attempt)||title?.running||title?.attempt&&!title.confirmed||collection?.running||collection?.attempt&&!collection.confirmed||creation.current?.study===id||(metadataReads.current.get(id)?.size??0)>0;
   if(unknown){target.status='recovery';target.message='A previous operation is not confirmed. Recover that original operation first.';update();return;}
   const latest=await withinStudyPreparation(()=>api.study(authorizedToken(),id),end);
   if(!current())return;target.study=latest;target.status='ready';target.message='';
  }catch(e){if(!current())return;target.status='recovery';target.message='Preparation not confirmed. Your input is kept. Recover before confirming.';if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}
  if(current())update();
 }
 function beginStudyDelete(){if(!study||!authority||!liveStudy(study.id))return;
  let target=studyDeletions.current.get(study.id);
  if(!target){target={study:{...study},open:true,status:'preparing',message:''};studyDeletions.current.set(study.id,target);for(const lane of targetLanes(study.id))clearTimeout(lane.timer);void prepareStudyDelete(target);}
  else if(!target.attempt&&target.status==='preparing'&&!target.open)void prepareStudyDelete(target);
  target.open=true;setStudyDeleteTarget(study.id);update();
 }
 function closeStudyDelete(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target)return;
  target.open=false;setStudyDeleteTarget(null);if(!target.attempt){studyDeletions.current.delete(target.study.id);for(const lane of targetLanes(target.study.id))if(lane.status==='pending')schedule(lane);}update();
 }
 async function recoverStudyWrites(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target||!token||target.status!=='recovery')return;
  const id=target.study.id,captured=epoch.current,requestNavigation=navigation.current,end=Date.now()+5000,run=(target.preparation??0)+1;target.preparation=run;
  const current=()=>studyTargetLive(target,captured)&&target.preparation===run;
  async function wait<T>(action:()=>Promise<T>){const value=await withinStudyPreparation(action,end);if(!current())throw new NotesFailure('operation_unresolved');return value;}
  const known=(error:unknown,codes:string[])=>error instanceof NotesFailure&&codes.includes(error.code);
  target.status='preparing';target.message='Recovering previous operations…';update();
  try{
   for(const lane of targetLanes(id)){
    if(lane.running)await wait(()=>lane.running!);
    if(lane.attempt&&lane.status!=='conflict'){const attempt=lane.attempt;let outcome:OperationAck;
     try{outcome=await wait(()=>execute(authorizedToken(),attempt));}
     catch(e){if(!current())return;if(known(e,['note_revision_conflict','note_format_unsupported','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){lane.status='conflict';lane.attempt=undefined;continue;}throw e;}
     lane.note={...lane.note,revision:outcome.revision,value:attempt.payload.value as NoteValue};lane.saved=attempt.generation;lane.attempt=undefined;lane.status=lane.saved===lane.generation?'saved':'pending';
     for(const fields of workspace.views.values()){const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.map(note=>note.id===lane.note.id?lane.note:note));}
    }
    const child=lane.deletion;if(child?.attempt){
     try{await wait(()=>childDeleteRunning.current.get(lane.note.id)??execute(authorizedToken(),child.attempt!));}
     catch(e){if(!current())return;if(known(e,['note_revision_conflict','resource_unavailable','operation_payload_mismatch','scribeswell_personal_notes_input_invalid'])){lane.status='conflict';child.status='conflict';child.attempt=undefined;child.review=undefined;child.reviewRevision=undefined;child.message='Deletion not confirmed. Your input is kept. Review the current note before confirming again.';continue;}throw e;}
     for(const fields of workspace.views.values()){if(fields.get('current')===lane.note.id)fields.set('current',null);const list=fields.get('notes') as NoteView[]|undefined;if(list)fields.set('notes',list.filter(note=>note.id!==lane.note.id));}
   for(const candidate of workspace.remembered?.tabs??[])if(candidate.note===lane.note.id)workspace.forgetRemembered(candidate.tabKey);
   deleted.current.add(lane.note.id);clearTimeout(lane.timer);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);setNotes(old=>old.filter(note=>note.id!==lane.note.id));setCurrent(old=>old===lane.note.id?null:old);setDeleteTarget(old=>old===lane.note.id?null:old);
    }
   }
   const title=titles.current.get(id);if(title?.running)await wait(()=>title.running!);
   if(title?.attempt&&!title.confirmed){try{const outcome=await wait(()=>execute(authorizedToken(),title.attempt!));title.confirmed=outcome;}catch(e){if(!current())return;if(known(e,['study_revision_conflict','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){title.attempt=undefined;title.status='conflict';}else throw e;}}
   const collection=collections.current.get(id);if(collection?.running)await wait(()=>collection.running!);
   if(collection?.attempt&&!collection.confirmed){try{const outcome=await wait(()=>execute(authorizedToken(),collection.attempt!));collection.confirmed=outcome;}catch(e){if(!current())return;if(known(e,['passage_revision_conflict','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){collection.attempt=undefined;collection.status='conflict';}else throw e;}}
   if(creation.current?.study===id){const original=creation.current;
    try{
     const outcome=creationConfirmed.current??await wait(()=>creationRunning.current??execute(authorizedToken(),original));if(!current()||creation.current!==original)return;creationConfirmed.current=outcome;
     const note=await wait(()=>api.note(authorizedToken(),id,outcome.note_id!));
     if(!materializeCreation(note,original,captured,requestNavigation))throw new NotesFailure('operation_unresolved');
    }catch(e){if(!current())return;if(known(e,['resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch']))retireCreation(original);else throw e;}
   }
  }catch(e){if(!current())return;target.status='recovery';target.message='Previous operation not confirmed. Retry its recovery first.';if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);update();return;}
  if(current())await prepareStudyDelete(target,end,run);
 }
 async function reviewStudyDelete(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target||!token||target.status!=='conflict')return;
  const captured=epoch.current;target.status='preparing';update();
  try{const latest=await api.study(authorizedToken(),target.study.id);if(!studyTargetLive(target,captured))return;target.review=latest;target.study=latest;target.status='ready';target.message='Review the current saved title, then explicitly confirm again. Your local input is kept.';}
  catch(e){if(!studyTargetLive(target,captured))return;target.status='conflict';target.message='Current study could not be loaded. Your input is kept.';if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}
  if(studyTargetLive(target,captured))update();
 }
 async function confirmStudyDelete(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target||!token||!['ready','unknown'].includes(target.status))return;
  const id=target.study.id,captured=epoch.current;
  if(!target.attempt){const operation_id=uuid();target.attempt={operation_id,command:'study.delete',path:`/api/studies/${id}`,method:'DELETE',payload:{operation_id,expected_revision:target.study.revision},study:id,generation:0};}
  target.status='executing';target.message='Deleting study…';update();
  try{await execute(authorizedToken(),target.attempt);if(!studyTargetLive(target,captured))return;
   const active=document.activeElement,focused=active instanceof HTMLElement&&active!==document.body?active:lastFocused.current,source=focused?.closest<HTMLElement>('[data-deleting-study]')??null;
   const focus=selectedStudy.current===id&&activeTool.current!==null&&!!source;
   if(source instanceof HTMLDialogElement)source.close();
   const restored=document.activeElement,replacement=restored instanceof HTMLElement?restored.closest<HTMLElement>('[aria-label="Note editor"],[aria-label="My studies"]'):null;
   const focusSource=replacement??source;
   for(const fields of workspace.views.values()){if((fields.get('study') as StudyView|undefined)?.id===id){fields.set('study',null);fields.set('current',null);fields.set('notes',[]);fields.set('tool','studies');}const list=fields.get('studies') as StudyView[]|undefined;if(list)fields.set('studies',list.filter(item=>item.id!==id));}
   for(const candidate of workspace.remembered?.tabs??[])if(candidate.study===id)workspace.forgetRemembered(candidate.tabKey);
   deletedStudies.current.add(id);studyDeletions.current.delete(id);setStudyDeleteTarget(old=>old===id?null:old);
   for(const lane of targetLanes(id)){clearTimeout(lane.timer);deleted.current.add(lane.note.id);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);}
   titles.current.delete(id);titleReads.current.delete(id);metadataReads.current.delete(id);collections.current.delete(id);
   if(creation.current?.study===id){creation.current=undefined;creationConfirmed.current=undefined;creationRunning.current=undefined;}
   setStudies(old=>old.filter(item=>item.id!==id));
   if(selectedStudy.current===id){navigation.current++;collectionNavigation.current++;selectedStudy.current=undefined;notesPosition.current=null;setStudy(null);setNotes([]);setCurrent(null);setNotesCursor(null);setDeleteTarget(null);setBusy(false);setTool('studies');}
   if(focus)setStudyDeletedFocus({captured,source:focusSource!,navigation:navigation.current});
  }catch(e){if(!studyTargetLive(target,captured))return;const code=e instanceof NotesFailure?e.code:'';
   if(['study_revision_conflict','resource_unavailable','operation_payload_mismatch','scribeswell_personal_notes_input_invalid'].includes(code)){target.attempt=undefined;target.status='conflict';target.review=undefined;target.message='Deletion not confirmed. Review the current study before confirming again.';}
   else{target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}
   if(['authentication_required','studies_access_denied'].includes(code)){target.open=false;setStudyDeleteTarget(null);fail(e);}
  }finally{if(valid(captured))update();}
 }
 async function start(){if(!token){setError('Sign in to use My studies.');return false;}const captured=epoch.current;setBusy(true);try{if(import.meta.env.VITE_STUDIES_PREGRANTED==='true'){await api.studies(authorizedToken());}else{enrollment.current??=uuid();await api.enroll(authorizedToken(),enrollment.current);}if(!valid(captured))return false;enrollment.current=undefined;setError('');return true;}catch(e){if(valid(captured))fail(e);return false;}finally{if(valid(captured))setBusy(false);}}
 async function create(title:string|null,details?:{introduction:string|null;source_url:string|null}){
  if(!token)return;if(creation.current&&creationOrigin.current?.key!==workspace.workspace.tabKey){setError('Recover the original creation before starting another study.');return;}if(creation.current&&creation.current.command!=='study.create'){setError('Retry the original note creation before starting another study.');return;}
  if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'study.create',path:'/api/studies',method:'POST',payload:{operation_id,title,...details},generation:0};creationOrigin.current={key:workspace.workspace.tabKey,navigation,generation:navigation.current,tool,resume:()=>create(title,details)};}
  const original=creation.current,captured=epoch.current;setBusy(true);
  const running=creationConfirmed.current?Promise.resolve(creationConfirmed.current):creationRunning.current??execute(authorizedToken(),original);creationRunning.current=running;
  const live=()=>valid(captured)&&creation.current===original;
  try{const result=creationConfirmed.current??await running;if(!live()||!liveStudy(result.study_id))return;creationConfirmed.current=result;original.study=result.study_id;update();
   const origin=creationOrigin.current;
   if(!origin||!workspace.latest.current.tabs.some(tab=>tab.tabKey===origin.key)||origin.navigation.current!==origin.generation||workspace.views.get(origin.key)?.get('tool')!==origin.tool)return;
   origin.generation=origin.navigation.current+1;await openStudy(result.study_id);if(valid(captured)&&creation.current===undefined)creationConfirmed.current=undefined;}
  catch(e){if(live()){if(e instanceof NotesFailure&&['scribeswell_personal_notes_input_invalid','resource_unavailable'].includes(e.code)){creation.current=undefined;creationConfirmed.current=undefined;}fail(e);}}
  finally{if(valid(captured)&&creationRunning.current===running){creationRunning.current=undefined;setBusy(false);update();}}
 }
 async function addNote(initial?:NoteValue){
  if(!token||!study||studyBlocked(study.id))return;const parent=study.id,requestNavigation=navigation.current;
  if(creation.current&&(creationOrigin.current?.key!==workspace.workspace.tabKey||creation.current.command!=='note.create'||creation.current.study!==parent)){setError('Retry the original creation before starting another note.');return;}
  let createdNote:string|undefined;
  await exit(async()=>{
   if(studyBlocked(parent)||selectedStudy.current!==parent||navigation.current!==requestNavigation)return;
   if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'note.create',path:`/api/studies/${parent}/notes`,method:'POST',payload:{operation_id,value:initial??{document:{version:1,blocks:[]},connections:[],highlights:[]}},study:parent,generation:0};creationOrigin.current={key:workspace.workspace.tabKey,navigation,generation:navigation.current,tool,resume:()=>addNote(initial)};}
   const original=creation.current,captured=epoch.current;setBusy(true);
   const running=creationConfirmed.current?Promise.resolve(creationConfirmed.current):creationRunning.current??execute(authorizedToken(),original);creationRunning.current=running;
   const live=()=>valid(captured)&&liveStudy(parent)&&creation.current===original;
   try{const result=creationConfirmed.current??await running;if(!live())return;creationConfirmed.current=result;update();
    // The command is known committed even if this optional follow-up read fails.
    const note=await api.note(authorizedToken(),parent,result.note_id!);const origin=creationOrigin.current;if(!origin||workspace.views.get(origin.key)?.get('tool')!==origin.tool)return;if(!live()||!materializeCreation(note,original,captured,requestNavigation,false))return;
    if(deleted.current.has(note.id)||studyBlocked(parent))return;
    await exit(()=>{if(!valid(captured)||navigation.current!==requestNavigation||selectedStudy.current!==parent)return;if(!lanes.current.has(note.id))lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});setCurrent(note.id);createdNote=note.id;setTool('analysis');setAnalysisTab('Notes');retireCreation(original);update();},true,workspace.workspace.tabKey,()=>navigation.current===requestNavigation&&selectedStudy.current===parent,undefined,true);
   }catch(e){if(live()){if(e instanceof NotesFailure&&['resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'].includes(e.code))retireCreation(original);fail(e);}}
   finally{if(valid(captured)){if(creationRunning.current===running)creationRunning.current=undefined;if((creation.current===original||!creation.current)&&liveStudy(parent)&&selectedStudy.current===parent)setBusy(false);update();}}
  },true);
  return createdNote;
 }
 useEffect(()=>{function unload(e:BeforeUnloadEvent){if([...studyDeletions.current.values()].some(target=>!!target.attempt)||[...lanes.current.values()].some(l=>!!l.deletion?.attempt||l.invalid||l.generation!==l.saved)||[...titles.current.values()].some(edit=>!edit.confirmed&&(edit.attempt||edit.running))||[...collections.current.values()].some(lane=>!lane.confirmed&&(!!lane.attempt||!!lane.running))){e.preventDefault();e.returnValue='';}}window.addEventListener('beforeunload',unload);return()=>window.removeEventListener('beforeunload',unload);},[]);
 const visible=dataAccount.current===account&&authority,libraryGeneration=library.current.generation,libraryEpoch=epoch.current,libraryNavigation=navigation.current;
 const canRestoreLibrary=()=>workspace.latest.current.workspace.tabKey===workspace.workspace.tabKey&&identity.current===account&&epoch.current===libraryEpoch&&library.current.generation===libraryGeneration&&navigation.current===libraryNavigation&&!selectedStudy.current&&!library.current.pending&&library.current.positionLocked;
 const titleEdit=study&&visible?titles.current.get(study.id):undefined;
 const collection=study&&visible?collections.current.get(study.id):undefined;
 const lane=current&&visible?lanes.current.get(current):undefined;
 const liveNotes=new Set(workspace.tabs.map(tab=>workspace.views.get(tab.tabKey)?.get('current')));
 const editorLanes=visible?[...lanes.current.values()].filter(item=>!item.abandoned&&(liveNotes.has(item.note.id)||item.generation!==item.saved||item.composing||item.invalid)):[];
 async function openCreated(){const original=creation.current,outcome=creationConfirmed.current;if(!original||!outcome)return;
  if(outcome.note_id&&study?.id===outcome.study_id){
   if(original.command==='note.conflict_copy'){
    const captured=epoch.current,key=workspace.workspace.tabKey,nav=navigation.current,shown=current,shownTool=tool,source=creationOrigin.current?.source;
    try{
     // Re-authorize and validate the known destination before retiring any input.
     const note=await api.note(authorizedToken(),outcome.study_id,outcome.note_id);
     if(!valid(captured)||creation.current!==original||creationConfirmed.current!==outcome||workspace.latest.current.workspace.tabKey!==key||navigation.current!==nav||selectedStudy.current!==outcome.study_id||selectedNote.current!==shown||activeTool.current!==shownTool||studyBlocked(outcome.study_id)||deleted.current.has(note.id))return;
     if(!lanes.current.has(note.id))lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});
     retireForkBranch(original,source,key);
    }catch(e){if(valid(captured))fail(e);return;}
   }
   await openNote(outcome.note_id);if(workspace.views.get(workspace.workspace.tabKey)?.get('current')===outcome.note_id)retireCreation(original);
  }
  else await openStudy(outcome.study_id);
  update();
 }
 function exitAccount(action:()=>void|Promise<void>){
  const captured=epoch.current,approved=new Map<Lane,{generation:number;composing:boolean;invalid:boolean}>();
  const next=():Promise<void>=>{
   if(!valid(captured))return Promise.resolve();
   const pending=[...lanes.current.values()].find(lane=>{
    if(lane.abandoned||!lane.composing&&!lane.invalid&&lane.generation===lane.saved)return false;
    const consent=approved.get(lane);return !consent||consent.generation!==lane.generation||consent.composing!==lane.composing||consent.invalid!==lane.invalid;
   });
   if(!pending)return Promise.resolve(action()).then(()=>{});
   return exit(()=>{approved.set(pending,{generation:pending.generation,composing:pending.composing,invalid:pending.invalid});return next();},false,workspace.workspace.tabKey,()=>true,pending);
  };
  return next();
 }
 return {pendingStudyCreation:visible&&creation.current?.command==='study.create'&&creationOrigin.current?.key===workspace.workspace.tabKey,privateReadFailure:(failure:unknown)=>{if(valid(libraryEpoch))fail(failure,true);},changeDetails,beginDetails:()=>beginRename(true),detailsEdit:titleEdit?.open&&titleEdit.details?titleEdit:undefined,reviewLatest,useLatest,duplicateNote:(bound?:Lane)=>copyOwn('note.duplicate',bound??lane),saveMine:(bound?:Lane)=>copyOwn('note.conflict_copy',bound??lane),copyStudy:()=>copyOwn('study.copy'),pendingSaves:visible?[...lanes.current.values()].filter(item=>item.abandoned&&item.attempt&&item.status!=='conflict'):[],recoverSave:(lane:Lane)=>flush(lane,true),creationRecovery:visible&&!!creation.current,creationKnown:visible&&!!creationConfirmed.current,creationLabel:creationConfirmed.current?.note_id&&study?.id===creationConfirmed.current.study_id?'Open created note':'Open created study',recoverCreation:()=>creationOrigin.current?.resume(),openCreated,editorLanes,studyDeletedFocus:visible&&studyDeletedFocus&&valid(studyDeletedFocus.captured)&&navigation.current===studyDeletedFocus.navigation&&!selectedStudy.current&&activeTool.current!==null&&(stillReplacingFocus(studyDeletedFocus.source)||document.activeElement?.hasAttribute('data-study-deleted-focus'))?studyDeletedFocus:null,studyDeletion:visible&&studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined,studyDeletionPaused:!!study&&studyBlocked(study.id),studyWritesFrozen:!!study&&!!studyDeletions.current.get(study.id)?.attempt,pendingStudyDeletions:visible?[...studyDeletions.current.values()].filter(target=>!!target.attempt&&!target.open):[],beginStudyDelete,closeStudyDelete,confirmStudyDelete,recoverStudyWrites,reviewStudyDelete,openStudyDeletion:(target:StudyDeletion)=>{if(!visible||studyDeletions.current.get(target.study.id)!==target)return;target.open=true;setStudyDeleteTarget(target.study.id);update();},deletionFocus:visible?deletionFocus:null,canFocusDeletion:()=>!!deletionFocus&&activeTool.current!==null&&stillReplacingFocus(deletionFocus.source)&&valid(deletionFocus.epoch)&&authority&&dataAccount.current===account&&selectedNote.current===null&&selectedStudy.current===deletionFocus.study&&navigation.current===deletionFocus.navigation,pendingDeletions:visible?[...deletions.current.values()].filter(target=>!!target.attempt&&!target.open):[],openDeletion:(target:Deletion)=>{if(!visible||deletions.current.get(target.lane.note.id)!==target)return;target.open=true;setDeleteTarget(target.lane.note.id);update();},deletion:visible&&deleteTarget?deletions.current.get(deleteTarget):undefined,beginDelete,closeDelete,confirmDelete,recoverDeleteSave,reviewDelete,accountKey:account??'anonymous',enabled:import.meta.env.VITE_STUDIES_ENABLED==='true',tool,setTool,analysisTab,setAnalysisTab,invalidInput:(bound?:Lane)=>{const target=bound??lane;if(target&&!target.deletion?.attempt){target.invalid=true;target.status='failed';clearTimeout(target.timer);update();}},studies:visible&&libraryVerified?studies:[],study:visible?study:null,notes:visible?notes:[],current:visible?current:null,lane,error,accountError,busy,searchCandidate:visible?searchCandidate:'',searchMasked:!visible,setSearchCandidate:changeSearchCandidate,searchStudies,clearSearch,libraryBusy,libraryError,libraryInputInvalid,libraryVerified:visible&&libraryVerified,libraryRestore,libraryPosition:library.current.position,canRestoreLibrary,finishLibraryRestore:()=>{if(canRestoreLibrary())library.current.positionLocked=false;},rememberLibrary,studyCursor:visible?studyCursor:null,notesCursor,collection,collect,removePassage,retryPassages,reviewPassages,cancelPassageIntent,titleEdit: titleEdit?.open&&!titleEdit.details?titleEdit:undefined,beginRename,changeTitle,cancelRename,saveTitle,reloadTitle,loadStudies,moreNotes,openStudies,openStudy,openNote,start,create,addNote,change,mark,composition,retry:(bound?:Lane)=>(bound??lane)&&flush((bound??lane)!,true),exit:exitAccount,exitPrompt,stay:()=>{setExitPrompt(null);workspace.cancelRestore();if(workspace.devicePending)workspace.cancelDevice();},proceed:async()=>{const prompt=exitPrompt;setExitPrompt(null);if(!prompt||!prompt.fresh())return;
 if(prompt.discard&&!contexts(prompt.discard,prompt.key).length){
  abandonLane(prompt.discard);
 }
 await prompt.action();},leave:()=>{const requestNavigation=++navigation.current;return exit(()=>{if(requestNavigation!==navigation.current)return;collectionNavigation.current++;selectedStudy.current=undefined;notesPosition.current=null;setStudy(null);setCurrent(null);setNotes([]);setTool('studies');void loadStudies();},true);}};
}
type Studies=ReturnType<typeof useStatefulStudies>;
const Context=createContext<Studies|null>(null);
function ExitDialog({studies}:{studies:Studies}){
 const dialog=useRef<HTMLDialogElement>(null),trigger=useRef(document.activeElement as HTMLElement|null);
 useEffect(()=>{dialog.current?.showModal();return()=>{dialog.current?.close();if(trigger.current?.isConnected)trigger.current.focus();};},[]);
 return <dialog ref={dialog} aria-label="Changes not saved" className="rounded-xl p-6 backdrop:bg-black/40" onCancel={e=>{e.preventDefault();studies.stay();}}><p>Changes not saved</p><button className="m-2 underline" autoFocus onClick={studies.stay}>Stay</button><button className="m-2 underline" onClick={()=>void studies.proceed()}>{studies.exitPrompt?.switching?'Switch anyway':'Close anyway'}</button></dialog>;
}
type SavedParagraph=Extract<NoteValue['document']['blocks'][number],{type:'paragraph'}>;
function noteDescription(value:NoteValue){return Array.from(value.document.blocks.flatMap(block=>block.type==='paragraph'?[block]:block.items.flat()).map(paragraph=>paragraph.content.map(inline=>inline.type==='text'?inline.text:inline.type==='passage_link'?inline.label:inline.content.map(text=>text.text).join('')).join('')).join(' ').trim()).slice(0,60).join('')||'Empty note';}
function SavedParagraphView({paragraph}:{paragraph:SavedParagraph}){
 function textNode(text:Extract<SavedParagraph['content'][number],{type:'text'}>){let node:ReactNode=text.text;for(const mark of [...text.marks].reverse())node=mark==='bold'?<strong>{node}</strong>:<em>{node}</em>;return node;}
 return <p dir={paragraph.direction}>{paragraph.content.map((inline,index)=><span key={index}>{inline.type==='text'?textNode(inline):inline.type==='passage_link'?<>{inline.label} <span>(passage: {referenceLabel(inline.reference)})</span></>:<>{inline.content.map((text,i)=><span key={i}>{textNode(text)}</span>)} <span>(link: {inline.url})</span></>}</span>)}</p>;
}
export function SavedNoteReview({value}:{value:NoteValue}){return <section aria-label="Current saved note" className="whitespace-pre-wrap [overflow-wrap:anywhere] [&_ol]:list-decimal [&_ul]:list-disc [&_li]:ml-5"><h3>Current saved writing</h3>{value.document.blocks.length?value.document.blocks.map((block,index)=>block.type==='paragraph'?<SavedParagraphView key={index} paragraph={block}/>:block.style==='ordered'?<ol key={index}>{block.items.map((item,i)=><li key={i}>{item.map((paragraph,j)=><SavedParagraphView key={j} paragraph={paragraph}/>)}</li>)}</ol>:<ul key={index}>{block.items.map((item,i)=><li key={i}>{item.map((paragraph,j)=><SavedParagraphView key={j} paragraph={paragraph}/>)}</li>)}</ul>):<p>Empty note</p>}</section>;}
function DeletionFocus({studies}:{studies:Studies}){
 const fallback=useRef<HTMLParagraphElement>(null);
 useLayoutEffect(()=>{if(!studies.canFocusDeletion())return;const empty=document.querySelector<HTMLElement>('[data-note-empty-state]');if(empty?.getClientRects().length&&!empty.closest('[hidden]'))empty.focus();else fallback.current?.focus();},[studies.deletionFocus]);
 return studies.canFocusDeletion()?<p ref={fallback} role="status" tabIndex={-1}>Note deleted.</p>:null;
}
function DeleteDialog({studies}:{studies:Studies}){
 const dialog=useRef<HTMLDialogElement>(null),trigger=useRef(document.activeElement as HTMLElement|null);const target=studies.deletion!;
 useEffect(()=>{dialog.current?.showModal();return()=>{dialog.current?.close();if(trigger.current?.isConnected)trigger.current.focus();};},[]);
 return <dialog ref={dialog} data-deleting-note={target.lane.note.id} aria-label="Delete this note?" className="rounded-xl p-6 max-w-sm backdrop:bg-black/40" onCancel={e=>{e.preventDefault();studies.closeDelete();}}><h2>Delete this note?</h2><p dir="auto">{target.label}</p><p>Its writing and highlights will be permanently removed. This cannot be undone. Other notes remain. Unsent writing in this note will be discarded if deletion succeeds.</p>{target.message&&<p role="status">{target.message}</p>}{target.review&&<SavedNoteReview value={target.review}/>}<button autoFocus className="underline m-2" onClick={studies.closeDelete}>{target.attempt?'Close':'Cancel'}</button>{target.status==='conflict'?<button disabled={target.reviewing} className="underline m-2" onClick={()=>void studies.reviewDelete()}>Review current note</button>:target.status==='save-recovery'?<button className="underline m-2" onClick={()=>void studies.recoverDeleteSave()}>Recover previous save</button>:<button className="underline m-2" disabled={!['ready','unknown'].includes(target.status)} onClick={()=>void studies.confirmDelete()}>{target.status==='unknown'?'Retry deletion':'Delete note'}</button>}</dialog>;
}
function StudyDeleteDialog({studies}:{studies:Studies}){
 const dialog=useRef<HTMLDialogElement>(null),trigger=useRef(document.activeElement as HTMLElement|null),target=studies.studyDeletion!;
 useEffect(()=>{dialog.current?.showModal();return()=>{dialog.current?.close();if(trigger.current?.isConnected&&trigger.current.getClientRects().length)trigger.current.focus();};},[]);
 return <dialog ref={dialog} data-deleting-study={target.study.id} aria-label="Delete this study?" className="rounded-xl p-6 max-w-sm [overflow-wrap:anywhere] backdrop:bg-black/40" onCancel={event=>{event.preventDefault();studies.closeStudyDelete();}}><h2>Delete this study?</h2><p dir="auto">{target.study.title}</p><p>All its notes, highlights and collected passages will be permanently removed. This cannot be undone. Unsent writing and title input in this study will be discarded only if deletion succeeds.</p>{target.review&&<p dir="auto">Current saved title: {target.review.title}</p>}{target.message&&<p role="status">{target.message}</p>}<button autoFocus className="underline m-2" onClick={studies.closeStudyDelete}>{target.attempt?'Close':'Cancel'}</button>{target.status==='conflict'?<button className="underline m-2" onClick={()=>void studies.reviewStudyDelete()}>Review current study</button>:target.status==='recovery'?<button className="underline m-2" onClick={()=>void studies.recoverStudyWrites()}>Recover previous operations</button>:<button className="underline m-2" disabled={!['ready','unknown'].includes(target.status)} onClick={()=>void studies.confirmStudyDelete()}>{target.status==='unknown'?'Retry study deletion':'Delete study'}</button>}</dialog>;
}
function StudyDeletedFocus({studies}:{studies:Studies}){const fallback=useRef<HTMLParagraphElement>(null);useLayoutEffect(()=>{if(studies.studyDeletedFocus)fallback.current?.focus();},[studies.studyDeletedFocus]);return studies.studyDeletedFocus?<p ref={fallback} data-study-deleted-focus role="status" tabIndex={-1}>Study deleted.</p>:null;}
export function StudiesProvider({children}:{children:ReactNode}){const value=useStatefulStudies();return <Context.Provider value={value}>{children}{value.pendingSaves.map((lane,index)=><button key={lane.note.id} className="underline m-2" disabled={!!lane.running} onClick={()=>void value.recoverSave(lane)}>Recover note save {index+1}</button>)}{value.creationRecovery&&<button className="underline m-2" onClick={()=>void (value.creationKnown?value.openCreated():value.recoverCreation())}>{value.creationKnown?value.creationLabel:'Recover original creation'}</button>}{value.studyDeletedFocus&&<StudyDeletedFocus studies={value}/>} {value.studyDeletion?.open&&<StudyDeleteDialog studies={value}/>} {value.pendingStudyDeletions.map(target=><button key={target.study.id} className="underline m-2" onClick={()=>value.openStudyDeletion(target)}>Recover study deletion: {target.study.title}</button>)}{value.deletionFocus&&<DeletionFocus studies={value}/>} {value.exitPrompt&&<ExitDialog studies={value}/>} {value.deletion?.open&&<DeleteDialog studies={value}/>} {value.pendingDeletions.map(target=><button key={target.lane.note.id} className="underline m-2" onClick={()=>value.openDeletion(target)}>Recover deletion: {target.label}</button>)}</Context.Provider>;}
export function useStudies(){const value=useContext(Context);if(!value)throw Error('StudiesProvider required');return value;}
