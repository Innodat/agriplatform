/** Inert explicit original administrator edit recovery; no integration or storage effects.
 * Unresolved and transport failures never prove an in-flight edit cannot commit.
 * Receipts carry no own/admin provenance; current server read.all alone authorizes
 * this executor-private lookup, independently of edit.all or original ownership. */
import type {AdminRecoverEditData,AdminRecoverEditErrors,AdminRecoverEditResponse,CaptureReceipt,Unresolved} from '../../contracts/admin-edit-generated/types.gen';
import type {Session} from './entry';
import {id,token,object,strictJSON,decimal,invalid,InvalidResponse,freeze,type Frozen} from './read-validation.js';
export type PendingAdminRecovery=Readonly<{account_id:string;org_id:string;operation_id:string;capture_id:string;command_type:'capture.edit'}>;
/** Owner pins generation/account/org and aborts on session replacement/disposal.
 * This local publication fence grants no authority; the server rechecks read.all. */
export type AdminRecoveryOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
export type AdminRecoveryError={[S in keyof AdminRecoverEditErrors]:Readonly<{kind:'error';status:S;error_id:AdminRecoverEditErrors[S]['error_id']}>}[keyof AdminRecoverEditErrors];
export type AdminRecoveryResult=Readonly<{kind:'committed';receipt:Frozen<CaptureReceipt>}>|Readonly<{kind:'unresolved';outcome:Frozen<Unresolved>}>|AdminRecoveryError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

function success(value:unknown,pinned:PendingAdminRecovery):AdminRecoveryResult {
 const base=object(value,['operation_id','command_type','status'],['command_version','result']);
 if(base.operation_id!==pinned.operation_id||base.command_type!==pinned.command_type)return invalid();
 if(base.status==='unresolved'){
  object(value,['operation_id','command_type','status']);
  const outcome:AdminRecoverEditResponse={operation_id:pinned.operation_id,command_type:pinned.command_type,status:'unresolved'};
  return {kind:'unresolved',outcome:freeze(outcome)};
 }
 object(value,['operation_id','command_type','status','command_version','result']);
 if(base.status!=='committed'||base.command_version!==1)return invalid();
 const result=object(base.result,['capture_id','revision']);
 if(result.capture_id!==pinned.capture_id||!decimal(result.revision))return invalid();
 // This is the original receipt, including old and no-op revisions. No current
 // snapshot or guessed revision can strengthen or invalidate this acknowledgement.
 const receipt:AdminRecoverEditResponse={operation_id:pinned.operation_id,command_type:pinned.command_type,
  command_version:1,status:'committed',result:{capture_id:pinned.capture_id,revision:result.revision}};
 return {kind:'committed',receipt:freeze(receipt)};
}
function errorResult(status:number,value:unknown):AdminRecoveryError {
 const body=object(value,['error','error_id'],['code']);
 if(typeof body.error!=='string'||(body.code!==undefined&&body.code!==null&&(typeof body.code!=='number'||!Number.isInteger(body.code))))return invalid();
 const e=body.error_id;
 if(status===401&&e==='authentication_required')return {kind:'error',status,error_id:e};
 if(status===403&&e==='access_denied')return {kind:'error',status,error_id:e};
 if(status===409&&e==='identity.actor_setup_required')return {kind:'error',status,error_id:e};
 if(status===422&&e==='validation_failed')return {kind:'error',status,error_id:e};
 if(status===500&&(e==='internal_error'||e==='invalid_write_context'))return {kind:'error',status,error_id:e};
 if(status===503&&(e==='authorization_unavailable'||e==='operation_verification_unavailable'||e==='authorization_observation_expired'||e==='execution_timeout'))return {kind:'error',status,error_id:e};
 return invalid();
}

export async function recoverAdminEdit(session: Session,pending: PendingAdminRecovery,options: AdminRecoveryOptions): Promise<AdminRecoveryResult> {
  const started=performance.now();
  let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
  try {
    object(options,['signal','isCurrent'],['request','timeoutMs']);
    duration=options.timeoutMs===undefined?10000:options.timeoutMs;
    signal=options.signal;isCurrent=options.isCurrent;request=options.request===undefined?fetch:options.request;
    if (!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||
        !Number.isFinite(duration)||duration<=0||duration>10000) return Object.freeze({kind:'invalid_request'});
  } catch {return Object.freeze({kind:'invalid_request'});}
  const current=()=>{try {return isCurrent()===true;} catch {return false;}};
  const deadline=started+duration;
  const finish=(result: AdminRecoveryResult): AdminRecoveryResult => {
    const fresh=current(); // Delegated predicates may synchronously abort the owner.
    return Object.freeze(signal.aborted?{kind:'cancelled'}:
      !fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  };
  if (!current() || signal.aborted || performance.now()>=deadline) return finish({kind:'superseded'});
  // Copy primitives before any await; caller mutation cannot retarget this request.
  let auth:Session,pinned:PendingAdminRecovery;
  try {
    auth={account_id:session?.account_id,access_token:session?.access_token};
    if(!id(auth.account_id)||!token(auth.access_token))return finish({kind:'authentication_required'});
    const snapshot={...pending};
    object(snapshot,['account_id','org_id','operation_id','capture_id','command_type']);
    if(snapshot.account_id!==auth.account_id||!id(snapshot.org_id)||!id(snapshot.operation_id)||!id(snapshot.capture_id)||snapshot.command_type!=='capture.edit')return finish({kind:'invalid_request'});
    pinned={account_id:snapshot.account_id,org_id:snapshot.org_id,operation_id:snapshot.operation_id,capture_id:snapshot.capture_id,command_type:snapshot.command_type};
  } catch {return finish({kind:'invalid_request'});}
  if (!current() || signal.aborted) return finish({kind:'superseded'});
  if (performance.now()>=deadline) return finish({kind:'verification_unavailable'});
  const controller=new AbortController();let body: ReadableStream<Uint8Array>|null|undefined;let reader: ReadableStreamDefaultReader<Uint8Array>|undefined;
  const cancelBody=()=>{try {const work=reader?reader.cancel():body?.cancel();if(work)void work.catch(()=>{});} catch {/* owned transport cancellation is best effort */}};
  let stop!: (result: AdminRecoveryResult)=>void;
  const stopped=new Promise<AdminRecoveryResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<AdminRecoveryResult> => {
    try {
      const data:AdminRecoverEditData={url:'/api/v1/admin/operations/{operation_id}',path:{operation_id:pinned.operation_id},query:{command_type:pinned.command_type}};
      const response=await request(data.url.replace('{operation_id}',data.path.operation_id)+'?command_type='+data.query.command_type,{
        method:'GET',headers:{Authorization:'Bearer '+auth.access_token},
        credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
      body=response.body;
      if (controller.signal.aborted) {cancelBody();return {kind:'cancelled'};}
      const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(v=>v.trim())??[];
      if (response.redirected || !response.body || response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json' || !cache.includes('private') || !cache.includes('no-store') || cache.includes('public')) return invalid();
      reader=response.body.getReader();const chunks: Uint8Array[]=[];let size=0;
      while (true) {
        // Immediate read promises can starve timer tasks, especially on empty
        // chunks. Enforce the same monotonic deadline inside the read loop.
        if (!current() || signal.aborted || performance.now()>=deadline) return finish({kind:'verification_unavailable'});
        const chunk=await reader.read();
        if (!current() || signal.aborted || performance.now()>=deadline) return finish({kind:'verification_unavailable'});
        if (chunk.done) break;
        if (!chunk.value.byteLength) continue;
        if (size+chunk.value.byteLength>16384) return invalid();
        size+=chunk.value.byteLength;chunks.push(chunk.value);
      }
      const bytes=new Uint8Array(size);let offset=0;for (const chunk of chunks) {bytes.set(chunk,offset);offset+=chunk.byteLength;}
      let value: unknown;
      try {value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));} catch {return invalid();}
      return response.status===200?success(value,pinned):errorResult(response.status,value);
    } catch (error) {return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
  };
  try {return finish(await Promise.race([work(),stopped]));}
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
