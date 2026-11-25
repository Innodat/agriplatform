import type {ExecutionLease} from './auth/lifecycle.ts';
import type {DraftRead,LeaveClient,SaveDraft,DiscardDraft,DraftOutcome,Result} from './api/leave.ts';
import {isDraftInput,type DraftInput} from './draft-input.ts';
export type InputProblem={path:string;message:string};
export function inputProblems(input:DraftInput):InputProblem[]{
 const result:InputProblem[]=[];
 for(const [path,value,max] of [['full_days.start',input.full_days.start.text,64],['full_days.end',input.full_days.end.text,64],['half_day.date',input.half_day.date.text,64],['hours.date',input.hours.date.text,64],['hours.duration',input.hours.duration.text,32],['note',input.note,4000]] as const){
  if(Array.from(value).length>max)result.push({path,message:`Use at most ${max.toLocaleString('en')} characters. Your input has not been shortened.`});
  else if(/[\u0000\uD800-\uDFFF]/u.test(value))result.push({path,message:'Remove unsupported characters before this input can be saved.'});
 }
 if(!result.length&&!isDraftInput(input))result.push({path:'input',message:'This input cannot be saved in the supported format.'});
 return result;
}
type ActiveDraft=Extract<DraftRead,{state:'active'}>;
export type EditorStatus='saved'|'dirty'|'saving'|'failed'|'conflict'|'closed'|'read_only'|'setup_required'|'auth_required'|'denied';
export type DraftDiscardState='none'|'confirm'|'running'|'save_retry'|'discard_retry'|'complete';
export type EditorState={input:DraftInput|null;revision:string;generation:number;status:EditorStatus;exit:'none'|'waiting'|'confirm'|'closed';discard:DraftDiscardState;discardFailed:boolean;problems:InputProblem[];reviewing:boolean;reviewFailed:boolean;reason?:string};
type Timer=ReturnType<typeof setTimeout>;
type Clock={now:()=>number;setTimeout:(f:()=>void,ms:number)=>Timer;clearTimeout:(id:Timer)=>void};
const same=(a:DraftInput,b:DraftInput)=>JSON.stringify(a)===JSON.stringify(b);
function frozen<T>(value:T):T{if(value&&typeof value==='object'){for(const child of Object.values(value))frozen(child);Object.freeze(value);}return value;}
/** One mounted scoped editor owns this sequence; nothing here is browser-persistent. */
export function createDraftEditorController(options:{org:string;initial:ActiveDraft;client:Pick<LeaveClient,'saveDraft'|'discardDraft'|'draftOutcome'|'readDraft'>;acquire:()=>ExecutionLease<unknown>|null;publish:(state:EditorState)=>void;newId?:()=>string;clock?:Clock}){
 const clock=options.clock??{now:()=>performance.now(),setTimeout:(f,ms)=>setTimeout(f,ms),clearTimeout:id=>clearTimeout(id)};
 const editorLease=options.acquire(),account=editorLease?.session.account_id;editorLease?.release();
 let state:EditorState={input:structuredClone(options.initial.input),revision:options.initial.revision,generation:0,status:options.initial.editability.status==='editable'?'saved':'read_only',exit:'none',discard:'none',discardFailed:false,problems:[],reviewing:false,reviewFailed:false,reason:options.initial.editability.status==='read_only'?options.initial.editability.reason:undefined};
 let acknowledged=structuredClone(options.initial.input),pending:SaveDraft|null=null,pendingDiscard:DiscardDraft|null=null,disposed=false,epoch=0,active:AbortController|null=null,timer:Timer|undefined,firstDirty:number|null=null,lastEdit=0,running:Promise<void>|null=null;
 let renewedRevision:string|undefined;
 const publish=()=>{if(!disposed)options.publish({...state});};
 const writable=()=>['saved','dirty','saving','failed'].includes(state.status)&&state.input!==null;
 const discardPaused=()=>state.discard!=='none'&&state.discard!=='confirm';
 const newId=()=>options.newId?.()??crypto.randomUUID();
 const clearTimer=()=>{if(timer!==undefined)clock.clearTimeout(timer);timer=undefined;};
 const updateStatus=()=>{if(!state.input)return;state.status=pending?'saving':same(state.input,acknowledged)?'saved':'dirty';};
 const failExit=()=>{if(state.exit==='waiting')state.exit='confirm';};
 function schedule(){
  clearTimer();if(disposed||discardPaused()||running||pending||!writable()||state.status==='failed'||!state.input||same(state.input,acknowledged))return;
  const due=state.exit==='waiting'?0:Math.max(0,Math.min(lastEdit+1000,(firstDirty??lastEdit)+5000)-clock.now());
  timer=clock.setTimeout(()=>{timer=undefined;void flush();},due);
 }
 function terminal(error:string):boolean{return ['authentication_required','access_denied','identity.verification_required','resource_not_found','leave.draft_revision_conflict','leave.draft_discarded','leave.draft_submitted','leave.draft_read_only','leave.setup_required','operation_mismatch','validation_failed','request_too_large'].includes(error);}
 function stop(error:string){
  if(error!=='authentication_required'){pending=null;renewedRevision=undefined;}
  clearTimer();state.status=error==='authentication_required'?'auth_required':error==='access_denied'||error==='identity.verification_required'||error==='resource_not_found'?'denied':error==='leave.draft_discarded'||error==='leave.draft_submitted'?'closed':error==='leave.draft_read_only'?'read_only':error==='leave.setup_required'?'setup_required':error==='validation_failed'||error==='request_too_large'?'failed':'conflict';
  if(!writable()){if(state.discard==='complete')state.exit='none';state.discard='none';if(error!=='authentication_required')pendingDiscard=null;}
  if(state.status==='denied'){state.input=null;acknowledged=options.initial.input;}failExit();
 }
 async function scoped(work:(token:string,signal:AbortSignal,current:()=>boolean)=>Promise<void>){
  const mine=++epoch,lease=options.acquire();if(!lease){stop('authentication_required');publish();return;}
  if(account!==undefined&&lease.session.account_id!==account){lease.release();return;}
  const controller=new AbortController();active=controller;const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});if(lease.signal.aborted)abort();
  const current=()=>!disposed&&mine===epoch&&!controller.signal.aborted&&lease.isCurrent();
  try{await work(lease.session.access_token,controller.signal,current);}finally{lease.signal.removeEventListener('abort',abort);controller.abort();lease.release();if(active===controller)active=null;}
 }
 async function bounded<T>(work:(signal:AbortSignal)=>Promise<T>,signal:AbortSignal,ms:number):Promise<T>{
  if(ms<=0||signal.aborted)throw Error('deadline');
  const controller=new AbortController();const abort=()=>controller.abort();signal.addEventListener('abort',abort,{once:true});
  let cancel:()=>void=()=>{};const timeout=clock.setTimeout(abort,ms);
  try{return await Promise.race([work(controller.signal),new Promise<never>((_,reject)=>{cancel=()=>reject(Error('deadline'));controller.signal.addEventListener('abort',cancel,{once:true});})]);}
  finally{clock.clearTimeout(timeout);signal.removeEventListener('abort',abort);controller.signal.removeEventListener('abort',cancel);controller.abort();}
 }
 async function resolveMutation(operation:string,recover:boolean,token:string,signal:AbortSignal,current:()=>boolean,write:(signal:AbortSignal)=>Promise<Result<DraftOutcome>>){
  let response:Result<DraftOutcome>={ok:false,error_id:'outcome_unresolved'};
  const send=(limit:number)=>bounded(write,signal,limit).catch(()=>({ok:false,error_id:'outcome_unresolved'} as const));
  if(!recover)response=await send(12000);
  if(!current())return response;
  if(!response.ok&&!terminal(response.error_id)||response.ok&&response.value.status==='unresolved'){
   const deadline=clock.now()+15000;let retried=false;
   for(let lookups=0;lookups<3&&clock.now()<deadline&&current();lookups++){
    try{response=await bounded(s=>options.client.draftOutcome(token,s,options.org,operation),signal,Math.min(10000,deadline-clock.now()));}catch{response={ok:false,error_id:'outcome_unresolved'};}
    if(!current()||response.ok&&response.value.status==='committed'||!response.ok&&terminal(response.error_id))break;
    if(response.ok&&response.value.status==='unresolved'&&!retried&&clock.now()<deadline){
     retried=true;response=await send(Math.min(12000,deadline-clock.now()));
     if(response.ok&&response.value.status==='committed'||!response.ok&&terminal(response.error_id))break;
    }
   }
  }
  return response;
 }
 function matches(command:DiscardDraft,value:Extract<DraftOutcome,{status:'committed'}>,kind:'save'|'discard'){
  const result=value.result;
  return value.operation_id===command.operation_id&&result.command===kind&&result.draft_id===options.initial.draft_id
   &&result.disposition===(kind==='save'?'saved':'discarded')&&/^[1-9][0-9]*$/.test(result.revision)
   &&BigInt(result.revision)===BigInt(command.expected_revision)+1n;
 }
 async function sequence(recover:boolean){
  const command=pending!;state.status='saving';publish();
  await scoped(async(token,signal,current)=>{
   const response=await resolveMutation(command.operation_id,recover,token,signal,current,s=>options.client.saveDraft(token,s,options.org,options.initial.draft_id,command));
   if(!current())return;
   if(response.ok&&response.value.status==='committed'){
    const value=response.value;
    if(!matches(command,value,'save')){stop('operation_mismatch');}
    else if(renewedRevision&&BigInt(renewedRevision)>BigInt(value.result.revision))stop('leave.draft_revision_conflict');
    else{acknowledged=structuredClone(command.input);state.revision=value.result.revision;pending=null;renewedRevision=undefined;updateStatus();if(state.status==='saved')firstDirty=null;}
   }else if(!response.ok&&terminal(response.error_id))stop(response.error_id);
   else{state.status='failed';failExit();}
   if(state.exit==='waiting'&&state.status==='saved')state.exit='closed';publish();
  });
 }
 function run(recover:boolean):Promise<void>{
  if(running)return running;
  running=sequence(recover).catch(()=>{if(!disposed&&state.status==='saving'){state.status='failed';failExit();publish();}}).finally(()=>{running=null;if(!disposed&&!discardPaused()&&state.status==='dirty'&&(state.exit==='waiting'||clock.now()>=Math.min(lastEdit+1000,(firstDirty??lastEdit)+5000)))void flush();else schedule();});
  return running;
 }
 function flush():Promise<void>{
  clearTimer();if(discardPaused())return Promise.resolve();if(running)return running;
  if(!pending&&(!state.input||same(state.input,acknowledged))){if(state.exit==='waiting')state.exit='closed';publish();return Promise.resolve();}
  if(!writable()||state.status==='failed'){failExit();publish();return Promise.resolve();}
  if(!state.input||same(state.input,acknowledged)){state.status='saved';if(state.exit==='waiting')state.exit='closed';publish();return Promise.resolve();}
  state.problems=inputProblems(state.input);
  const command:SaveDraft={operation_id:newId(),expected_revision:state.revision,input:structuredClone(state.input)};
  if(!state.problems.length&&new TextEncoder().encode(JSON.stringify(command)).length>32768)state.problems=[{path:'input',message:'This application is too large to save. Shorten your input.'}];
  if(state.problems.length){state.status='failed';failExit();publish();return Promise.resolve();}
  pending=frozen(command);return run(false);
 }
 async function proceedDiscard(){
  if(running)await running;
  else if(pending)await run(true);
  if(disposed||state.discard!=='running')return;
  if(pending){state.discard='save_retry';publish();return;}
  if(!writable()){state.discard='none';publish();return;}
  await sendDiscard(false);
 }
 async function sendDiscard(recover:boolean){
  const command=pendingDiscard??=Object.freeze({operation_id:newId(),expected_revision:state.revision});
  await scoped(async(token,signal,current)=>{
   const response=await resolveMutation(command.operation_id,recover,token,signal,current,s=>options.client.discardDraft(token,s,options.org,options.initial.draft_id,command));
   if(!current())return;
   if(response.ok&&response.value.status==='committed'){
    if(!matches(command,response.value,'discard')){stop('operation_mismatch');}
    else completeDiscard();
   }else if(!response.ok&&terminal(response.error_id)){
    if(response.error_id!=='authentication_required')pendingDiscard=null;state.discard='none';
    if(response.error_id==='validation_failed'||response.error_id==='request_too_large'){
     state.discardFailed=true;schedule();
    }else stop(response.error_id);
   }else state.discard='discard_retry';
   publish();
  });
 }
 function completeDiscard(){
  pendingDiscard=null;state.input=null;state.discard='complete';state.exit='closed';
 }
 publish();
 return{
  snapshot:()=>({...state}),
  hasRenewedPendingSave:()=>renewedRevision!==undefined,
  async resumeAfterAuth(value:DraftRead){
   if(running)await running;
   if(disposed||state.status!=='auth_required')return;
   state.exit='none';
   if(value.state==='discarded'){
    const original=pendingDiscard;
    stop('leave.draft_discarded');state.input=null;state.reason='closure_unattributed';publish();
    if(!original)return;
    // The current closed row does not identify the command that closed it.
    // Recover only the original confirmed operation's receipt.
    await scoped(async(token,signal,current)=>{
     const response=await bounded(s=>options.client.draftOutcome(token,s,options.org,original.operation_id),signal,10000).catch(()=>null);
     if(!current()||!response?.ok||response.value.status!=='committed'||response.value.result.revision!==value.revision||!matches(original,response.value,'discard'))return;
     completeDiscard();publish();
    });
    return;
   }else if(value.editability.status==='read_only'){
    stop('leave.draft_read_only');state.reason=value.editability.reason;
    state.input=structuredClone(value.input);acknowledged=structuredClone(value.input);
    state.revision=value.revision;state.generation++;state.problems=[];
   }else if(pending){
    renewedRevision=value.revision;
    await run(true);return;
   }else if(pendingDiscard){
    updateStatus();state.discard='discard_retry';
   }else if(value.revision!==state.revision&&state.input&&!same(state.input,acknowledged)){
    stop('leave.draft_revision_conflict');
   }else{
    const clean=state.input&&same(state.input,acknowledged);
    acknowledged=structuredClone(value.input);state.revision=value.revision;
    if(clean){state.input=structuredClone(value.input);state.generation++;}
    updateStatus();schedule();
   }
   publish();
  },
  protectedFailure(error:string){if(disposed)return;epoch++;active?.abort();stop(error);publish();},
  change(input:DraftInput){if(disposed||discardPaused()||!writable())return;state.input=structuredClone(input);state.generation++;lastEdit=clock.now();firstDirty??=lastEdit;state.problems=[];if(state.status!=='failed'||!pending)updateStatus();if(!pending&&same(state.input,acknowledged))firstDirty=null;publish();schedule();},
  async retry(){if(disposed||discardPaused()||state.status!=='failed'||running)return;if(pending)await run(true);else{updateStatus();await flush();}},
  async close(){if(disposed||state.discard!=='none'||state.exit==='closed')return;state.exit='waiting';publish();await flush();while(running&&state.exit==='waiting')await running;if(state.exit==='waiting')await flush();},
  stay(){if(state.exit==='confirm'){state.exit='none';publish();}},
  closeAnyway(){state.exit='closed';publish();},
  requestDiscard(){if(disposed||state.exit!=='none'||state.discard!=='none'||!writable())return;state.discardFailed=false;state.discard='confirm';publish();},
  cancelDiscard(){
   if(state.discard!=='confirm'&&state.discard!=='save_retry')return;
   state.discard='none';publish();schedule();
  },
  async confirmDiscard(){
   if(disposed||state.discard!=='confirm'||!writable())return;
   state.discard='running';clearTimer();publish();
   await proceedDiscard();
  },
  async retryDiscard(){
   if(disposed)return;
   const retry=state.discard;
   if(retry!=='save_retry'&&retry!=='discard_retry')return;
   state.discard='running';publish();
   if(retry==='save_retry')await proceedDiscard();
   else await sendDiscard(true);
  },
  async review(){
   if(disposed||running||state.reviewing||!['conflict','read_only','setup_required','auth_required'].includes(state.status))return;
   state.reviewing=true;state.reviewFailed=false;publish();
   try{await scoped(async(token,signal,current)=>{try{const response=await bounded(s=>options.client.readDraft(token,s,options.org,options.initial.draft_id),signal,10000);if(!current())return;
    if(!response.ok){if(['authentication_required','access_denied','identity.verification_required','resource_not_found'].includes(response.error_id))stop(response.error_id);else state.reviewFailed=true;}
    else if(response.value.org_id!==options.org||response.value.draft_id!==options.initial.draft_id)state.reviewFailed=true;
    else if(response.value.state==='discarded')stop('leave.draft_discarded');
    else{const value=response.value;pending=null;state.input=structuredClone(value.input);acknowledged=structuredClone(value.input);state.revision=value.revision;state.generation++;state.status=value.editability.status==='editable'?'saved':'read_only';state.reason=value.editability.status==='read_only'?value.editability.reason:undefined;firstDirty=null;state.problems=[];}
   }catch{if(current())state.reviewFailed=true;}});}finally{state.reviewing=false;publish();}
  },
  dispose(){disposed=true;epoch++;clearTimer();active?.abort();pending=null;pendingDiscard=null;},
 };
}
