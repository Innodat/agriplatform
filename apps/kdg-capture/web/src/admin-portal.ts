/** App-owned online review. No startup wiring, persistence, own-read fallback or write ports. */
import {createSessionLifecycle,type AuthPort,type Session,type EntryState,type Boundary} from './auth/lifecycle.js';
import {adminHistoryCaptures} from './admin-history.js';
import {readAdminCapture} from './admin-detail.js';
import {auditDetails} from './audit-display.js';
import {auditPresentation,type AuditPresentation,type AuditActorLabel} from './audit-presentation.js';
import type {CaptureDetail} from '../../contracts/admin-generated/types.gen';
import type {AuditPage} from '../../contracts/audit-display-generated/types.gen';
import {freeze,type Frozen} from './read-validation.js';

type HistoryView={kind:'history';rows:{capture:Frozen<CaptureDetail>;capturer:Frozen<AuditActorLabel>}[];next_cursor:string|null;returnFocus:string|null};
type DetailView={kind:'detail';capture:Frozen<CaptureDetail>;audit:Frozen<AuditPresentation>;auditExpanded:boolean};
type Failure='denied'|'signed_out'|'unavailable';
export type PortalState=Frozen<HistoryView|DetailView|{kind:Failure|'checking'|'loading'|'offline'|'closed'}>;
export type AdminPortalOptions=Readonly<{auth:AuthPort;org_id:string;from_date:string;to_date:string;beginSignIn:()=>Promise<void>;request?:typeof fetch;timeoutMs?:number;online?:boolean}>;
type Execution={session:Session;org:string;signal:AbortSignal;isCurrent:()=>boolean;deadline:number};
// The one-use result is consumed only after the generic lifecycle accepts the returned
// outcome. Owner callbacks cannot publish admission. Clearing drops unconsumed data.
type Admission={account_id:string;org_id:string;take:()=>Frozen<HistoryView>|null};
class ReadFailure {constructor(readonly kind:Failure){}}
function reject(result:{kind:string;status?:number}):never {
 throw new ReadFailure(result.kind==='authentication_required'||result.status===401?'signed_out':result.status===403?'denied':'unavailable');
}
function remaining(execution:Execution):number {
 const value=execution.deadline-performance.now();
 if(value<=0||execution.signal.aborted||!execution.isCurrent())throw new ReadFailure('unavailable');
 return value;
}
function sameCapture(detail:Frozen<CaptureDetail>,audit:Frozen<AuditPage>,latest:boolean):boolean {
 return detail.capture_id===audit.capture_id&&detail.org_id===audit.org_id&&detail.owner_account_id===audit.owner_account_id&&
  detail.owner_actor_id===audit.owner_actor_id&&detail.created_by===audit.created_by&&detail.created_at===audit.created_at&&
  (!latest||(detail.revision===audit.current_revision&&detail.updated_by===audit.updated_by&&detail.updated_at===audit.updated_at));
}

export function createAdminPortal(options:AdminPortalOptions){
 const {auth,beginSignIn}=options,request=options.request??fetch,duration=options.timeoutMs??10000;
 if(!Number.isFinite(duration)||duration<=0||duration>10000)throw new Error('portal_configuration_invalid');
 let org=options.org_id,from=options.from_date,to=options.to_date,connected=options.online!==false;
 let state:PortalState=freeze({kind:connected?'checking':'offline'}),epoch=0,disposed=false,started=false;
 // Local signout intent outlives a generic lifecycle and pending provider work.
 // Only deliberate reentry clears it; logout completions never mutate this fence.
 let signoutFenced=false;
 let active:AbortController|undefined,historyCursor:string|undefined,selected:string|null=null,expanded=false;
 let intent:'history'|'detail'='history',auditCursor:string|undefined;
 const listeners=new Set<()=>void>();
 const publish=(next:PortalState)=>{state=freeze(next);for(const listener of [...listeners])listener();};
 function clear(kind:'checking'|'loading'|'offline'|'closed'='checking'){
  epoch++;const old=active;active=undefined;old?.abort();publish({kind:signoutFenced&&(kind==='checking'||kind==='loading')?'signed_out':kind});
 }
 async function audit(execution:Execution,capture_id:string,limit:number,cursor?:string){
  const result=await auditDetails(execution.session,{account_id:execution.session.account_id,org_id:execution.org,capture_id,limit,...(cursor?{cursor}:{})},
   {signal:execution.signal,isCurrent:execution.isCurrent,request,timeoutMs:remaining(execution)});
  remaining(execution);if(result.kind!=='loaded')return reject(result);return result;
 }
 async function history(execution:Execution,cursor?:string,returnFocus:string|null=null):Promise<Frozen<HistoryView>>{
  const page=await adminHistoryCaptures(execution.session,{account_id:execution.session.account_id,org_id:execution.org,from_date:from,to_date:to,limit:5,...(cursor?{cursor}:{})},
   {signal:execution.signal,isCurrent:execution.isCurrent,request,timeoutMs:remaining(execution)});
  remaining(execution);if(page.kind!=='loaded')return reject(page);
  const rows:HistoryView['rows']=[];
  // At most five authorized IDs, one request per row, all on the original deadline.
  for(const capture of page.page.items){
   const loaded=await audit(execution,capture.capture_id,1);
   if(!sameCapture(capture,loaded.page.audit,false))throw new ReadFailure('unavailable');
   const projection=auditPresentation(loaded);if(projection.kind!=='loaded')return reject(projection);
   rows.push({capture,capturer:projection.model.original_capturer});
  }
  remaining(execution);return freeze({kind:'history',rows,next_cursor:page.page.next_cursor,returnFocus});
 }
 async function detail(execution:Execution,capture_id:string,cursor?:string):Promise<Frozen<DetailView>>{
  const loaded=await readAdminCapture(execution.session,{account_id:execution.session.account_id,org_id:execution.org,capture_id},
   {signal:execution.signal,isCurrent:execution.isCurrent,request,timeoutMs:remaining(execution)});
  remaining(execution);if(loaded.kind!=='loaded')return reject(loaded);
  const events=await audit(execution,capture_id,5,cursor);
  if(!sameCapture(loaded.snapshot,events.page.audit,true))throw new ReadFailure('unavailable');
  const projection=auditPresentation(events);if(projection.kind!=='loaded')return reject(projection);
  remaining(execution);return freeze({kind:'detail',capture:loaded.snapshot,audit:projection.model,auditExpanded:expanded});
 }
 function boundary():Boundary<Admission>{
  let generation=0,controller:AbortController|undefined,pending:Frozen<HistoryView>|null=null;
  const reset=()=>{generation++;controller?.abort();controller=undefined;pending=null;clear(connected?'checking':'offline');};
  return {
   async check(session){
    reset();const execution=generation,pinnedOrg=org;
    if(!session||signoutFenced)return {kind:'signed_out'};
    controller=new AbortController();const signal=controller.signal;
    try{
     const view=await history({session:{...session},org:pinnedOrg,signal,isCurrent:()=>!disposed&&generation===execution&&connected,deadline:performance.now()+duration});
     if(disposed||generation!==execution||signal.aborted)return {kind:'superseded'};
     pending=view;
     return {kind:'authorized',context:{account_id:session.account_id,org_id:pinnedOrg,take(){const result=pending;pending=null;return generation===execution?result:null;}}};
    }catch(error){
     if(disposed||generation!==execution||signal.aborted)return {kind:'superseded'};
     const kind=error instanceof ReadFailure?error.kind:'unavailable';
     return {kind:kind==='denied'?'access_denied':kind==='signed_out'?'authentication_required':'authorization_unavailable'};
    }finally{if(generation===execution){controller?.abort();controller=undefined;}}
   },clear:reset,dispose:reset,
  };
 }
 function admitted(next:EntryState<Admission>){
  if(disposed||!connected)return;
  if(signoutFenced){publish({kind:'signed_out'});return;}
  if(next.kind==='authorized'){
   const view=next.context.take();if(!view||next.context.org_id!==org){publish({kind:'unavailable'});return;}
   historyCursor=undefined;selected=null;intent='history';auditCursor=undefined;expanded=false;publish(view);
  }else publish({kind:next.kind==='checking'?'checking':next.kind==='access_denied'?'denied':next.kind==='signed_out'||next.kind==='authentication_required'?'signed_out':'unavailable'});
 }
 const makeLifecycle=()=>createSessionLifecycle<Admission>({auth,beginSignIn,createBoundary:boundary,publish:admitted,timeoutMs:duration,online:connected});
 let lifecycle=makeLifecycle();
 async function fresh(){
  if(disposed)return;
  lifecycle.dispose();historyCursor=undefined;selected=null;intent='history';auditCursor=undefined;expanded=false;
  if(!connected){publish({kind:'offline'});return;}
  if(signoutFenced){publish({kind:'signed_out'});return;}
  lifecycle=makeLifecycle();started=true;await lifecycle.start();
 }
 async function read(returnFocus:string|null=null){
  if(disposed||!connected)return;
  if(signoutFenced){publish({kind:'signed_out'});return;}
  clear('loading');const execution=epoch,lease=lifecycle.acquireExecution();
  if(!lease){publish({kind:'signed_out'});return;}
  const controller=new AbortController();active=controller;
  const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});
  const current=()=>!disposed&&connected&&epoch===execution&&lease.isCurrent()&&!controller.signal.aborted;
  const context:Execution={session:lease.session,org:lease.context.org_id,signal:controller.signal,isCurrent:current,deadline:performance.now()+duration};
  const pinnedIntent=intent,pinnedCapture=selected,pinnedHistoryCursor=historyCursor,pinnedAuditCursor=auditCursor;
  try{
   const view=pinnedIntent==='detail'&&pinnedCapture?await detail(context,pinnedCapture,pinnedAuditCursor):await history(context,pinnedHistoryCursor,returnFocus);
   if(current())publish(view);
  }catch(error){if(current())publish({kind:error instanceof ReadFailure?error.kind:'unavailable'});}
  finally{lease.signal.removeEventListener('abort',abort);lease.release();controller.abort();if(active===controller)active=undefined;}
 }
 return {
  snapshot:()=>state,
  subscribe(listener:()=>void){listeners.add(listener);return()=>{listeners.delete(listener);};},
  async start(){if(disposed||started||!connected)return;started=true;await lifecycle.start();},
  refresh:fresh,
  async retry(){if(disposed||!connected)return;if(signoutFenced){signoutFenced=false;return fresh();}const lease=lifecycle.acquireExecution();const admitted=lease!==null;lease?.release();if(state.kind==='denied'||state.kind==='signed_out'||!admitted)return fresh();await read();},
  async select(capture_id:string){if(state.kind!=='history'||!state.rows.some(row=>row.capture.capture_id===capture_id))return;selected=capture_id;intent='detail';expanded=false;auditCursor=undefined;await read();},
  async back(){if(intent!=='detail')return;const target=selected;intent='history';auditCursor=undefined;expanded=false;await read(target);},
  async nextHistory(){if(state.kind!=='history'||!state.next_cursor)return;historyCursor=state.next_cursor;await read();},
  async firstHistory(){intent='history';historyCursor=undefined;await read();},
  async auditPage(cursor:string){if(state.kind!=='detail')return;expanded=true;auditCursor=cursor;await read();},
  toggleAudit(){if(state.kind==='detail'){expanded=!state.auditExpanded;publish({...state,auditExpanded:expanded});}},
  async dates(from_date:string,to_date:string){from=from_date;to=to_date;await fresh();},
  async online(value:boolean){if(disposed||connected===value)return;connected=value;await fresh();},
  async replaceOrganization(value:string){org=value;await fresh();},
  async signIn(){if(disposed||!connected)return;if(signoutFenced){signoutFenced=false;await fresh();if(disposed||signoutFenced||state.kind!=='signed_out')return;}await lifecycle.signIn();},
  async signOut(){if(disposed)return;signoutFenced=true;clear();await lifecycle.signOut();},
  dispose(){if(disposed)return;disposed=true;lifecycle.dispose();clear('closed');listeners.clear();},
 };
}
export type AdminPortalController=ReturnType<typeof createAdminPortal>;
