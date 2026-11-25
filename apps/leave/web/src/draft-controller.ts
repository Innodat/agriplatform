// D1 owns the original start operation until resolved. No form payload is persisted here.
import type {ExecutionLease} from './auth/lifecycle.ts';
import type {LeaveClient,DraftContextV1,DraftRead,StartDraft,DraftOutcome,DraftChoicesResponse} from './api/leave.ts';
export type DraftState={kind:'loading'|'working'|'unresolved'|'unavailable'|'outdated'|'closed'|'read_only'|'setup_required'}|{kind:'denied';error_id?:string;draft?:string}|{kind:'context';value:DraftContextV1}|{kind:'opened';value:DraftRead;firstChoiceEligible?:boolean;background?:DraftContextV1;choices:DraftChoicesResponse};
export function createDraftController(options:{client:Pick<LeaveClient,'draftContext'|'startDraft'|'draftOutcome'|'editorOpen'>;acquire:()=>ExecutionLease<unknown>|null;publish:(s:DraftState)=>void;navigate?:(draft:string|null)=>void;newId?:()=>string;now?:()=>number}){
 let epoch=0,disposed=false,active:AbortController|null=null,pending:StartDraft|null=null,scope='',context:DraftContextV1|null=null,busy=false,opening:{draft:string;createdRevision?:string}|null=null;
 const set=(s:DraftState)=>{if(!disposed)options.publish(s);};
 const failureState=(name:string):'outdated'|'read_only'|'setup_required'|'denied'=>name==='leave.draft_start_outdated'?'outdated':name==='leave.draft_read_only'?'read_only':name==='leave.setup_required'?'setup_required':'denied';
 const terminal=(name:string)=>['authentication_required','access_denied','identity.verification_required','leave.draft_start_outdated','leave.draft_read_only','leave.setup_required','validation_failed','operation_mismatch','resource_not_found'].includes(name);
 function clear(){epoch++;active?.abort();active=null;busy=false;}
 async function execute(work:(lease:ExecutionLease<unknown>,signal:AbortSignal,current:()=>boolean)=>Promise<void>){
  clear();const mine=epoch,lease=options.acquire();if(!lease){set({kind:'denied',error_id:'authentication_required'});return;}
  const c=new AbortController();active=c;const abort=()=>c.abort();lease.signal.addEventListener('abort',abort,{once:true});if(lease.signal.aborted)abort();
  const current=()=>!disposed&&mine===epoch&&lease.isCurrent()&&!c.signal.aborted;
  try{await work(lease,c.signal,current);}catch{if(current())set({kind:'unavailable'});}finally{lease.signal.removeEventListener('abort',abort);lease.release();c.abort();if(active===c)active=null;}
 }
 function acceptOpening(r:Awaited<ReturnType<LeaveClient['editorOpen']>>,draft:string,createdRevision?:string){
  if(!r.ok){
   if(['authentication_required','access_denied','identity.verification_required','resource_not_found'].includes(r.error_id))set({kind:'denied',error_id:r.error_id,draft});
   else set({kind:r.error_id==='leave.setup_required'?'setup_required':'unavailable'});
   return;
  }
  context=r.value.context;
  if(!('choices' in r.value)){set({kind:'closed'});return;}
  set({kind:'opened',value:r.value.draft,choices:r.value.choices,firstChoiceEligible:createdRevision!==undefined&&r.value.draft.revision===createdRevision,background:context});options.navigate?.(draft);
 }
 async function openWith(lease:ExecutionLease<unknown>,signal:AbortSignal,current:()=>boolean,draft:string,createdRevision?:string){
  opening={draft,createdRevision};
  const r=await options.client.editorOpen(lease.session.access_token,signal,scope,draft);if(!current())return;
  acceptOpening(r,draft,createdRevision);
 }
 async function load(org:string,draft?:string){pending=null;scope=org;context=null;opening=draft?{draft}:null;set({kind:'loading'});return execute(async(lease,signal,current)=>{
  if(draft){await openWith(lease,signal,current,draft);return;}
  const r=await options.client.draftContext(lease.session.access_token,signal,org);if(!current())return;
  if(!r.ok){
   if(['authentication_required','access_denied','identity.verification_required'].includes(r.error_id))set({kind:'denied',error_id:r.error_id});
   else set({kind:'unavailable'});
   return;
  }
  context=r.value;
  if(draft)await openWith(lease,signal,current,draft);else set({kind:'context',value:r.value});
 });}
 async function start(recover=false){
  if(busy||!pending)return;busy=true;const command=pending;set({kind:'working'});
  return execute(async(lease,signal,current)=>{
   busy=true;
   const now=options.now??(()=>performance.now());
   const token=lease.session.access_token;let r:Awaited<ReturnType<LeaveClient['startDraft']>>;
   if(!recover)r=await options.client.startDraft(token,signal,scope,command);else r={ok:true,value:{operation_id:command.operation_id,status:'unresolved'}};
   if(!current())return;
   if(!r.ok&&terminal(r.error_id)){pending=null;set({kind:failureState(r.error_id)});return;}
   if(!r.ok||r.value.status==='unresolved'){
    const deadline=now()+15000,c=new AbortController(),abort=()=>c.abort();signal.addEventListener('abort',abort,{once:true});
    const timeout=setTimeout(abort,15000);
    const bounded=<T,>(work:Promise<T>):Promise<T>=>Promise.race([work,new Promise<never>((_,reject)=>{if(c.signal.aborted)reject(Error());else c.signal.addEventListener('abort',()=>reject(Error()),{once:true});})]);
    try{
     let retried=false;
     for(let lookups=0;lookups<3&&now()<deadline&&current();lookups++){
      r=await bounded(options.client.draftOutcome(token,c.signal,scope,command.operation_id));
      if(r.ok&&r.value.status==='committed'||!r.ok&&terminal(r.error_id))break;
      if(r.ok&&r.value.status==='unresolved'&&!retried&&now()<deadline){retried=true;r=await bounded(options.client.startDraft(token,c.signal,scope,command));if(r.ok&&r.value.status==='committed'||!r.ok&&terminal(r.error_id))break;}
     }
    }catch{r={ok:false,error_id:'outcome_unresolved'};}finally{clearTimeout(timeout);signal.removeEventListener('abort',abort);c.abort();}
   }
   if(!current())return;
   if(r.ok&&r.value.status==='committed'&&(r.value.result.command!=='start'||r.value.operation_id!==command.operation_id))r={ok:false,error_id:'operation_mismatch'};
   if(r.ok&&r.value.status==='committed'){pending=null;await openWith(lease,signal,current,r.value.result.draft_id,r.value.result.disposition==='created'?r.value.result.revision:undefined);}
   else if(!r.ok&&terminal(r.error_id)){pending=null;set({kind:failureState(r.error_id)});}
   else set({kind:'unresolved'});
   busy=false;
  }).finally(()=>{busy=false;});
 }
 return{load,retryOpen(){set({kind:'loading'});return opening?execute((lease,signal,current)=>openWith(lease,signal,current,opening!.draft,opening!.createdRevision)):load(scope);},resumeOpen(draft:string,result:Awaited<ReturnType<LeaveClient['editorOpen']>>){if(!disposed&&opening?.draft===draft)acceptOpening(result,draft);},apply(){if(pending||busy||context?.status!=='ready'||context.editability.status!=='editable')return Promise.resolve();pending={operation_id:(options.newId??(()=>crypto.randomUUID()))(),expected_scope_generation:context.scope_generation};return start();},retry:()=>start(true),open(draft:string){set({kind:'loading'});return execute((lease,signal,current)=>openWith(lease,signal,current,draft));},close(){clear();pending=null;opening=null;options.navigate?.(null);return load(scope);},dispose(){clear();disposed=true;pending=null;context=null;}};
}
