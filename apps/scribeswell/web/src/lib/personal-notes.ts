/** Same-origin private adapter. No private bodies in browser storage or diagnostics. */
import type {NoteValue, NoteView, StudyView, OperationAck, StudyPage, NotePage, Outcome, EnrollmentAck, PassageList} from '@/generated/personal-notes/types.gen';
export type {NoteValue,NoteView,StudyView,OperationAck,PassageList};
import {isReadableNoteValue} from './note-value';
// A declared page can carry 50 maximum-size aggregates plus bounded attribution.
const MAX_RESPONSE_CHARS=50*262144+65536;
const base=import.meta.env.BASE_URL.replace(/\/$/,'');
export class NotesFailure extends Error { constructor(public code:string){super(code);} }
export const emptyValue=():NoteValue=>({document:{version:1,blocks:[]},connections:[],highlights:[]});
export function uuid(){return crypto.randomUUID();}
export async function request<T>(token:string,path:string,method='GET',body?:unknown,timeout=15000,signal?:AbortSignal):Promise<T>{
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
 try{
  const response=await fetch(base+path,{method,headers:{Authorization:`Bearer ${token}`,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,signal:signal?AbortSignal.any([signal,controller.signal]):controller.signal,cache:'no-store',credentials:'omit',redirect:'error'});
  const raw=await response.text();
  if(raw.length>MAX_RESPONSE_CHARS)throw new NotesFailure('response_invalid');
  let value:unknown;try{value=JSON.parse(raw);}catch{throw new NotesFailure('operation_unresolved');}
  if(!response.ok){const code=value&&typeof value==='object'&&'code'in value&&typeof value.code==='string'?value.code:'studies_storage_unavailable';throw new NotesFailure(code);}
  return value as T;
 }catch(error){if(error instanceof NotesFailure)throw error;throw new NotesFailure('operation_unresolved');}
 finally{clearTimeout(timer);}
}
const noteIdentifier=(value:unknown):value is string=>typeof value==='string'&&value.length===36&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value)&&value!=='00000000-0000-0000-0000-000000000000';
const object=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value);
function creditTitle(value:unknown){return typeof value==='string'&&Array.from(value).length>=1&&Array.from(value).length<=200&&/\S/u.test(value)&&!/[\u0000-\u001f\u007f-\u009f\uD800-\uDFFF]/u.test(value);}
function creditTime(value:unknown){if(typeof value!=='string'||value.length!==27||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$/.test(value)||Number(value.slice(0,4))<1)return false;try{return new Date(value).toISOString()===value.slice(0,23)+'Z';}catch{return false;}}
function readableCredit(value:unknown,owner:unknown,note:boolean){
 if(value===undefined||value===null)return true;
 if(!object(value)||Object.keys(value).sort().join(',')!=='created_at,created_by_actor_id,label,origin_account_id,origin_note_id,origin_study_id,relation,source_account_id,source_note_id,source_study_id')return false;
 if(!['source_account_id','source_study_id','origin_account_id','origin_study_id','created_by_actor_id'].every(key=>noteIdentifier(value[key]))||value.source_account_id!==owner||value.origin_account_id!==owner||!creditTime(value.created_at)||!creditTitle(value.label))return false;
 return note?['note.duplicate','note.conflict_copy','study.copy'].includes(value.relation as string)&&noteIdentifier(value.source_note_id)&&noteIdentifier(value.origin_note_id):value.relation==='study.copy'&&value.source_note_id===null&&value.origin_note_id===null;
}
function readableStudy(value:unknown):value is StudyView{return object(value)&&noteIdentifier(value.id)&&noteIdentifier(value.owner_account_id)&&readableCredit(value.copy_credit,value.owner_account_id,false);}
function studyPage(value:StudyPage){if(!value||!Array.isArray(value.items)||!value.items.every(readableStudy))throw new NotesFailure('response_invalid');return value;}
async function readStudy(token:string,id:string,signal?:AbortSignal){const value=await request<unknown>(token,`/api/studies/${id}`,'GET',undefined,15000,signal);if(!readableStudy(value)||value.id!==id)throw new NotesFailure('response_invalid');return value;}
function readableNote(value:unknown):value is NoteView {
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 const note=value as Record<string,unknown>;
 return ['id','study_id','owner_account_id'].every(key=>noteIdentifier(note[key]))&&typeof note.revision==='string'&&/^[1-9][0-9]{0,18}$/.test(note.revision)&&BigInt(note.revision)<=9223372036854775807n&&note.visibility==='study'&&readableCredit(note.copy_credit,note.owner_account_id,true)&&isReadableNoteValue(note.value);
}
async function readNote(token:string,study:string,id:string,signal?:AbortSignal):Promise<NoteView>{
 const value=await request<unknown>(token,`/api/studies/${study}/notes/${id}`,'GET',undefined,15000,signal);
 if(!readableNote(value)||value.id!==id||value.study_id!==study)throw new NotesFailure('response_invalid');
 return value;
}
async function readNotes(token:string,study:string,cursor?:string,signal?:AbortSignal):Promise<NotePage>{
 const value=await request<NotePage>(token,`/api/studies/${study}/notes`+(cursor?'?cursor='+encodeURIComponent(cursor):''),'GET',undefined,15000,signal);
 if(!value||!Array.isArray(value.items)||value.items.length>50||!value.items.every(note=>readableNote(note)&&note.study_id===study)||new Set(value.items.map(note=>note.id)).size!==value.items.length||value.next_cursor!==null&&(typeof value.next_cursor!=='string'||!/^[A-Za-z0-9_-]{1,512}$/.test(value.next_cursor)))throw new NotesFailure('response_invalid');
 return value;
}
export const api={
 search:(token:string,query:string,cursor?:string)=>request<StudyPage>(token,'/api/studies/search','POST',{query,cursor:cursor??null}).then(studyPage),
 enroll:(token:string,operation_id:string)=>request<EnrollmentAck>(token,'/api/studies/enrollment','POST',{operation_id}),
 studies:(token:string,cursor?:string,signal?:AbortSignal)=>request<StudyPage>(token,'/api/studies'+(cursor?'?cursor='+encodeURIComponent(cursor):''),'GET',undefined,15000,signal).then(studyPage),
 study:readStudy,
 notes:readNotes,
 passages:(token:string,id:string,signal?:AbortSignal)=>request<PassageList>(token,`/api/studies/${id}/passages`,'GET',undefined,15000,signal),
 note:readNote,
 lookup:(token:string,operation:string,command:string,timeout=15000)=>request<Outcome>(token,`/api/operations/${operation}?command=${command}`,'GET',undefined,timeout),
};
export type Attempt={operation_id:string;command:'study.create'|'study.rename'|'study.passages.replace'|'study.delete'|'note.create'|'note.replace'|'note.delete'|'note.duplicate'|'note.conflict_copy'|'study.copy';path:string;method:string;payload:Record<string,unknown>;study?:string;note?:string;sourceStudy?:string;sourceNote?:string;generation:number};
function ack(value:OperationAck,attempt:Attempt){
 if(!value||Object.keys(value).sort().join(',')!=='command,note_id,operation_id,revision,study_id'||typeof value.revision!=='string'||value.operation_id!==attempt.operation_id||value.command!==attempt.command||!/^\d+$/.test(value.revision)||BigInt(value.revision)<1n||BigInt(value.revision)>9223372036854775807n||!noteIdentifier(value.study_id)||(value.note_id!==null&&!noteIdentifier(value.note_id))||(attempt.command==='study.copy'&&value.study_id===attempt.sourceStudy)||(['note.duplicate','note.conflict_copy'].includes(attempt.command)&&value.note_id===attempt.sourceNote)||(attempt.study&&attempt.command!=='study.copy'&&value.study_id!==attempt.study)||(attempt.note&&value.note_id!==attempt.note)||(['study.create','study.rename','study.passages.replace','study.delete','study.copy'].includes(attempt.command)?value.note_id!==null:!value.note_id))throw new NotesFailure('operation_unresolved');
 return value;
}
export async function execute(token:string,attempt:Attempt):Promise<OperationAck>{
 try{return ack(await request<OperationAck>(token,attempt.path,attempt.method,attempt.payload),attempt);}
 catch(error){
  if(!(error instanceof NotesFailure)||error.code!=='operation_unresolved')throw error;
  const end=performance.now()+10000;
  for(let i=0;i<2;i++){
   try{const result=await api.lookup(token,attempt.operation_id,attempt.command,Math.max(1,end-performance.now()));if(result.status==='committed')return ack(result.outcome,attempt);}
   catch(failure){if(failure instanceof NotesFailure&&['authentication_required','studies_access_denied'].includes(failure.code))throw failure;}
   if(performance.now()>=end)break;
  }
  throw new NotesFailure('operation_unresolved');
 }
}
