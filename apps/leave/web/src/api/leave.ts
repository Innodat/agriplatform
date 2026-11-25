import {isDraftInput,type DraftInput} from '../draft-input.ts';
// Owner API adapter. Every business request goes through Leave; no browser database access.
import type {Organization as WireOrganization,Organizations as WireOrganizations,Receipt as WireReceipt,SelectionResult as WireSelectionResult,Unresolved as WireUnresolved,Language as WireLanguage,Ready,Setup,Choice as WireChoice,Choices as WireChoices,DiscardDraftV1OrganizationsOrgIdDraftsDraftIdDiscardPostData} from './generated/types.gen';
export type Organization=Readonly<WireOrganization>;
export type Organizations=Readonly<Omit<WireOrganizations,'organizations'>&{organizations:readonly Organization[]}>;
export type Receipt=Readonly<Required<Omit<WireReceipt,'result'>>&{result:Readonly<Required<WireSelectionResult>>}>;
export type Unresolved=Readonly<Required<WireUnresolved>>;
export type Language=Readonly<WireLanguage>;
export type DraftChoice=Readonly<WireChoice>;
export type DraftChoicesResponse=Readonly<WireChoices>;
export type DraftPreparation=Readonly<Ready|Setup>;

export type DraftContextV1=DraftPreparation extends infer T?T extends {status:'ready'}?T&{scope_generation:string;active_draft:{draft_id:string;revision:string}|null}:T:never;
export type DraftCommandResult={draft_id:string;revision:string;scope_generation:string}&({command:'start';disposition:'created'|'resumed'}|{command:'save';disposition:'saved'}|{command:'discard';disposition:'discarded'});
export type DraftOutcome={operation_id:string;status:'unresolved'}|{operation_id:string;status:'committed';result:DraftCommandResult};
export type DraftRead={org_id:string;draft_id:string;revision:string}&({state:'discarded';discarded_at:string}|{state:'active';input:DraftInput;editability:{status:'editable'}|{status:'read_only';reason:'permission_missing'|'employment_ended'|'employment_periods_missing'};setup_notices:{code:'work_timezone_missing'|'work_timezone_invalid'}[];updated_at:string});
export type EditorOpening={context:Extract<DraftContextV1,{status:'ready'}>;draft:Extract<DraftRead,{state:'active'}>;choices:DraftChoicesResponse}|{context:Extract<DraftContextV1,{status:'ready'}>;draft:Extract<DraftRead,{state:'discarded'}>};
export type DiscardDraft=DiscardDraftV1OrganizationsOrgIdDraftsDraftIdDiscardPostData['body'];
export type SaveDraft={operation_id:string;expected_revision:string;input:DraftInput};
export type StartDraft={operation_id:string;expected_scope_generation:string};
export type Result<T>=Readonly<{ok:true;value:T}>|Readonly<{ok:false;error_id:string;details?:Readonly<Record<string,unknown>>}>;
const object=(v:unknown,keys:string[]):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join()===keys.sort().join();
export const id=(v:unknown):v is string=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(v)&&v!=='00000000-0000-0000-0000-000000000000';
const revision=(v:unknown):v is string=>typeof v==='string'&&/^(0|[1-9][0-9]{0,18})$/.test(v)&&BigInt(v)<=9223372036854775807n;

export const draftId=(v:unknown):v is string=>id(v)&&v[14]==='4'&&/[89ab]/.test(v[19]!);
const utc=(v:unknown):v is string=>typeof v==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)$/.test(v)&&Number.isFinite(Date.parse(v));
const draftOutcome=(operation:string,command?:DraftCommandResult['command'],target?:string)=>(v:unknown):v is DraftOutcome=>{
 if(object(v,['operation_id','status']))return v.operation_id===operation&&v.status==='unresolved';
 if(!object(v,['operation_id','status','result'])||v.operation_id!==operation||v.status!=='committed'||!object(v.result,['command','draft_id','revision','scope_generation','disposition']))return false;
 const r=v.result;
 return (!command||r.command===command)&&(!target||r.draft_id===target)&&draftId(r.draft_id)&&revision(r.revision)&&r.revision!=='0'&&revision(r.scope_generation)&&(r.command==='start'&&['created','resumed'].includes(String(r.disposition))||r.command==='save'&&r.disposition==='saved'||r.command==='discard'&&r.disposition==='discarded'&&r.scope_generation!=='0');
};
const fieldPaths=new Set(['$','operation_id','expected_revision','expected_scope_generation','input','input.input_version','input.leave_type_id','input.duration_mode','input.note','input.full_days','input.half_day','input.hours','input.full_days.start','input.full_days.start.text','input.full_days.start.format','input.full_days.end','input.full_days.end.text','input.full_days.end.format','input.half_day.date','input.half_day.date.text','input.half_day.date.format','input.hours.date','input.hours.date.text','input.hours.date.format','input.hours.duration','input.hours.duration.text','input.hours.duration.format']);
const fieldRules=new Set(['required','unknown_field','invalid_type','invalid_value','too_long','unsafe_text','invalid_json']);
const draftErrors=(name:string,v:unknown):boolean=>{
 if(name==='leave.draft_revision_conflict')return object(v,['current_revision'])&&revision(v.current_revision)&&v.current_revision!=='0';
 if(name==='leave.draft_discarded')return object(v,['draft_id'])&&draftId(v.draft_id);
 if(name==='leave.draft_start_outdated')return object(v,['current_scope_generation'])&&revision(v.current_scope_generation);
 if(name==='leave.draft_read_only')return object(v,['reason'])&&v.reason==='employment_ended';
 if(name==='leave.setup_required')return object(v,['reason'])&&typeof v.reason==='string'&&['employment_missing','employment_periods_missing','identity_person_link_required','identity_actor_setup_required'].includes(v.reason);
 if(name==='request_too_large')return object(v,['max_bytes'])&&v.max_bytes===32768;
 if(name==='validation_failed')return object(v,['fields'])&&Array.isArray(v.fields)&&v.fields.length>0&&v.fields.length<=64&&v.fields.every(f=>object(f,['path','rule'])&&typeof f.path==='string'&&fieldPaths.has(f.path)&&typeof f.rule==='string'&&fieldRules.has(f.rule))||object(v,[]);
 return object(v,[]);
};
const preparation=(org:string)=>(v:unknown):v is DraftPreparation=>{

   if(object(v,['status','org_id','reason']))return v.status==='setup_required'&&v.org_id===org&&typeof v.reason==='string'&&['employment_missing','identity_person_link_required','identity_actor_setup_required'].includes(v.reason);
   return object(v,['status','org_id','employment_id','editability','setup_notices'])&&v.status==='ready'&&v.org_id===org&&id(v.employment_id)&&(object(v.editability,['status'])&&v.editability.status==='editable'||object(v.editability,['status','reason'])&&v.editability.status==='read_only'&&typeof v.editability.reason==='string'&&['permission_missing','employment_ended','employment_periods_missing'].includes(v.editability.reason))&&Array.isArray(v.setup_notices)&&v.setup_notices.length<=1&&v.setup_notices.every(n=>object(n,['code'])&&typeof n.code==='string'&&['work_timezone_missing','work_timezone_invalid'].includes(n.code));

};

const choicesResponse=(org:string,selected:string|null)=>{
 const choice=(v:unknown):v is DraftChoice=>object(v,['type_id','version_id','name','revision','permitted_modes'])&&id(v.type_id)&&id(v.version_id)&&typeof v.name==='string'&&Array.from(v.name).length>=1&&Array.from(v.name).length<=120&&!/[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]$/u.test(v.name)&&! /^[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/u.test(v.name)&&!/[\p{Cc}\p{Cs}]/u.test(v.name)&&revision(v.revision)&&v.revision!=='0'&&Array.isArray(v.permitted_modes)&&v.permitted_modes.length>=1&&v.permitted_modes.length<=3&&new Set(v.permitted_modes).size===v.permitted_modes.length&&v.permitted_modes.every(mode=>typeof mode==='string'&&['full_days','half_day','hours'].includes(mode));
 return (v:unknown):v is DraftChoicesResponse=>{
    if(!object(v,['choices','next_cursor','selected'])||!Array.isArray(v.choices)||v.choices.length>100||!v.choices.every(choice))return false;
    const choices=v.choices as DraftChoice[];if(choices.some((c,i)=>i>0&&choices[i-1]!.type_id>=c.type_id))return false;
    if(v.next_cursor!==null){
     if(typeof v.next_cursor!=='string'||!/[A-Za-z0-9_-]{1,256}/.test(v.next_cursor)||v.choices.length!==100)return false;
     try{const text=atob(v.next_cursor.replaceAll('-','+').replaceAll('_','/'));const position:unknown=JSON.parse(text);if(!object(position,['version','org_id','after'])||position.version!==1||position.org_id!==org||position.after!==v.choices.at(-1)!.type_id||btoa(JSON.stringify({after:position.after,org_id:org,version:1})).replaceAll('+','-').replaceAll('/','_').replaceAll('=','')!==v.next_cursor)return false;}catch{return false;}
    }
    const r=v.selected;
    if(selected===null)return object(r,['status'])&&r.status==='not_requested';
    if(object(r,['status'])&&r.status==='obsolete')return true;
    if(!object(r,['status','choice'])||r.status!=='available'||!choice(r.choice)||r.choice.type_id!==selected)return false;
    const resolved=r.choice;
    return choices.every(c=>c.type_id!==selected||c.version_id===resolved.version_id&&c.name===resolved.name&&c.revision===resolved.revision&&c.permitted_modes.join()===resolved.permitted_modes.join());
   };
};
const contextResponse=(org:string)=>(v:unknown):v is DraftContextV1=>{
   if(object(v,['status','org_id','reason']))return preparation(org)(v);
   if(!object(v,['status','org_id','employment_id','editability','setup_notices','scope_generation','active_draft']))return false;
   const {scope_generation,active_draft,...legacy}=v;
   return preparation(org)(legacy)&&revision(scope_generation)&&(active_draft===null||object(active_draft,['draft_id','revision'])&&draftId(active_draft.draft_id)&&revision(active_draft.revision)&&active_draft.revision!=='0');
  };
const draftResponse=(org:string,draft:string)=>(v:unknown):v is DraftRead=>{
   const common=(v:Record<string,unknown>)=>v.org_id===org&&v.draft_id===draft&&revision(v.revision)&&v.revision!=='0';
   if(object(v,['org_id','draft_id','revision','state','discarded_at']))return common(v)&&v.state==='discarded'&&utc(v.discarded_at);
   return object(v,['org_id','draft_id','revision','state','input','editability','setup_notices','updated_at'])&&common(v)&&v.state==='active'&&isDraftInput(v.input)&&utc(v.updated_at)&&preparation(org)({status:'ready',org_id:org,employment_id:org,editability:v.editability,setup_notices:v.setup_notices});
  };
export function createLeaveClient(request:typeof fetch=fetch){
 async function call<T>(path:string,token:string,signal:AbortSignal,validate:(v:unknown)=>v is T,method='GET',body?:unknown,maxBytes=65536,errorDetails:(id:string,v:unknown)=>boolean=(_id,v)=>object(v,[])):Promise<Result<T>>{
  const controller=new AbortController(),abort=()=>controller.abort();signal.addEventListener('abort',abort,{once:true});if(signal.aborted)abort();const timer=setTimeout(abort,method==='POST'||method==='PUT'?12000:10000);
  try{
   const response=await request('/api'+path,{method,signal:controller.signal,headers:{Authorization:'Bearer '+token,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,cache:'no-store',redirect:'error'});
   if(controller.signal.aborted)throw Error();
   const reader=response.body?.getReader();if(!reader)throw Error();let raw='',bytes=0;const decoder=new TextDecoder('utf-8',{fatal:true});
   try{while(true){const part=await reader.read();if(part.done)break;bytes+=part.value.length;if(bytes>maxBytes||controller.signal.aborted)throw Error();raw+=decoder.decode(part.value,{stream:true});}raw+=decoder.decode();}finally{void reader.cancel().catch(()=>{});}
   const value:unknown=JSON.parse(raw);
   if(controller.signal.aborted)throw Error();
   if(response.status===200||response.status===202){if(!validate(value))return{ok:false,error_id:'invalid_response'};return{ok:true,value};}
   if(object(value,['error_id','error','details'])&&typeof value.error_id==='string'&&typeof value.error==='string'&&errorDetails(value.error_id,value.details)&&[401,403,404,409,413,422,503].includes(response.status))return{ok:false,error_id:value.error_id,...(Object.keys(value.details as object).length?{details:value.details as Record<string,unknown>}:{})};
   return{ok:false,error_id:'invalid_response'};
  }catch{return{ok:false,error_id:signal.aborted?'cancelled':'api_unavailable'};}
  finally{clearTimeout(timer);signal.removeEventListener('abort',abort);controller.abort();}
 }
 const language=(v:unknown):v is Language=>object(v,['preferred_locale','revision'])&&['en','pt'].includes(String(v.preferred_locale))&&revision(v.revision);
 const outcome=(org:string,operation:string)=>(v:unknown):v is Receipt|Unresolved=>object(v,['operation_id','status'])&&v.operation_id===operation&&v.status==='unresolved'||object(v,['operation_id','status','result'])&&v.operation_id===operation&&v.status==='committed'&&object(v.result,['command','org_id','event_id'])&&v.result.command==='select_organization'&&v.result.org_id===org&&id(v.result.event_id);
 return{
  choices:(token:string,signal:AbortSignal,org:string,selected:string|null,cursor:string|null)=>{
   const query=new URLSearchParams();if(selected!==null)query.set('selected_type_id',selected);if(cursor!==null)query.set('cursor',cursor);
   return call('/v1/organizations/'+org+'/draft-choices'+(query.size?'?'+query.toString():''),token,signal,choicesResponse(org,selected),'GET',undefined,131072);
  },
  context:(token:string,signal:AbortSignal,org:string)=>call('/v1/organizations/'+org+'/me/draft-context',token,signal,preparation(org)),
  draftContext:(token:string,signal:AbortSignal,org:string)=>call('/v1/organizations/'+org+'/me/draft-context?draft_context_version=1',token,signal,contextResponse(org)),
  startDraft:(token:string,signal:AbortSignal,org:string,command:StartDraft)=>call('/v1/organizations/'+org+'/me/draft/start',token,signal,draftOutcome(command.operation_id,'start'),'POST',command,65536,draftErrors),
  saveDraft:(token:string,signal:AbortSignal,org:string,draft:string,command:SaveDraft)=>call('/v1/organizations/'+org+'/drafts/'+draft+'/input',token,signal,draftOutcome(command.operation_id,'save',draft),'PUT',command,65536,draftErrors),
  discardDraft:(token:string,signal:AbortSignal,org:string,draft:string,command:DiscardDraft)=>call('/v1/organizations/'+org+'/drafts/'+draft+'/discard',token,signal,draftOutcome(command.operation_id,'discard',draft),'POST',command,65536,draftErrors),
  draftOutcome:(token:string,signal:AbortSignal,org:string,operation:string)=>call('/v1/organizations/'+org+'/operations/'+operation,token,signal,draftOutcome(operation),'GET',undefined,65536,draftErrors),
  editorOpen:(token:string,signal:AbortSignal,org:string,draft:string)=>call('/v1/organizations/'+org+'/drafts/'+draft+'/editor',token,signal,(v:unknown):v is EditorOpening=>{
   if(!object(v,['context','draft','choices'])&&!object(v,['context','draft']))return false;
   if(!contextResponse(org)(v.context)||v.context.status!=='ready'||!draftResponse(org,draft)(v.draft))return false;
   const c=v.context,d=v.draft;
   if(d.state==='discarded')return object(v,['context','draft'])&&c.active_draft?.draft_id!==draft;
   return object(v,['context','draft','choices'])&&c.active_draft?.draft_id===draft&&c.active_draft.revision===d.revision&&JSON.stringify(c.editability)===JSON.stringify(d.editability)&&JSON.stringify(c.setup_notices)===JSON.stringify(d.setup_notices)&&choicesResponse(org,d.input.leave_type_id)(v.choices)&&!(v.choices.selected.status==='obsolete'&&v.choices.choices.some(choice=>choice.type_id===d.input.leave_type_id));
  },'GET',undefined,196608,draftErrors),
  readDraft:(token:string,signal:AbortSignal,org:string,draft:string)=>call('/v1/organizations/'+org+'/drafts/'+draft,token,signal,draftResponse(org,draft),'GET',undefined,65536,draftErrors),
  async organizations(token:string,signal:AbortSignal):Promise<Result<Organizations>>{
   const all:Organization[]=[];let cursor:string|null=null;const seen=new Set<string>();
   do{
    const result:Result<Organizations>=await call('/v1/me/organizations'+(cursor?'?cursor='+encodeURIComponent(cursor):''),token,signal,(v:unknown):v is Organizations=>object(v,['organizations','next_cursor'])&&Array.isArray(v.organizations)&&v.organizations.length<=100&&v.organizations.every(o=>object(o,['org_id','name','membership_id'])&&id(o.org_id)&&typeof o.name==='string'&&o.name.length<=4096&&revision(o.membership_id)&&o.membership_id!=='0')&&(v.next_cursor===null||typeof v.next_cursor==='string'&&/^[A-Za-z0-9_-]{48}$/.test(v.next_cursor)));
    if(!result.ok)return result;
    for(const org of result.value.organizations){if(org.org_id<=(all.at(-1)?.org_id??''))return{ok:false,error_id:'invalid_response'};all.push(org);}
    cursor=result.value.next_cursor;
    if(cursor){if(seen.has(cursor)||!all.length||cursor!==btoa(all.at(-1)!.org_id).replaceAll('+','-').replaceAll('/','_').replaceAll('=',''))return{ok:false,error_id:'invalid_response'};seen.add(cursor);}
    if(all.length>10000)return{ok:false,error_id:'invalid_response'};
   }while(cursor);
   return{ok:true,value:{organizations:all,next_cursor:null}};
  },
  select:(token:string,signal:AbortSignal,org:string,operation:string)=>call('/v1/organizations/'+org+'/context/selection',token,signal,outcome(org,operation),'POST',{operation_id:operation}),
  lookup:(token:string,signal:AbortSignal,org:string,operation:string)=>call('/v1/organizations/'+org+'/context/operations/'+operation,token,signal,outcome(org,operation)),
  language:(token:string,signal:AbortSignal)=>call('/v1/me/preferences/language',token,signal,language),
  setLanguage:(token:string,signal:AbortSignal,command:{operation_id:string;expected_revision:string;preferred_locale:'en'|'pt'})=>call('/v1/me/preferences/language',token,signal,language,'PUT',command),
 };
}
export type LeaveClient=ReturnType<typeof createLeaveClient>;
