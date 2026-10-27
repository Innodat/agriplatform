/** Explicit online metadata read only; no admission, cache, UI or retry effects. */
import type {AuditPage,AuditEventsData,AuditEventsErrors} from '../../contracts/audit-generated/types.gen';
import type {Session} from './entry';
import {id,token,object,strictJSON,decimal,instant,freeze,errorResult,InvalidResponse,invalid,type Frozen} from './read-validation.js';

export type PendingAudit=Readonly<{account_id:string;org_id:string;capture_id:string;limit?:number;cursor?:string}>;
export type AuditOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
export type AuditError={[S in keyof AuditEventsErrors]:Readonly<{kind:'error';status:S;error_id:AuditEventsErrors[S]['error_id']}>}[keyof AuditEventsErrors];
export type AuditResult=Readonly<{kind:'loaded';page:Frozen<AuditPage>}>|AuditError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;
type Pinned=PendingAudit & {limit:number};
const permission='kdg_capture.capture.read.all';
const cursorKeys=['account_id','capture_id','last_revision','limit','org_id','permission','v'];

function cursor(raw:unknown,pinned:Pinned):Record<string,unknown> {
 if(typeof raw!=='string'||raw.length<1||raw.length>2048||!/^[A-Za-z0-9_-]+$/.test(raw))return invalid();
 try{
  const value=object(strictJSON(atob(raw.replaceAll('-','+').replaceAll('_','/')+'='.repeat((4-raw.length%4)%4))),cursorKeys);
  const canonical=JSON.stringify(Object.fromEntries(Object.keys(value).sort().map(key=>[key,value[key]])));
  const encoded=btoa(canonical).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
  if(encoded!==raw||value.v!==1||value.permission!==permission||value.account_id!==pinned.account_id||value.org_id!==pinned.org_id||value.capture_id!==pinned.capture_id||value.limit!==pinned.limit||!decimal(value.last_revision))return invalid();
  return value;
 }catch{return invalid();}
}

function pin(value:PendingAudit):Pinned {
 // The private copy is the only request/validation context used after awaits.
 const captured={...value};object(captured,['account_id','org_id','capture_id'],['limit','cursor']);
 if(Object.hasOwn(captured,'limit')&&captured.limit===undefined)return invalid();
 const pinned={...captured,limit:captured.limit===undefined?30:captured.limit};
 if(!id(pinned.account_id)||!id(pinned.org_id)||!id(pinned.capture_id)||!Number.isInteger(pinned.limit)||pinned.limit<1||pinned.limit>100)return invalid();
 if(Object.hasOwn(captured,'cursor'))cursor(pinned.cursor,pinned);
 return pinned;
}

function validatePage(value:unknown,pinned:Pinned):Frozen<AuditPage> {
 const page=object(value,['account_id','org_id','capture_id','owner_account_id','owner_actor_id','created_by','created_at','updated_by','updated_at','current_revision','limit','events','next_cursor']);
 if(page.account_id!==pinned.account_id||page.org_id!==pinned.org_id||page.capture_id!==pinned.capture_id||page.limit!==pinned.limit)return invalid();
 for(const key of ['owner_account_id','owner_actor_id','created_by','updated_by'])if(!id(page[key]))return invalid();
 if(page.created_by!==page.owner_actor_id||!decimal(page.current_revision)||!instant(page.created_at)||!instant(page.updated_at)||!Array.isArray(page.events)||page.events.length>pinned.limit)return invalid();
 const current=BigInt(page.current_revision);
 let previous=pinned.cursor?BigInt(cursor(pinned.cursor,pinned).last_revision as string):current+1n;
 let last:string|undefined;
 for(const raw of page.events){
  const event=object(raw,['revision','command_type','executor_actor_id','initiator_actor_id','recorded_at']);
  if(!decimal(event.revision)||!id(event.executor_actor_id)||(event.initiator_actor_id!==null&&!id(event.initiator_actor_id))||!instant(event.recorded_at))return invalid();
  const revision=BigInt(event.revision);
  if(revision>current||revision>=previous||event.command_type!==(revision===1n?'capture.create':'capture.edit')||
   (revision===1n&&event.executor_actor_id!==page.owner_actor_id)||(revision===current&&event.executor_actor_id!==page.updated_by))return invalid();
  previous=revision;last=event.revision;
 }
 if(!pinned.cursor&&(!page.events.length||page.events[0].revision!==page.current_revision))return invalid();
 if(page.next_cursor!==null){
  const next=cursor(page.next_cursor,pinned);
  // Audit uses limit+1 lookahead without byte trimming; continuation requires
  // a full included page with a possible earlier positive revision. This says
  // nothing about contiguous revision history.
  if(page.events.length!==pinned.limit||last===undefined||last==='1'||next.last_revision!==last)return invalid();
 }
 // Timestamps are independent statement times; gaps in revision history are legal.
 return freeze(value as AuditPage);
}

export async function auditEvents(session:Session,pending:PendingAudit,options:AuditOptions):Promise<AuditResult> {
 let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
 try{
  object(options,['signal','isCurrent'],['request','timeoutMs']);
  duration=options.timeoutMs===undefined?10000:options.timeoutMs;signal=options.signal;isCurrent=options.isCurrent;request=options.request===undefined?fetch:options.request;
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const deadline=performance.now()+duration;
 const current=()=>{try{return isCurrent()===true;}catch{return false;}};
 const finish=(result:AuditResult):AuditResult=>{
  const fresh=current(); // A caller predicate can synchronously abort or consume time.
  return Object.freeze(signal.aborted?{kind:'cancelled'}:!fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
 };
 let auth:Session,pinned:Pinned;
 try{
  auth={account_id:session?.account_id,access_token:session?.access_token};
  if(!id(auth.account_id)||!token(auth.access_token))return finish({kind:'authentication_required'});
  pinned=pin(pending);
  if(pinned.account_id!==auth.account_id)return finish({kind:'invalid_request'});
 }catch{return finish({kind:'invalid_request'});}
 if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'superseded'});
 const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,body:ReadableStream<Uint8Array>|null|undefined;
 const cancelBody=()=>{try{const work=reader?reader.cancel():body?.cancel();if(work)void work.catch(()=>{});}catch{/* best effort for an owned transport */}};
 let stop!:(result:AuditResult)=>void;const stopped=new Promise<AuditResult>(resolve=>{stop=resolve;});
 const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};signal.addEventListener('abort',cancel,{once:true});
 const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<AuditResult>=>{
  try{
   const data:AuditEventsData={url:'/api/v1/admin/captures/{capture_id}/events',path:{capture_id:pinned.capture_id},query:{limit:pinned.limit,...(pinned.cursor?{cursor:pinned.cursor}:{})}};
   const query=new URLSearchParams(Object.entries(data.query!).map(([key,value])=>[key,String(value)]));
   const response=await request(data.url.replace('{capture_id}',data.path.capture_id)+'?'+query,{method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
   body=response.body;
   if(controller.signal.aborted){cancelBody();return {kind:'cancelled'};}
   const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(value=>value.trim())??[];
   if(response.redirected||!body||response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json'||!cache.includes('private')||!cache.includes('no-store')||cache.includes('public'))return invalid();
   reader=body.getReader();const chunks:Uint8Array[]=[];let size=0;
   while(true){
    // Immediate empty read promises can starve timer tasks; check the original
    // monotonic deadline on both sides of every read as well as at publication.
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    const chunk=await reader.read();
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    if(chunk.done)break;if(!chunk.value.byteLength)continue;
    size+=chunk.value.byteLength;if(size>65536)return invalid();chunks.push(chunk.value);
   }
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   let value:unknown;try{value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{return invalid();}
   return response.status===200?{kind:'loaded',page:validatePage(value,pinned)}:errorResult(response.status,value);
  }catch(error){return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
 };
 try{return finish(await Promise.race([work(),stopped]));}
 finally{clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
