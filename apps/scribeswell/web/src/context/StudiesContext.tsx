/** One in-memory account/note save lane, independent of mounted tool/editor views. */
import {createContext,useContext,useEffect,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {useAuth} from './AuthContext';
import {api,execute,NotesFailure,uuid,type NoteValue,type NoteView,type StudyView,type OperationAck,type Attempt,type PassageList} from '@/lib/personal-notes';
import {referenceKey,referenceLabel,validateReference,type PassageReference} from '@/lib/passage-references';
type PassageIntent={kind:'add';reference:PassageReference}|{kind:'remove';id:string;reference:PassageReference};
type CollectionLane={study:string;list?:PassageList;intent?:PassageIntent;attempt?:Attempt;confirmed?:OperationAck;running?:Promise<void>;status:'loading'|'ready'|'saving'|'failed'|'conflict'|'reviewed';message:string;read:number};
export type Lane={note:NoteView;value:NoteValue;generation:number;saved:number;status:'saved'|'pending'|'saving'|'failed'|'conflict';attempt?:Attempt;running?:Promise<void>;timer?:ReturnType<typeof setTimeout>;first?:number;composing:boolean;invalid:boolean;formatUnsupported?:boolean;deletion?:Deletion};
type Deletion={lane:Lane;label:string;open:boolean;reviewing?:boolean;status:'preparing'|'ready'|'save-recovery'|'executing'|'unknown'|'conflict';message:string;review?:NoteValue;reviewRevision?:string;attempt?:Attempt};
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
 const collections=useRef(new Map<string,CollectionLane>());
 const creation=useRef<Attempt|undefined>(undefined);const enrollment=useRef<string|undefined>(undefined);
 useEffect(()=>{for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();navigation.current++;pendingPages.current.clear();notesPosition.current=null;creation.current=undefined;enrollment.current=undefined;setStudies([]);setStudy(null);setNotes([]);setCurrent(null);setError('');setBusy(false);setExitPrompt(null);setStudyCursor(null);setNotesCursor(null);dataAccount.current=account;setAuthority(true);library.current={query:'',generation:library.current.generation+1,depth:1,cursor:null,pending:false,positionLocked:false,position:{scroll:0,focus:''}};setSearchCandidate('');setLibraryError('');setLibraryInputInvalid(false);setLibraryBusy(false);setLibraryVerified(false);},[account]);
 function valid(captured:number){return epoch.current===captured&&identity.current===account;}
 function fail(failure:unknown){
  const code=failure instanceof NotesFailure?failure.code:'studies_storage_unavailable';
  if(code==='authentication_required'){setDeleteTarget(null);for(const target of deletions.current.values()){target.open=false;if(target.status==='executing'){target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}}epoch.current++;library.current.pending=false;setLibraryBusy(false);setLibraryVerified(false);setAuthority(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);}
  if(code==='studies_access_denied'){
   epoch.current++;library.current.generation++;library.current.query='';library.current.depth=1;library.current.cursor=null;library.current.position={scroll:0,focus:''};library.current.positionLocked=false;setSearchCandidate('');setLibraryVerified(false);setLibraryBusy(false);for(const lane of lanes.current.values())clearTimeout(lane.timer);lanes.current.clear();deleted.current.clear();deletions.current.clear();deletionSequence.current=0;setDeletionFocus(null);setDeleteTarget(null);titles.current.clear();titleReads.current.clear();collections.current.clear();setStudies([]);setNotes([]);setStudy(null);setCurrent(null);creation.current=undefined;enrollment.current=undefined;
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
   setStudies(old=>{const existing=new Map(old.map(item=>[item.id,item])),unique=new Map<string,StudyView>();for(const item of more?[...old,...items]:items){const known=existing.get(item.id);unique.set(item.id,known&&BigInt(known.revision)>BigInt(item.revision)?known:item);}return [...unique.values()];});
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
  if(lane.deletion)return;
  if(!token||lane.invalid||lane.composing||lane.generation===lane.saved||lane.status==='conflict'||(lane.status==='failed'&&!retry))return;
  clearTimeout(lane.timer);lane.first=undefined;
  const captured=epoch.current;
  if(!lane.attempt){const operation_id=uuid();lane.attempt={operation_id,command:'note.replace',path:`/api/studies/${lane.note.study_id}/notes/${lane.note.id}`,method:'PUT',payload:{operation_id,expected_revision:lane.note.revision,value:structuredClone(lane.value)},study:lane.note.study_id,note:lane.note.id,generation:lane.generation};}
  const attempt=lane.attempt;lane.status='saving';update();
  lane.running=(async()=>{
   try{const result=await execute(token,attempt);if(!valid(captured)||lanes.current.get(lane.note.id)!==lane||deleted.current.has(lane.note.id))return;lane.note={...lane.note,revision:result.revision,value:attempt.payload.value as NoteValue};lane.saved=attempt.generation;setNotes(old=>old.map(note=>note.id===lane.note.id?lane.note:note));lane.attempt=undefined;lane.status=lane.saved===lane.generation?'saved':'pending';}
   catch(e){if(!valid(captured))return;const code=e instanceof NotesFailure?e.code:'';lane.status=['note_revision_conflict','note_format_unsupported','operation_payload_mismatch','resource_unavailable'].includes(code)?'conflict':'failed';if(code==='note_format_unsupported')lane.formatUnsupported=true;if(code==='scribeswell_personal_notes_input_invalid')lane.attempt=undefined;if(['authentication_required','studies_access_denied'].includes(code))fail(e);}
   finally{lane.running=undefined;if(valid(captured)){update();if(lane.status==='pending'&&!lane.deletion)schedule(lane);}}
  })();return lane.running;
 }
 function schedule(lane:Lane){clearTimeout(lane.timer);if(lane.deletion||lane.composing||lane.running||lane.status==='failed'||lane.status==='conflict')return;const now=Date.now();lane.first??=now;lane.timer=setTimeout(()=>void flush(lane),Math.min(500,Math.max(0,2000-(now-lane.first))));}
 function change(value:NoteValue){const lane=current?lanes.current.get(current):undefined;if(!lane||lane.deletion?.attempt)return;lane.value=value;lane.invalid=false;lane.generation++;if(lane.status!=='failed'&&lane.status!=='conflict')lane.status='pending';update();schedule(lane);}
 function composition(active:boolean){const lane=current?lanes.current.get(current):undefined;if(lane){lane.composing=active;if(active)clearTimeout(lane.timer);else schedule(lane);update();}}
 async function exit(action:()=>void|Promise<void>,switching=false){const captured=epoch.current;const lane=current?lanes.current.get(current):undefined;if(lane&&!lane.deletion){const end=Date.now()+5000;while(lane.generation!==lane.saved&&!lane.invalid&&!lane.composing&&lane.status!=='failed'&&lane.status!=='conflict'&&Date.now()<end){await Promise.race([flush(lane),new Promise<void>(resolve=>setTimeout(resolve,Math.max(1,end-Date.now())))]);if(!valid(captured))return;}if(!valid(captured))return;if(lane.composing||lane.invalid||lane.generation!==lane.saved){setExitPrompt({action,switching,discard:switching&&lane.status==='conflict'?lane:undefined});return;}}await action();}
 async function openStudy(id:string){
  if(!token)return;const requestLibrary=++library.current.generation;library.current.pending=false;setLibraryBusy(false);const requestNavigation=++navigation.current;
  await exit(async()=>{if(requestNavigation!==navigation.current||requestLibrary!==library.current.generation)return;collectionNavigation.current++;const captured=epoch.current;setBusy(true);
   try{const [selected,page]=await Promise.all([api.study(token,id),api.notes(token,id)]);
    if(valid(captured)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation){library.current.positionLocked=true;selectedStudy.current=selected.id;notesPosition.current=page.next_cursor;setStudy(selected);if(creation.current?.command==='study.create'&&creation.current.study===selected.id)creation.current=undefined;setNotes(page.items.filter(note=>!deleted.current.has(note.id)));setNotesCursor(page.next_cursor);setCurrent(null);setTool('studies');setError('');void loadPassages(selected.id);}
   }catch(e){if(valid(captured)&&requestNavigation===navigation.current&&requestLibrary===library.current.generation)fail(e);}finally{if(valid(captured)&&requestNavigation===navigation.current)setBusy(false);}
  },true);
 }
 // Collection authority/revisions/recovery are independent of notes and metadata.
 function collectionLane(id:string){let lane=collections.current.get(id);if(!lane){lane={study:id,status:'loading',message:'',read:0};collections.current.set(id,lane);}return lane;}
 async function refreshPassages(lane:CollectionLane,captured:number,currentRead=()=>true){
  if(!token)return;const read=++lane.read;const latest=await api.passages(token,lane.study);
  if(!valid(captured)||collections.current.get(lane.study)!==lane||read!==lane.read||!currentRead())return;
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
  if(!token||lane.running||lane.status==='conflict')return;
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
   try{if(!lane.confirmed){lane.confirmed=await execute(token,attempt);if(!valid(captured))return;}
    await refreshPassages(lane,captured);if(!valid(captured))return;
    lane.attempt=undefined;lane.confirmed=undefined;lane.intent=undefined;lane.status='ready';lane.message='';
   }catch(e){if(!valid(captured))return;const code=e instanceof NotesFailure?e.code:'';
    if(lane.confirmed){lane.status='failed';lane.message='Passages saved. Current list could not be refreshed. Retry loading it.';}
    else if(code==='passage_revision_conflict'){lane.status='conflict';lane.attempt=undefined;lane.message='Passages changed elsewhere. Load and review current passages before trying your change.';}
    else if(code==='scribeswell_personal_notes_input_invalid'){lane.status='ready';lane.attempt=undefined;lane.message='This passage could not be added. Check the reference.';}
    else{lane.status='failed';lane.message='Passages not saved. Retry the original change.';}
    if(selectedStudy.current===lane.study&&navigation.current===requestNavigation&&['authentication_required','studies_access_denied'].includes(code))fail(e);
   }finally{lane.running=undefined;if(valid(captured))update();}
  })();return lane.running;
 }
 async function collect(reference:PassageReference){if(!study)return false;const lane=collectionLane(study.id);if(lane.attempt||lane.running||!lane.list||['conflict','reviewed'].includes(lane.status))return false;lane.intent={kind:'add',reference};await savePassages(lane);return !['This passage could not be added. Check the reference.','Already in this study'].includes(lane.message);}
 function removePassage(id:string){if(!study)return;const lane=collectionLane(study.id);if(lane.attempt||lane.running||!lane.list||['conflict','reviewed'].includes(lane.status))return;const item=lane.list.items.find(item=>item.id===id);if(!item)return;lane.intent={kind:'remove',id,reference:item.reference};void savePassages(lane);}
 function retryPassages(){if(!study)return;const lane=collectionLane(study.id);if(lane.attempt||lane.intent&&lane.status==='reviewed')void savePassages(lane);else void loadPassages(study.id);}
 function reviewPassages(){if(study)void loadPassages(study.id);}
 function cancelPassageIntent(){const lane=study?collections.current.get(study.id):undefined;if(lane&&!lane.attempt&&!lane.running){lane.intent=undefined;lane.status='ready';lane.message='';update();}}
 // Metadata has its own operation lane and never flushes/replaces a note buffer.
 async function refreshTitle(id:string,captured:number){
  if(!token)return;
  const latest=await api.study(token,id);
  if(!valid(captured))return;
  setStudies(old=>old.map(item=>item.id===id&&BigInt(item.revision)<=BigInt(latest.revision)?latest:item));
  if(selectedStudy.current===id)setStudy(old=>old?.id===id&&BigInt(old.revision)>BigInt(latest.revision)?old:latest);
  return latest;
 }
 async function beginRename(){
  if(!token||!study||busy)return;
  const id=study.id,existing=titles.current.get(id);
  if(existing?.attempt||existing?.running){existing.open=true;update();return;}
  const captured=epoch.current,requestNavigation=navigation.current,read=(titleReads.current.get(id)??0)+1;titleReads.current.set(id,read);setBusy(true);
  try{const latest=await refreshTitle(id,captured);
   if(!latest||!valid(captured)||requestNavigation!==navigation.current||selectedStudy.current!==id||titleReads.current.get(id)!==read)return;
   titles.current.set(id,{study:id,candidate:latest.title,base:latest.revision,open:true,status:'editing',message:''});update();
  }catch(e){if(valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===id&&titleReads.current.get(id)===read)fail(e);}
  finally{if(valid(captured)&&(requestNavigation===navigation.current||selectedStudy.current===id)&&titleReads.current.get(id)===read)setBusy(false);}
 }
 function changeTitle(candidate:string){const edit=study?titles.current.get(study.id):undefined;if(!edit||edit.attempt||edit.running)return;edit.candidate=candidate;edit.message='';update();}
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
  if(!token||!study)return;const edit=titles.current.get(study.id);if(!edit||edit.running||edit.status==='conflict')return;
  const captured=epoch.current;
  if(!edit.attempt){const operation_id=uuid();edit.attempt={operation_id,command:'study.rename',path:`/api/studies/${edit.study}/title`,method:'PUT',payload:{operation_id,expected_revision:edit.base,title:edit.candidate},study:edit.study,generation:0};}
  const attempt=edit.attempt;edit.status='saving';edit.message=edit.confirmed?'Title saved. Refreshing current title…':'Saving title…';update();
  edit.running=(async()=>{
   try{if(!edit.confirmed){const outcome=await execute(token,attempt);if(!valid(captured))return;edit.confirmed=outcome;}
    if(!valid(captured))return;
    // A receipt may describe an older rename; only a current read supplies the heading.
    await refreshTitle(edit.study,captured);if(!valid(captured))return;
    titles.current.delete(edit.study);
   }catch(e){if(!valid(captured))return;const code=e instanceof NotesFailure?e.code:'';
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
  const currentPage=()=>valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===parent&&notesPosition.current===cursor;
  try{const result=await api.notes(token,parent,cursor);if(currentPage()){notesPosition.current=result.next_cursor;setNotes(old=>[...old,...result.items.filter(note=>!deleted.current.has(note.id))]);setNotesCursor(result.next_cursor);}}
  catch(e){if(currentPage())fail(e);}finally{pendingPages.current.delete(key);}
 }
 async function openNote(id:string){
  if(!token||!study||deleted.current.has(id))return;const parent=study.id,requestNavigation=++navigation.current;
  await exit(async()=>{if(requestNavigation!==navigation.current||selectedStudy.current!==parent)return;const captured=epoch.current;
   try{let lane=lanes.current.get(id);if(!lane){const note=await api.note(token,parent,id);if(!valid(captured)||requestNavigation!==navigation.current||selectedStudy.current!==parent||deleted.current.has(id))return;lane={note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false};lanes.current.set(id,lane);}setCurrent(id);setTool('analysis');setAnalysisTab('Notes');setError('');update();}
   catch(e){if(valid(captured)&&requestNavigation===navigation.current&&selectedStudy.current===parent)fail(e);}
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
 function beginDelete(){const lane=current?lanes.current.get(current):undefined;if(!lane||!authority)return;
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
  try{await execute(token,target.attempt);if(!valid(captured)||lanes.current.get(lane.note.id)!==lane)return;
   if(selectedNote.current===lane.note.id&&selectedStudy.current===lane.note.study_id){const source=deletionFocusSource(lane.note.id);setDeletionFocus(source?{epoch:captured,navigation:navigation.current,study:lane.note.study_id,source}:null);}
   deleted.current.add(lane.note.id);clearTimeout(lane.timer);lanes.current.delete(lane.note.id);deletions.current.delete(lane.note.id);setNotes(old=>old.filter(note=>note.id!==lane.note.id));setCurrent(old=>old===lane.note.id?null:old);setDeleteTarget(old=>old===lane.note.id?null:old);
  }catch(e){if(!valid(captured))return;const code=e instanceof NotesFailure?e.code:'';
   if(['note_revision_conflict','resource_unavailable','operation_payload_mismatch','scribeswell_personal_notes_input_invalid'].includes(code)){lane.status='conflict';target.status='conflict';target.attempt=undefined;target.reviewRevision=undefined;target.review=undefined;target.message='Deletion not confirmed. Your input is kept. Review the current note before confirming again.';}
   else {target.status='unknown';target.message='Deletion not confirmed. Retry the original deletion.';}
   if(['authentication_required','studies_access_denied'].includes(code)){target.open=false;setDeleteTarget(null);fail(e);}
  }finally{if(valid(captured))update();}
 }
 async function start(){if(!token){setError('Sign in to use My studies.');return false;}const captured=epoch.current;setBusy(true);try{enrollment.current??=uuid();await api.enroll(token,enrollment.current);if(!valid(captured))return false;enrollment.current=undefined;setError('');return true;}catch(e){if(valid(captured))fail(e);return false;}finally{if(valid(captured))setBusy(false);}}
 async function create(title:string|null){if(!token)return;if(creation.current&&creation.current.command!=='study.create'){setError('Retry the original note creation before starting another study.');return;}const captured=epoch.current;setBusy(true);try{if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'study.create',path:'/api/studies',method:'POST',payload:{operation_id,title},generation:0};}const result=await execute(token,creation.current);if(!valid(captured))return;creation.current.study=result.study_id;await openStudy(result.study_id);}catch(e){if(valid(captured)){if(e instanceof NotesFailure&&e.code==='scribeswell_personal_notes_input_invalid')creation.current=undefined;fail(e);}}finally{if(valid(captured))setBusy(false);}}
 async function addNote(){if(!token||!study)return;if(creation.current&&(creation.current.command!=='note.create'||creation.current.study!==study.id)){setError('Retry the original creation before starting another note.');return;}await exit(async()=>{const captured=epoch.current;setBusy(true);try{if(!creation.current){const operation_id=uuid();creation.current={operation_id,command:'note.create',path:`/api/studies/${study.id}/notes`,method:'POST',payload:{operation_id,value:{document:{version:1,blocks:[]},connections:[],highlights:[]}},study:study.id,generation:0};}const result=await execute(token,creation.current);if(!valid(captured))return;const note=await api.note(token,study.id,result.note_id!);if(!valid(captured)||deleted.current.has(note.id))return;creation.current=undefined;lanes.current.set(note.id,{note,value:note.value,generation:0,saved:0,status:'saved',composing:false,invalid:false});setNotes(old=>[note,...old]);setCurrent(note.id);setTool('analysis');setAnalysisTab('Notes');update();}catch(e){if(valid(captured))fail(e);}finally{if(valid(captured))setBusy(false);}},true);}
 useEffect(()=>{function unload(e:BeforeUnloadEvent){if([...lanes.current.values()].some(l=>!!l.deletion?.attempt||l.invalid||l.generation!==l.saved)||[...titles.current.values()].some(edit=>!edit.confirmed&&(edit.attempt||edit.running))||[...collections.current.values()].some(lane=>!lane.confirmed&&(!!lane.attempt||!!lane.running))){e.preventDefault();e.returnValue='';}}window.addEventListener('beforeunload',unload);return()=>window.removeEventListener('beforeunload',unload);},[]);
 const visible=dataAccount.current===account&&authority,libraryGeneration=library.current.generation,libraryEpoch=epoch.current,libraryNavigation=navigation.current;
 const canRestoreLibrary=()=>identity.current===account&&epoch.current===libraryEpoch&&library.current.generation===libraryGeneration&&navigation.current===libraryNavigation&&!selectedStudy.current&&!library.current.pending&&library.current.positionLocked;
 const titleEdit=study&&visible?titles.current.get(study.id):undefined;
 const collection=study&&visible?collections.current.get(study.id):undefined;
 const lane=current&&visible?lanes.current.get(current):undefined;
 return {deletionFocus:visible?deletionFocus:null,canFocusDeletion:()=>!!deletionFocus&&activeTool.current!==null&&stillReplacingFocus(deletionFocus.source)&&valid(deletionFocus.epoch)&&authority&&dataAccount.current===account&&selectedNote.current===null&&selectedStudy.current===deletionFocus.study&&navigation.current===deletionFocus.navigation,pendingDeletions:visible?[...deletions.current.values()].filter(target=>!!target.attempt&&!target.open):[],openDeletion:(target:Deletion)=>{if(!visible||deletions.current.get(target.lane.note.id)!==target)return;target.open=true;setDeleteTarget(target.lane.note.id);update();},deletion:visible&&deleteTarget?deletions.current.get(deleteTarget):undefined,beginDelete,closeDelete,confirmDelete,recoverDeleteSave,reviewDelete,accountKey:account??'anonymous',enabled:import.meta.env.VITE_STUDIES_ENABLED==='true',tool,setTool,analysisTab,setAnalysisTab,invalidInput:()=>{if(lane&&!lane.deletion?.attempt){lane.invalid=true;lane.status='failed';clearTimeout(lane.timer);update();}},studies:visible&&libraryVerified?studies:[],study:visible?study:null,notes:visible?notes:[],current:visible?current:null,lane,error,busy,searchCandidate:visible?searchCandidate:'',searchMasked:!visible,setSearchCandidate:changeSearchCandidate,searchStudies,clearSearch,libraryBusy,libraryError,libraryInputInvalid,libraryVerified:visible&&libraryVerified,libraryRestore,libraryPosition:library.current.position,canRestoreLibrary,finishLibraryRestore:()=>{if(canRestoreLibrary())library.current.positionLocked=false;},rememberLibrary,studyCursor:visible?studyCursor:null,notesCursor,collection,collect,removePassage,retryPassages,reviewPassages,cancelPassageIntent,titleEdit: titleEdit?.open?titleEdit:undefined,beginRename,changeTitle,cancelRename,saveTitle,reloadTitle,loadStudies,moreNotes,openStudies,openStudy,openNote,start,create,addNote,change,composition,retry:()=>lane&&flush(lane,true),exit,exitPrompt,stay:()=>setExitPrompt(null),proceed:async()=>{const prompt=exitPrompt;setExitPrompt(null);if(prompt){if(prompt.discard&&lanes.current.get(prompt.discard.note.id)===prompt.discard){clearTimeout(prompt.discard.timer);lanes.current.delete(prompt.discard.note.id);setCurrent(null);}await prompt.action();}},leave:()=>{const requestNavigation=++navigation.current;return exit(()=>{if(requestNavigation!==navigation.current)return;collectionNavigation.current++;selectedStudy.current=undefined;notesPosition.current=null;setStudy(null);setCurrent(null);setNotes([]);setTool('studies');void loadStudies();},true);}};
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
export function StudiesProvider({children}:{children:ReactNode}){const value=useStatefulStudies();return <Context.Provider value={value}>{children}{value.deletionFocus&&<DeletionFocus studies={value}/>} {value.exitPrompt&&<ExitDialog studies={value}/>} {value.deletion?.open&&<DeleteDialog studies={value}/>} {value.pendingDeletions.map(target=><button key={target.lane.note.id} className="underline m-2" onClick={()=>value.openDeletion(target)}>Recover deletion: {target.label}</button>)}</Context.Provider>;}
export function useStudies(){const value=useContext(Context);if(!value)throw Error('StudiesProvider required');return value;}
