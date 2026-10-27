/** Inert explicit administrator edit request; no Auth, UI, queue or storage effects.
 * After dispatch an unavailable/cancelled outcome may still commit. Preserve the
 * original operation and input; this adapter never retries or claims rollback. */
import type {AdminEditCaptureData,AdminEditCaptureErrors,AdminEditCaptureResponse,EditCommand} from '../../contracts/admin-edit-generated/types.gen';
import type {Session} from './entry';
import {id,token,object,strictJSON,decimal,invalid,InvalidResponse,freeze,type Frozen} from './read-validation.js';
export type PendingAdminEdit=Readonly<{account_id:string;org_id:string;capture_id:string;command:EditCommand}>;
/** Owner pins generation/account/org and aborts on session replacement/disposal.
 * This local publication fence grants no authority; server current read.all AND
 * edit.all remain authoritative, without original-owner impersonation. */
export type AdminEditOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
type SafeVariant<S,E>=E extends {error_id:string}?Readonly<{kind:'error';status:S;error_id:E['error_id']}&(E extends {current_revision:string}?Pick<E,'current_revision'>:{})>:never;
export type AdminEditError={[S in keyof AdminEditCaptureErrors]:SafeVariant<S,AdminEditCaptureErrors[S]>}[keyof AdminEditCaptureErrors];
export type AdminEditResult=Readonly<{kind:'committed';receipt:Frozen<AdminEditCaptureResponse>}>|AdminEditError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

function success(value: unknown, operation_id: string, capture_id: string): AdminEditResult {
  const base=object(value,['operation_id','command_type','status','command_version','result']);
  if (base.operation_id!==operation_id || base.command_type!=='capture.edit' || base.status!=='committed' || base.command_version!==1) return invalid();
  const result=object(base.result,['capture_id','revision']);
  if (result.capture_id!==capture_id || !decimal(result.revision)) return invalid();
  return {kind:'committed',receipt:freeze({operation_id,command_type:'capture.edit',
    command_version:1,status:'committed',result:{capture_id,revision:result.revision}})};
}
function errorResult(status: number,value: unknown): AdminEditError {
  const body=object(value,['error','error_id'],['code','current_revision']);
  if (typeof body.error!=='string' || (body.code!==undefined && body.code!==null && (typeof body.code!=='number'||!Number.isInteger(body.code)))) return invalid();
  const e=body.error_id;
  if (status===409 && e==='kdg_capture.capture_revision_conflict') {
    if (!decimal(body.current_revision)) return invalid();
    return {kind:'error',status,error_id:e,current_revision:body.current_revision};
  }
  if (Object.hasOwn(body,'current_revision')) return invalid();
  if (status===401 && e==='authentication_required') return {kind:'error',status,error_id:e};
  if (status===403 && e==='access_denied') return {kind:'error',status,error_id:e};
  if (status===404 && e==='capture_unavailable') return {kind:'error',status,error_id:e};
  if (status===409 && (e==='identity.actor_setup_required'||e==='operation_busy'||e==='questionnaire_version_unavailable')) return {kind:'error',status,error_id:e};
  if (status===422 && (e==='validation_failed'||e==='unsupported_command_version')) return {kind:'error',status,error_id:e};
  if (status===500 && (e==='internal_error'||e==='invalid_write_context')) return {kind:'error',status,error_id:e};
  if (status===503 && (e==='authorization_unavailable'||e==='operation_verification_unavailable'||e==='authorization_observation_expired'||e==='execution_timeout')) return {kind:'error',status,error_id:e};
  return invalid();
}


export async function editAdminCapture(session: Session,pending: PendingAdminEdit,options: AdminEditOptions): Promise<AdminEditResult> {
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
  const finish=(result: AdminEditResult): AdminEditResult => {
    const fresh=current(); // Delegated predicates may synchronously abort the owner.
    return Object.freeze(signal.aborted?{kind:'cancelled'}:
      !fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  };
  if (!current() || signal.aborted || performance.now()>=deadline) return finish({kind:'superseded'});
  // Copy primitives before any await; caller mutation cannot retarget this request.
  let auth: Session, pinned: {account_id: string; org_id: string; capture_id: string}, serialized: string, operation_id: string;
  try {
    auth={account_id:session?.account_id,access_token:session?.access_token};
    if (!id(auth.account_id)||!token(auth.access_token)) return finish({kind:'authentication_required'});
    object(pending,['account_id','org_id','capture_id','command']);
    pinned={account_id:pending.account_id,org_id:pending.org_id,capture_id:pending.capture_id};
    const command={...pending.command};
    object(command,['operation_id','command_version','expected_revision','observation_date','answers']);
    operation_id=command.operation_id;
    if (pinned.account_id!==auth.account_id || !id(pinned.org_id) || !id(pinned.capture_id) || !id(operation_id) ||
      command.command_version!==1 || !decimal(command.expected_revision)) return finish({kind:'invalid_request'});
    // Generated DTO supplies structure; original-definition/domain validation stays server-owned.
    // Serialize nested input now, before transport or any await; never freeze caller objects.
    if (command.answers && typeof command.answers==='object' &&
        Object.values(command.answers).some(answer=>answer===undefined)) return finish({kind:'invalid_request'});
    serialized=JSON.stringify(command);
    if (new TextEncoder().encode(serialized).byteLength>131072) return finish({kind:'invalid_request'});
    const snapshot=object(strictJSON(serialized),['operation_id','command_version','expected_revision','observation_date','answers']);
    if (snapshot.operation_id!==operation_id || snapshot.command_version!==1 || snapshot.expected_revision!==command.expected_revision ||
        typeof snapshot.observation_date!=='string' || !snapshot.answers || typeof snapshot.answers!=='object' || Array.isArray(snapshot.answers)) return finish({kind:'invalid_request'});
  } catch {return finish({kind:'invalid_request'});}
  if (!current() || signal.aborted) return finish({kind:'superseded'});
  if (performance.now()>=deadline) return finish({kind:'verification_unavailable'});
  const controller=new AbortController();let body: ReadableStream<Uint8Array>|null|undefined;let reader: ReadableStreamDefaultReader<Uint8Array>|undefined;
  const cancelBody=()=>{try {const work=reader?reader.cancel():body?.cancel();if(work)void work.catch(()=>{});} catch {/* owned transport cancellation is best effort */}};
  let stop!: (result: AdminEditResult)=>void;
  const stopped=new Promise<AdminEditResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<AdminEditResult> => {
    try {
      const data: Pick<AdminEditCaptureData,'url'|'path'>={url:'/api/v1/admin/captures/{capture_id}',path:{capture_id:pinned.capture_id}};
      const response=await request(data.url.replace('{capture_id}',data.path.capture_id),{
        method:'PUT',headers:{Authorization:'Bearer '+auth.access_token,'Content-Type':'application/json'},body:serialized,
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
      return response.status===200?success(value,operation_id,pinned.capture_id):errorResult(response.status,value);
    } catch (error) {return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
  };
  try {return finish(await Promise.race([work(),stopped]));}
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
