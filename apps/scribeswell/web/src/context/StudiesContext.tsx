/** One in-memory account/note save lane, independent of mounted tool/editor views. */
import {createContext,useContext,useEffect,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {useAuth} from './AuthContext';
import {api,execute,NotesFailure,uuid,type NoteValue,type NoteView,type StudyView,type OperationAck,type Attempt,type PassageList} from '@/lib/personal-notes';
import {referenceKey,referenceLabel,validateReference,type PassageReference} from '@/lib/passage-references';
type PassageIntent={kind:'add';reference:PassageReference}|{kind:'remove';id:string;reference:PassageReference};
type CollectionLane={study:string;list?:PassageList;intent?:PassageIntent;attempt?:Attempt;confirmed?:OperationAck;running?:Promise<void>;status:'loading'|'ready'|'saving'|'failed'|'conflict'|'reviewed';message:string;read:number};
export type Lane={note:NoteView;value:NoteValue;generation:number;saved:number;status:'saved'|'pending'|'saving'|'failed'|'conflict';attempt?:Attempt;running?:Promise<void>;timer?:ReturnType<typeof setTimeout>;first?:number;composing:boolean;invalid:boolean;formatUnsupported?:boolean;deletion?:Deletion};
type Deletion={lane:Lane;label:string;open:boolean;reviewing?:boolean;status:'preparing'|'ready'|'save-recovery'|'executing'|'unknown'|'conflict';message:string;review?:NoteValue;reviewRevision?:string;attempt?:Attempt};
type StudyDeletion={preparation?:number;study:StudyView;open:boolean;status:'preparing'|'ready'|'recovery'|'executing'|'unknown'|'conflict';message:string;attempt?:Attempt;review?:StudyView;running?:Promise<void>};
type TitleEdit={study:string;candidate:string;base:string;open:boolean;status:'editing'|'saving'|'failed'|'conflict';message:string;confirmed?:OperationAck;attempt?:Attempt;running?:Promise<void>};
type Tool='studies'|'analysis'|null;
function useStatefulStudies(){
 const {session}=useAuth();const account=session?.user.id,token=session?.access_token;
 const identity=useRef(account);identity.current=account;
 const dataAccount=useRef(account);const [authority,setAuthority]=useState(true);
 const epoch=useRef(0);const previous=useRef(account);
 if(previous.current!==account){previous.current=account;epoch.current++;}
 const [analysisTab,setAnalysisTab]=useState<'Word'|'Occurrences'|'Notes'>('Notes');
 const [tool,setTool]=useState<Tool>(null),[studies,setStudies]=useState<StudyView[]>([]),[study,setStudy]=useState<StudyView|null>(null),[notes,setNotes]=useState<NoteView[]>([]),[current,setCurrent]=useState<string|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const [studyCursor,setStudyCursor]=useState<string|null>(null),[notesCursor,setNotesCursor]=useState<string|null>(null);
 const [searchCandidate,setSearchCandidate]=useState(''),[libraryBusy,setLibraryBusy]=useState(false),[libraryError,setLibraryError]=useState(''),[libraryInputInvalid,setLibraryInputInvalid]=useState(false),[libraryVerified,setLibraryVerified]=useState(false),[libraryRestore,setLibraryRestore]=useState(0);
 // Passive scroll events from a collapsed list must not replace its saved return anchor.
 const library=useRef({query:'',generation:0,depth:1,cursor:null as string|null,pending:false,positionLocked:false,position:{scroll:0,focus:''}});
 const lanes=useRef(new Map<string,Lane>()),[,render]=useState(0);const update=()=>render(x=>x+1);
 const [exitPrompt,setExitPrompt]=useState<{action:()=>void|Promise<void>;switching:boolean;discard?:Lane}|null>(null);
 const collectionNavigation=useRef(0);
 const navigation=useRef(0),selectedStudy=useRef<string|undefined>(undefined),notesPosition=useRef<string|null>(null),pendingPages=useRef(new Set<string>());
 selectedStudy.current=study?.id;
 const titles=useRef(new Map<string,TitleEdit>()),titleReads=useRef(new Map<string,number>());
 const activeTool=useRef(tool);activeTool.current=tool;const lastFocused=useRef<HTMLElement|null>(null);
 useEffect(()=>{const remember=(event:FocusEvent)=>{if(event.target instanceof HTMLElement&&event.target!==document.body)lastFocused.current=event.target;};document.addEventListener('focusin',remember);return()=>document.removeEventListener('focusin',remember);},[]);
 const selectedNote=useRef(current);selectedNote.current=current;const deletionSequence=useRef(0);
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
 const creation=useRef<Attempt|undefined>(undefined);const enrollment=useRef<string|undefined>(undefined);
 useEffect(()=>{for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;childDeleteRunning.current.clear();setStudyDeletedFocus(null);deletedStudies.current.clear();studyDeletions.current.clear();setStudyDeleteTarget(null);creationRunning.current=undefined;creationConfirmed.current=undefined;metadataReads.current.clear();setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();navigation.current++;pendingPages.current.clear();notesPosition.current=null;creation.current=undefined;enrollment.current=undefined;setStudies([]);setStudy(null);setNotes([]);setCurrent(null);setError('');setBusy(false);setExitPrompt(null);setStudyCursor(null);setNotesCursor(null);dataAccount.current=account;setAuthority(true);library.current={query:'',generation:library.current.generation+1,depth:1,cursor:null,pending:false,positionLocked:false,position:{scroll:0,focus:''}};setSearchCandidate('');setLibraryError('');setLibraryInputInvalid(false);setLibraryBusy(false);setLibraryVerified(false);},[account]);
 function valid(captured:number){return epoch.current===captured&&identity.current===account;}
 function fail(failure:unknown){
  const code=failure instanceof NotesFailure?failure.code:'studies_storage_unavailable';
  if(code==='authentication_required'){setStudyDeleteTarget(null);for(const target of studyDeletions.current.values()){target.open=false;if(target.status==='executing'){target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}}setDeleteTarget(null);for(const target of deletions.current.values()){target.open=false;if(target.status==='executing'){target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}}epoch.current++;library.current.pending=false;setLibraryBusy(false);setLibraryVerified(false);setAuthority(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);}
  if(code==='studies_access_denied'){
   epoch.current++;library.current.generation++;library.current.query='';library.current.depth=1;library.current.cursor=null;library.current.position={scroll:0,focus:''};library.current.positionLocked=false;setSearchCandidate('');setLibraryVerified(false);setLibraryBusy(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;childDeleteRunning.current.clear();setStudyDeletedFocus(null);deletedStudies.current.clear();studyDeletions.current.clear();setStudyDeleteTarget(null);creationRunning.current=undefined;creationConfirmed.current=undefined;metadataReads.current.clear();setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();setStudies([]);setNotes([]);setStudy(null);setCurrent(null);creation.current=undefined;enrollment.current=undefined;
  }
  setBusy(false);setError(code==='studies_access_denied'?'Studies access is unavailable for this account.':code==='authentication_required'?'Sign in to use My studies.':'Studies could not be loaded. Try again.');
 }
 async function loadStudies(more=false,query=library.current.query,changed=false){
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
    const result=await api.search(token,query,cursor??undefined);
    if(!currentRead())return;
    items.push(...result.items);cursor=result.next_cursor;pages++;
   }while(cursor&&pages<depth);
   if(!currentRead())return;
   setAuthority(true);setLibraryVerified(true);setError('');
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
 async function flush(lane:Lane,retry=false):Promise<void>{
  if(lane.running)return lane.running;
  if(lane.deletion||studyBlocked(lane.note.study_id))return;
  if(!token||lane.invalid||lane.composing||lane.generation===lane.saved||lane.status==='conflict'||(lane.status==='failed'&&!retry))return;
  clearTimeout(lane.timer);lane.first=undefined;
  const captured=epoch.current;
  if(!lane.attempt){const operation_id=uuid();lane.attempt={operation_id,command:'note.replace',path:`/api/studies/${lane.note.study_id}/notes/${lane.note.id}`,method:'PUT',payload:{operation_id,expected_revision:lane.note.revision,value:structuredClone(lane.value)},study:lane.note.study_id,note:lane.note.id,generation:lane.generation};}
  const attempt=lane.attempt;lane.status='saving';update();
  lane.running=(async()=>{
   try{const result=await execute(token,attempt);if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane||deleted.current.has(lane.note.id))return;lane.note={...lane.note,revision:result.revision,value:attempt.payload.value as NoteValue};lane.saved=attempt.generation;setNotes(old=>old.map(note=>note.id===lane.note.id?lane.note:note));lane.attempt=undefined;lane.status=lane.saved===lane.generation?'saved':'pending';}
   catch(e){if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane)return;const code=e instanceof NotesFailure?e.code:'';lane.status=['note_revision_conflict','note_format_unsupported','operation_payload_mismatch','resource_unavailable'].includes(code)?'conflict':'failed';if(code==='note_format_unsupported')lane.formatUnsupported=true;if(code==='scribeswell_personal_notes_input_invalid')lane.attempt=undefined;if(['authentication_required','studies_access_denied'].includes(code))fail(e);}
   finally{lane.running=undefined;if(valid(captured)&&liveStudy(lane.note.study_id)&&lanes.current.get(lane.note.id)===lane){update();if(lane.status==='pending'&&!lane.deletion)schedule(lane);}}
  })();return lane.running;
 }
 function schedule(lane:Lane){clearTimeout(lane.timer);if(studyBlocked(lane.note.study_id)||lane.deletion||lane.composing||lane.running||lane.status==='failed'||lane.status==='conflict')return;const now=Date.now();lane.first??=now;lane.timer=setTimeout(()=>void flush(lane),Math.min(500,Math.max(0,2000-(now-lane.first))));}
 function change(value:NoteValue){const lane=current?lanes.current.get(current):undefined;if(!lane||lane.deletion?.attempt||studyDeletions.current.get(lane.note.study_id)?.attempt)return;lane.value=value;lane.invalid=false;lane.generation++;if(lane.status!=='failed'&&lane.status!=='conflict')lane.status='pending';update();schedule(lane);}
 function composition(active:boolean){const lane=current?lanes.current.get(current):undefined;if(lane){lane.composing=active;if(active)clearTimeout(lane.timer);else schedule(lane);update();}}
 async function exit(action:()=>void|Promise<void>,switching=false){const captured=epoch.current;const lane=current?lanes.current.get(current):undefined;if(lane&&!lane.deletion&&!studyBlocked(lane.note.study_id)){const end=Date.now()+5000;while(lane.generation!==lane.saved&&!lane.invalid&&!lane.composing&&lane.status!=='failed'&&lane.status!=='conflict'&&Date.now()<end){await Promise.race([flush(lane),new Promise<void>(resolve=>setTimeout(resolve,Math.max(1,end-Date.now())))]);if(!valid(captured))return;}if(!valid(captured))return;if(lane.composing||lane.invalid||lane.generation!==lane.saved){setExitPrompt({action,switching,discard:switching&&lane.status==='conflict'?lane:undefined});return;}}await action();}
 async function openStudy(id:string){
  if(!token||!liveStudy(id))return;const requestLibrary=++library.current.generation;library.current.pending=false;setLibraryBusy(false);const requestNavigation=++navigation.current;
  await exit(async()=>{if(requestNavigation!==navigation.current||requestLibrary!==library.current.generation)return;collectionNavigation.current++;const captured=epoch.current;setBusy(true);
   try{const [selected,page]=await Promise.all([api.study(token,id),api.notes(token,id)]);
    if(valid(captured)&&liveStudy(id)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation){library.current.positionLocked=true;selectedStudy.current=selected.id;notesPosition.current=page.next_cursor;setStudy(selected);if(creation.current?.command==='study.create'&&creation.current.study===selected.id)creation.current=undefined;setNotes(page.items.filter(note=>!deleted.current.has(note.id)));setNotesCursor(page.next_cursor);setCurrent(null);setTool('studies');setError('');void loadPassages(selected.id);}
   }catch(e){if(valid(captured)&&liveStudy(id)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation)fail(e);}finally{if(valid(captured)&&requestNavigation===navigation.current)setBusy(false);}
  },true);
 }
 // Collection authority/revisions/recovery are independent of notes and metadata.
 function collectionLane(id:string){let lane=collections.current.get(id);if(!lane){lane={study:id,status:'loading',message:'',read:0};collections.current.set(id,lane);}return lane;}
 async function refreshPassages(lane:CollectionLane,captured:number,currentRead=()=>true){
  if(!token)return;const read=++lane.read;const latest=await api.passages(token,lane.study);
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
   try{if(!lane.confirmed){lane.confirmed=await execute(token,attempt);if(!valid(captured)||!liveStudy(lane.study)||collections.current.get(lane.study)!==lane)return;}
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
  const latest=await api.study(token,id);
  if(!valid(captured)||!liveStudy(id))return;
  setStudies(old=>old.map(item=>item.id===id&&BigInt(item.revision)<=BigInt(latest.revision)?latest:item));
  if(selectedStudy.current===id)setStudy(old=>old?.id!==id||BigInt(old.revision)>BigInt(latest.revision)?old:latest);
  return latest;
 }
 function refreshTitle(id:string,captured:number){
  const reads=metadataReads.current.get(id)??new Set<Promise<StudyView|undefined>>();metadataReads.current.set(id,reads);
  const promise=readTitle(id,captured);reads.add(promise);void promise.then(()=>reads.delete(promise),()=>reads.delete(promise));return promise;
 }
 async function beginRename(){
  if(!token||!study||busy||studyBlocked(study.id))return;
  const id=study.id,existing=titles.current.get(id);
  if(existing?.attempt||existing?.running){existing.open=true;update();return;}
  const captured=epoch.current,requestNavigation=navigation.current,read=(titleReads.current.get(id)??0)+1;titleReads.current.set(id,read);setBusy(true);
  try{const latest=await refreshTitle(id,captured);
   if(!latest||!valid(captured)||requestNavigation!==navigation.current||selectedStudy.current!==id||titleReads.current.get(id)!==read)return;
   titles.current.set(id,{study:id,candidate:latest.title,base:latest.revision,open:true,status:'editing',message:''});update();
  }catch(e){if(valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===id&&titleReads.current.get(id)===read)fail(e);}
  finally{if(valid(captured)&&(requestNavigation===navigation.current||selectedStudy.current===id)&&titleReads.current.get(id)===read)setBusy(false);}
 }
 function changeTitle(candidate:string){const edit=study?titles.current.get(study.id):undefined;if(!edit||studyBlocked(edit.study)||edit.attempt||edit.running)return;edit.candidate=candidate;edit.message='';update();}
 function cancelRename(){if(study)titleReads.current.set(study.id,(titleReads.current.get(study.id)??0)+1);const edit=study?titles.current.get(study.id):undefined;if(!edit)return;if(edit.attempt||edit.running)edit.open=false;else titles.current.delete(edit.study);update();}
 async function reloadTitle(){
  if(!study||!token)return;const edit=titles.current.get(study.id);if(!edit||edit.running)return;
  const captured=epoch.current,requestNavigation=navigation.current,read=(titleReads.current.get(edit.study)??0)+1;titleReads.current.set(edit.study,read);
  const currentRead=()=>valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===edit.study&&titles.current.get(edit.study)===edit&&titleReads.current.get(edit.study)===read&&!edit.attempt&&!edit.running;
  try{const latest=await refreshTitle(edit.study,captured);if(!latest||!currentRead())return;
   edit.base=latest.revision;edit.status='editing';edit.message='Current title: '+latest.title+'. Your entered title is kept. Select Save to rename.';update();
  }catch(e){if(currentRead()){edit.message='Current title could not be loaded. Retry loading it.';update();if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}}
 }
 async function saveTitle(){
  if(!token||!study)return;const edit=titles.current.get(study.id);if(!edit||studyBlocked(edit.study)||edit.running||edit.status==='conflict')return;
  const captured=epoch.current;
  if(!edit.attempt){const operation_id=uuid();edit.attempt={operation_id,command:'study.rename',path:`/api/studies/${edit.study}/title`,method:'PUT',payload:{operation_id,expected_revision:edit.base,title:edit.candidate},study:edit.study,generation:0};}
  const attempt=edit.attempt;edit.status='saving';edit.message=edit.confirmed?'Title saved. Refreshing current title…':'Saving title…';update();
  edit.running=(async()=>{
   try{if(!edit.confirmed){const outcome=await execute(token,attempt);if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;edit.confirmed=outcome;}
    if(!valid(captured))return;
    // A receipt may describe an older rename; only a current read supplies the heading.
    await refreshTitle(edit.study,captured);if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;
    titles.current.delete(edit.study);
   }catch(e){if(!valid(captured)||!liveStudy(edit.study)||titles.current.get(edit.study)!==edit)return;const code=e instanceof NotesFailure?e.code:'';
    if(edit.confirmed){edit.status='failed';edit.message='Title saved. Current title could not be refreshed. Retry loading it.';}
    else if(code==='study_revision_conflict'){edit.status='conflict';edit.attempt=undefined;edit.message='This study title changed elsewhere. Load current title before saving.';}
    else if(code==='scribeswell_personal_notes_input_invalid'){edit.status='editing';edit.attempt=undefined;edit.message='Enter a title of 1–200 characters without control characters.';}
    else {edit.status='failed';edit.message='Title not saved. Retry the original rename.';}
    if(['authentication_required','studies_access_denied'].includes(code))fail(e);
   }finally{edit.running=undefined;if(valid(captured))update();}
  })();return edit.running;
 }
 async function moreNotes(){
  if(!token||!study||!notesCursor)return;
  const captured=epoch.current,parent=study.id,cursor=notesCursor,requestNavigation=navigation.current,key=JSON.stringify([captured,parent,cursor]);
  if(pendingPages.current.has(key))return;pendingPages.current.add(key);
  const currentPage=()=>valid(captured)&&liveStudy(parent)&&requestNavigation===navigation.current&&selectedStudy.current===parent&&notesPosition.current===cursor;
  try{const result=await api.notes(token,parent,cursor);if(currentPage()){notesPosition.current=result.next_cursor;setNotes(old=>[...old,...result.items.filter(note=>!deleted.current.has(note.id))]);setNotesCursor(result.next_cursor);}}
  catch(e){if(currentPage())fail(e);}finally{pendingPages.current.delete(key);}
 }
 async function openNote(id:string){
  if(!token||!study||!liveStudy(study.id)||deleted.current.has(id))return;const parent=study.id,requestNavigation=++navigation.current;
  await exit(async()=>{if(requestNavigation!==navigation.current||selectedStudy.current!==parent)return;const captured=epoch.current;
   try{let lane=lanes.current.get(id);if(!lane){const note=await api.note(token,parent,id);if(!valid(captured)||requestNavigation!==navigation.current||selectedStudy.current!==parent||!liveStudy(parent)||deleted.current.has(id))return;lane={note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false};lanes.current.set(id,lane);}setCurrent(id);setTool('analysis');setAnalysisTab('Notes');setError('');update();}
   catch(e){if(valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===parent&&liveStudy(parent))fail(e);}
  },true);
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
  try{const latest=await api.note(token,lane.note.study_id,lane.note.id);if(!currentReview())return;
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
  try{const pending=execute(token,target.attempt);childDeleteRunning.current.set(lane.note.id,pending);await pending;if(!valid(captured)||!liveStudy(lane.note.study_id)||lanes.current.get(lane.note.id)!==lane)return;
   if(selectedNote.current===lane.note.id&&selectedStudy.current===lane.note.study_id){const source=deletionFocusSource(lane.note.id);setDeletionFocus(source?{epoch:captured,navigation:navigation.current,study:lane.note.study_id,source}:null);}
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
 function retireCreation(original:Attempt){if(creation.current!==original)return;creation.current=undefined;creationConfirmed.current=undefined;creationRunning.current=undefined;}
 function materializeCreation(note:NoteView,original:Attempt,captured:number,requestNavigation:number){
  if(!valid(captured)||creation.current!==original||!original.study||!liveStudy(original.study)||selectedStudy.current!==original.study||navigation.current!==requestNavigation||note.study_id!==original.study)return false;
  const acknowledged=lanes.current.get(note.id)?.note??note;
  setNotes(old=>{const existing=old.find(item=>item.id===note.id);return existing?old.map(item=>item.id===note.id&&BigInt(item.revision)<=BigInt(acknowledged.revision)?acknowledged:item):[acknowledged,...old];});
  retireCreation(original);return true;
 }
 async function prepareStudyDelete(target:StudyDeletion,end=Date.now()+5000,preparation?:number){
  const id=target.study.id,captured=epoch.current,requestNavigation=navigation.current,run=preparation??(target.preparation??0)+1;target.preparation=run;
  const current=()=>studyTargetLive(target,captured)&&target.preparation===run;
  target.status='preparing';target.message='Preparing deletion…';update();
  try{
   const pending=[...targetLanes(id).map(lane=>lane.running),titles.current.get(id)?.running,collections.current.get(id)?.running,...(metadataReads.current.get(id)??[]),...targetLanes(id).map(lane=>childDeleteRunning.current.get(lane.note.id)),...(creation.current?.study===id?[creationRunning.current]:[])].filter(Boolean) as Promise<unknown>[];
   await withinStudyPreparation(()=>Promise.allSettled(pending),end);if(!current())return;
   if(creation.current?.study===id&&creationConfirmed.current){const original=creation.current,outcome=creationConfirmed.current;const note=await withinStudyPreparation(()=>api.note(token!,id,outcome.note_id!),end);if(!current())return;if(creation.current===original&&!materializeCreation(note,original,captured,requestNavigation))throw new NotesFailure('operation_unresolved');}
   const title=titles.current.get(id),collection=collections.current.get(id);
   const unknown=targetLanes(id).some(lane=>lane.running||childDeleteRunning.current.has(lane.note.id)||lane.attempt&&lane.status!=='conflict'||lane.deletion?.attempt)||title?.running||title?.attempt&&!title.confirmed||collection?.running||collection?.attempt&&!collection.confirmed||creation.current?.study===id||(metadataReads.current.get(id)?.size??0)>0;
   if(unknown){target.status='recovery';target.message='A previous operation is not confirmed. Recover that original operation first.';update();return;}
   const latest=await withinStudyPreparation(()=>api.study(token!,id),end);
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
     try{outcome=await wait(()=>execute(token,attempt));}
     catch(e){if(!current())return;if(known(e,['note_revision_conflict','note_format_unsupported','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){lane.status='conflict';lane.attempt=undefined;continue;}throw e;}
     lane.note={...lane.note,revision:outcome.revision,value:attempt.payload.value as NoteValue};lane.saved=attempt.generation;lane.attempt=undefined;lane.status=lane.saved===lane.generation?'saved':'pending';
     setNotes(old=>old.map(note=>note.id===lane.note.id?lane.note:note));
    }
    const child=lane.deletion;if(child?.attempt){
     try{await wait(()=>childDeleteRunning.current.get(lane.note.id)??execute(token,child.attempt!));}
     catch(e){if(!current())return;if(known(e,['note_revision_conflict','resource_unavailable','operation_payload_mismatch','scribeswell_personal_notes_input_invalid'])){lane.status='conflict';child.status='conflict';child.attempt=undefined;child.review=undefined;child.reviewRevision=undefined;child.message='Deletion not confirmed. Your input is kept. Review the current note before confirming again.';continue;}throw e;}
     deleted.current.add(lane.note.id);clearTimeout(lane.timer);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);setNotes(old=>old.filter(note=>note.id!==lane.note.id));setCurrent(old=>old===lane.note.id?null:old);setDeleteTarget(old=>old===lane.note.id?null:old);
    }
   }
   const title=titles.current.get(id);if(title?.running)await wait(()=>title.running!);
   if(title?.attempt&&!title.confirmed){try{const outcome=await wait(()=>execute(token,title.attempt!));title.confirmed=outcome;}catch(e){if(!current())return;if(known(e,['study_revision_conflict','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){title.attempt=undefined;title.status='conflict';}else throw e;}}
   const collection=collections.current.get(id);if(collection?.running)await wait(()=>collection.running!);
   if(collection?.attempt&&!collection.confirmed){try{const outcome=await wait(()=>execute(token,collection.attempt!));collection.confirmed=outcome;}catch(e){if(!current())return;if(known(e,['passage_revision_conflict','resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'])){collection.attempt=undefined;collection.status='conflict';}else throw e;}}
   if(creation.current?.study===id){const original=creation.current;
    try{
     const outcome=creationConfirmed.current??await wait(()=>creationRunning.current??execute(token,original));if(!current()||creation.current!==original)return;creationConfirmed.current=outcome;
     const note=await wait(()=>api.note(token,id,outcome.note_id!));
     if(!materializeCreation(note,original,captured,requestNavigation))throw new NotesFailure('operation_unresolved');
    }catch(e){if(!current())return;if(known(e,['resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch']))retireCreation(original);else throw e;}
   }
  }catch(e){if(!current())return;target.status='recovery';target.message='Previous operation not confirmed. Retry its recovery first.';if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);update();return;}
  if(current())await prepareStudyDelete(target,end,run);
 }
 async function reviewStudyDelete(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target||!token||target.status!=='conflict')return;
  const captured=epoch.current;target.status='preparing';update();
  try{const latest=await api.study(token,target.study.id);if(!studyTargetLive(target,captured))return;target.review=latest;target.study=latest;target.status='ready';target.message='Review the current saved title, then explicitly confirm again. Your local input is kept.';}
  catch(e){if(!studyTargetLive(target,captured))return;target.status='conflict';target.message='Current study could not be loaded. Your input is kept.';if(e instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(e.code))fail(e);}
  if(studyTargetLive(target,captured))update();
 }
 async function confirmStudyDelete(){const target=studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined;if(!target||!token||!['ready','unknown'].includes(target.status))return;
  const id=target.study.id,captured=epoch.current;
  if(!target.attempt){const operation_id=uuid();target.attempt={operation_id,command:'study.delete',path:`/api/studies/${id}`,method:'DELETE',payload:{operation_id,expected_revision:target.study.revision},study:id,generation:0};}
  target.status='executing';target.message='Deleting study…';update();
  try{await execute(token,target.attempt);if(!studyTargetLive(target,captured))return;
   const active=document.activeElement,focused=active instanceof HTMLElement&&active!==document.body?active:lastFocused.current,source=focused?.closest<HTMLElement>('[data-deleting-study]')??null;
   const focus=selectedStudy.current===id&&activeTool.current!==null&&!!source;
   if(source instanceof HTMLDialogElement)source.close();
   const restored=document.activeElement,replacement=restored instanceof HTMLElement?restored.closest<HTMLElement>('[aria-label="Note editor"],[aria-label="My studies"]'):null;
   const focusSource=replacement??source;
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
 async function start(){if(!token){setError('Sign in to use My studies.');return false;}const captured=epoch.current;setBusy(true);try{enrollment.current??=uuid();await api.enroll(token,enrollment.current);if(!valid(captured))return false;enrollment.current=undefined;setError('');return true;}catch(e){if(valid(captured))fail(e);return false;}finally{if(valid(captured))setBusy(false);}}
 async function create(title:string|null){
  if(!token)return;if(creation.current&&creation.current.command!=='study.create'){setError('Retry the original note creation before starting another study.');return;}
  if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'study.create',path:'/api/studies',method:'POST',payload:{operation_id,title},generation:0};}
  const original=creation.current,captured=epoch.current;setBusy(true);
  const running=creationConfirmed.current?Promise.resolve(creationConfirmed.current):creationRunning.current??execute(token,original);creationRunning.current=running;
  const live=()=>valid(captured)&&creation.current===original;
  try{const result=creationConfirmed.current??await running;if(!live()||!liveStudy(result.study_id))return;creationConfirmed.current=result;original.study=result.study_id;await openStudy(result.study_id);if(valid(captured)&&creation.current===undefined)creationConfirmed.current=undefined;}
  catch(e){if(live()){if(e instanceof NotesFailure&&['scribeswell_personal_notes_input_invalid','resource_unavailable'].includes(e.code)){creation.current=undefined;creationConfirmed.current=undefined;}fail(e);}}
  finally{if(valid(captured)&&creationRunning.current===running){creationRunning.current=undefined;setBusy(false);}}
 }
 async function addNote(){
  if(!token||!study||studyBlocked(study.id))return;const parent=study.id,requestNavigation=navigation.current;
  if(creation.current&&(creation.current.command!=='note.create'||creation.current.study!==parent)){setError('Retry the original creation before starting another note.');return;}
  await exit(async()=>{
   if(studyBlocked(parent)||selectedStudy.current!==parent||navigation.current!==requestNavigation)return;
   if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'note.create',path:`/api/studies/${parent}/notes`,method:'POST',payload:{operation_id,value:{document:{version:1,blocks:[]},connections:[],highlights:[]}},study:parent,generation:0};}
   const original=creation.current,captured=epoch.current;setBusy(true);
   const running=creationConfirmed.current?Promise.resolve(creationConfirmed.current):creationRunning.current??execute(token,original);creationRunning.current=running;
   const live=()=>valid(captured)&&liveStudy(parent)&&creation.current===original;
   try{const result=creationConfirmed.current??await running;if(!live())return;creationConfirmed.current=result;
    // The command is known committed even if this optional follow-up read fails.
    const note=await api.note(token,parent,result.note_id!);if(!live()||!materializeCreation(note,original,captured,requestNavigation))return;
    if(deleted.current.has(note.id)||studyBlocked(parent))return;
    lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});setCurrent(note.id);setTool('analysis');setAnalysisTab('Notes');update();
   }catch(e){if(live()){if(e instanceof NotesFailure&&['resource_unavailable','scribeswell_personal_notes_input_invalid','operation_payload_mismatch'].includes(e.code))retireCreation(original);fail(e);}}
   finally{if(valid(captured)){if(creationRunning.current===running)creationRunning.current=undefined;if((creation.current===original||!creation.current)&&liveStudy(parent)&&selectedStudy.current===parent)setBusy(false);}}
  },true);
 }
 useEffect(()=>{function unload(e:BeforeUnloadEvent){if([...studyDeletions.current.values()].some(target=>!!target.attempt)||[...lanes.current.values()].some(l=>!!l.deletion?.attempt||l.invalid||l.generation!==l.saved)||[...titles.current.values()].some(edit=>!edit.confirmed&&(edit.attempt||edit.running))||[...collections.current.values()].some(lane=>!lane.confirmed&&(!!lane.attempt||!!lane.running))){e.preventDefault();e.returnValue='';}}window.addEventListener('beforeunload',unload);return()=>window.removeEventListener('beforeunload',unload);},[]);
 const visible=dataAccount.current===account&&authority,libraryGeneration=library.current.generation,libraryEpoch=epoch.current,libraryNavigation=navigation.current;
 const canRestoreLibrary=()=>identity.current===account&&epoch.current===libraryEpoch&&library.current.generation===libraryGeneration&&navigation.current===libraryNavigation&&!selectedStudy.current&&!library.current.pending&&library.current.positionLocked;
 const titleEdit=study&&visible?titles.current.get(study.id):undefined;
 const collection=study&&visible?collections.current.get(study.id):undefined;
 const lane=current&&visible?lanes.current.get(current):undefined;
 return {studyDeletedFocus:visible&&studyDeletedFocus&&valid(studyDeletedFocus.captured)&&navigation.current===studyDeletedFocus.navigation&&!selectedStudy.current&&activeTool.current!==null&&(stillReplacingFocus(studyDeletedFocus.source)||document.activeElement?.hasAttribute('data-study-deleted-focus'))?studyDeletedFocus:null,studyDeletion:visible&&studyDeleteTarget?studyDeletions.current.get(studyDeleteTarget):undefined,studyDeletionPaused:!!study&&studyBlocked(study.id),studyWritesFrozen:!!study&&!!studyDeletions.current.get(study.id)?.attempt,pendingStudyDeletions:visible?[...studyDeletions.current.values()].filter(target=>!!target.attempt&&!target.open):[],beginStudyDelete,closeStudyDelete,confirmStudyDelete,recoverStudyWrites,reviewStudyDelete,openStudyDeletion:(target:StudyDeletion)=>{if(!visible||studyDeletions.current.get(target.study.id)!==target)return;target.open=true;setStudyDeleteTarget(target.study.id);update();},deletionFocus:visible?deletionFocus:null,canFocusDeletion:()=>!!deletionFocus&&activeTool.current!==null&&stillReplacingFocus(deletionFocus.source)&&valid(deletionFocus.epoch)&&authority&&dataAccount.current===account&&selectedNote.current===null&&selectedStudy.current===deletionFocus.study&&navigation.current===deletionFocus.navigation,pendingDeletions:visible?[...deletions.current.values()].filter(target=>!!target.attempt&&!target.open):[],openDeletion:(target:Deletion)=>{if(!visible||deletions.current.get(target.lane.note.id)!==target)return;target.open=true;setDeleteTarget(target.lane.note.id);update();},deletion:visible&&deleteTarget?deletions.current.get(deleteTarget):undefined,beginDelete,closeDelete,confirmDelete,recoverDeleteSave,reviewDelete,accountKey:account??'anonymous',enabled:import.meta.env.VITE_STUDIES_ENABLED==='true',tool,setTool,analysisTab,setAnalysisTab,invalidInput:()=>{if(lane&&!lane.deletion?.attempt){lane.invalid=true;lane.status='failed';clearTimeout(lane.timer);update();}},studies:visible&&libraryVerified?studies:[],study:visible?study:null,notes:visible?notes:[],current:visible?current:null,lane,error,busy,searchCandidate:visible?searchCandidate:'',searchMasked:!visible,setSearchCandidate:changeSearchCandidate,searchStudies,clearSearch,libraryBusy,libraryError,libraryInputInvalid,libraryVerified:visible&&libraryVerified,libraryRestore,libraryPosition:library.current.position,canRestoreLibrary,finishLibraryRestore:()=>{if(canRestoreLibrary())library.current.positionLocked=false;},rememberLibrary,studyCursor:visible?studyCursor:null,notesCursor,collection,collect,removePassage,retryPassages,reviewPassages,cancelPassageIntent,titleEdit: titleEdit?.open?titleEdit:undefined,beginRename,changeTitle,cancelRename,saveTitle,reloadTitle,loadStudies,moreNotes,openStudies,openStudy,openNote,start,create,addNote,change,composition,retry:()=>lane&&flush(lane,true),exit,exitPrompt,stay:()=>setExitPrompt(null),proceed:async()=>{const prompt=exitPrompt;setExitPrompt(null);if(prompt){if(prompt.discard&&lanes.current.get(prompt.discard.note.id)===prompt.discard){clearTimeout(prompt.discard.timer);lanes.current.delete(prompt.discard.note.id);setCurrent(null);}await prompt.action();}},leave:()=>{const requestNavigation=++navigation.current;return exit(()=>{if(requestNavigation!==navigation.current)return;collectionNavigation.current++;selectedStudy.current=undefined;notesPosition.current=null;setStudy(null);setCurrent(null);setNotes([]);setTool('studies');void loadStudies();},true);}};
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
function SavedNoteReview({value}:{value:NoteValue}){return <section aria-label="Current saved note" className="whitespace-pre-wrap [overflow-wrap:anywhere] [&_ol]:list-decimal [&_ul]:list-disc [&_li]:ml-5"><h3>Current saved writing</h3>{value.document.blocks.length?value.document.blocks.map((block,index)=>block.type==='paragraph'?<SavedParagraphView key={index} paragraph={block}/>:block.style==='ordered'?<ol key={index}>{block.items.map((item,i)=><li key={i}>{item.map((paragraph,j)=><SavedParagraphView key={j} paragraph={paragraph}/>)}</li>)}</ol>:<ul key={index}>{block.items.map((item,i)=><li key={i}>{item.map((paragraph,j)=><SavedParagraphView key={j} paragraph={paragraph}/>)}</li>)}</ul>):<p>Empty note</p>}</section>;}
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
export function StudiesProvider({children}:{children:ReactNode}){const value=useStatefulStudies();return <Context.Provider value={value}>{children}{value.studyDeletedFocus&&<StudyDeletedFocus studies={value}/>} {value.studyDeletion?.open&&<StudyDeleteDialog studies={value}/>} {value.pendingStudyDeletions.map(target=><button key={target.study.id} className="underline m-2" onClick={()=>value.openStudyDeletion(target)}>Recover study deletion: {target.study.title}</button>)}{value.deletionFocus&&<DeletionFocus studies={value}/>} {value.exitPrompt&&<ExitDialog studies={value}/>} {value.deletion?.open&&<DeleteDialog studies={value}/>} {value.pendingDeletions.map(target=><button key={target.lane.note.id} className="underline m-2" onClick={()=>value.openDeletion(target)}>Recover deletion: {target.label}</button>)}</Context.Provider>;}
export function useStudies(){const value=useContext(Context);if(!value)throw Error('StudiesProvider required');return value;}
