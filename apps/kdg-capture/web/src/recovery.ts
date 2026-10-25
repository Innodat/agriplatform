/** Candidate-only own-read recovery; no Auth, queue, UI or storage side effects. */
import type {CaptureReceipt, Unresolved, RecoverOperationData, RecoverOperationErrors} from '../../contracts/recovery-generated/types.gen';
import type {Session} from './entry';

export type PendingRecovery = Readonly<{account_id: string; org_id: string; operation_id: string} & (
  {command_type: 'capture.create'} | {command_type: 'capture.edit'; capture_id: string})>;
/** Owner captures its existing generation AND pinned account/org. Exceptions mean stale.
 * Owner must abort on logout, organization/session replacement and disposal. This is
 * a local freshness fence, never cached authorization; the server checks current access.
 */
export type RecoveryOptions = {signal: AbortSignal; isCurrent: () => boolean; request?: typeof fetch; timeoutMs?: number};
type SafeError = {[S in keyof RecoverOperationErrors]: Readonly<{
  kind: 'error'; status: S; error_id: RecoverOperationErrors[S]['error_id']
}>}[keyof RecoverOperationErrors];
export type RecoveryResult = Readonly<{kind: 'committed'; receipt: Readonly<Omit<CaptureReceipt,'result'>> & {readonly result: Readonly<CaptureReceipt['result']>}}> |
  Readonly<{kind: 'unresolved'; outcome: Readonly<Unresolved>}> | SafeError |
  Readonly<{kind: 'invalid_request' | 'authentication_required' | 'invalid_response' | 'verification_unavailable' | 'cancelled' | 'superseded'}>;

const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const id=(v: unknown): v is string => typeof v==='string' && v.length===36 && UUID.test(v) && v!=='00000000-0000-0000-0000-000000000000';
const token=(v: unknown): v is string => typeof v==='string' && /^[A-Za-z0-9\-._~+/]+=*$/.test(v) && !/\s/.test(v);
class InvalidResponse extends Error {}
const invalid=(): never => {throw new InvalidResponse();};
function object(v: unknown, keys: string[], optional: string[]=[]): Record<string,unknown> {
  if (!v || typeof v!=='object' || Array.isArray(v)) return invalid();
  if (!keys.every(k=>Object.hasOwn(v,k)) || !Object.keys(v).every(k=>keys.includes(k)||optional.includes(k))) return invalid();
  return v as Record<string,unknown>;
}
function strictJSON(text: string): unknown {
  const value: unknown=JSON.parse(text); // Standard parser owns JSON grammar.
  const tokens=[...text.matchAll(/"(?:\\[\s\S]|[^"\\])*"|[{}\[\]:]/g)].map(m=>m[0]);
  const stack: Array<Set<string>|null>=[];
  for (let i=0;i<tokens.length;i++) {
    const t=tokens[i];
    if (t==='{') stack.push(new Set());
    else if (t==='[') stack.push(null);
    else if (t==='}'||t===']') stack.pop();
    else if (t.startsWith('"') && tokens[i+1]===':') {
      const key: string=JSON.parse(t), keys=stack.at(-1);
      if (!keys || keys.has(key)) return invalid();
      keys.add(key);
    }
  }
  const check=(v: unknown): void => {
    if (typeof v==='number' && !Number.isFinite(v)) return invalid();
    if (typeof v==='string') {
      for (const c of v) {const code=c.codePointAt(0)!;if (code===0 || (code>=0xd800&&code<=0xdfff)) return invalid();}
    } else if (v && typeof v==='object') for (const [k,item] of Object.entries(v)) {check(k);check(item);}
  };
  check(value);return value;
}
function success(value: unknown, pending: PendingRecovery): RecoveryResult {
  const base=object(value,['operation_id','command_type','status'],['command_version','result']);
  if (base.operation_id!==pending.operation_id || base.command_type!==pending.command_type) return invalid();
  if (base.status==='unresolved') {
    object(value,['operation_id','command_type','status']);
    return {kind:'unresolved',outcome:Object.freeze({operation_id:pending.operation_id,command_type:pending.command_type,status:'unresolved'})};
  }
  object(value,['operation_id','command_type','status','command_version','result']);
  if (base.status!=='committed' || base.command_version!==1) return invalid();
  const result=object(base.result,['capture_id','revision']);
  if (!id(result.capture_id) || typeof result.revision!=='string' || result.revision.length>19 ||
    !result.revision || result.revision[0]==='0' || /[^0-9]/.test(result.revision) || BigInt(result.revision)>9223372036854775807n ||
    (pending.command_type==='capture.edit' && result.capture_id!==pending.capture_id)) return invalid();
  return {kind:'committed',receipt:Object.freeze({operation_id:pending.operation_id,command_type:pending.command_type,
    command_version:1,status:'committed',result:Object.freeze({capture_id:result.capture_id,revision:result.revision})})};
}
function errorResult(status: number,value: unknown): SafeError {
  const body=object(value,['error','error_id'],['code']);
  if (typeof body.error!=='string' || (body.code!==undefined && body.code!==null && (typeof body.code!=='number'||!Number.isFinite(body.code)))) return invalid();
  const e=body.error_id;
  if (status===401 && e==='authentication_required') return {kind:'error',status,error_id:e};
  if (status===403 && e==='access_denied') return {kind:'error',status,error_id:e};
  if (status===409 && e==='identity.actor_setup_required') return {kind:'error',status,error_id:e};
  if (status===422 && e==='validation_failed') return {kind:'error',status,error_id:e};
  if (status===500 && (e==='internal_error'||e==='invalid_write_context')) return {kind:'error',status,error_id:e};
  if (status===503 && (e==='authorization_unavailable'||e==='operation_verification_unavailable'||e==='authorization_observation_expired'||e==='execution_timeout')) return {kind:'error',status,error_id:e};
  return invalid();
}

export async function recoverOperation(session: Session,pending: PendingRecovery,options: RecoveryOptions): Promise<RecoveryResult> {
  const duration=options?.timeoutMs??10000;
  if (!options || !(options.signal instanceof AbortSignal) || typeof options.isCurrent!=='function' ||
      (options.request!==undefined && typeof options.request!=='function') ||
      !Number.isFinite(duration)||duration<=0||duration>10000) return Object.freeze({kind:'invalid_request'});
  const signal=options.signal, isCurrent=options.isCurrent, request=options.request??fetch;
  const current=()=>{try {return isCurrent()===true;} catch {return false;}};
  const deadline=performance.now()+duration;
  const finish=(result: RecoveryResult): RecoveryResult => Object.freeze(signal.aborted?{kind:'cancelled'}:
    !current()?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  // Copy primitives before any await; caller mutation cannot retarget this request.
  let auth: Session, pinned: PendingRecovery;
  try {
    auth={account_id:session?.account_id,access_token:session?.access_token};pinned={...pending};
    if (!id(auth.account_id)||!token(auth.access_token)) return finish({kind:'authentication_required'});
    object(pinned,['account_id','org_id','operation_id','command_type'],pinned.command_type==='capture.edit'?['capture_id']:[]);
    if (pinned.account_id!==auth.account_id || !id(pinned.org_id) || !id(pinned.operation_id) ||
      (pinned.command_type!=='capture.create'&&pinned.command_type!=='capture.edit') ||
      (pinned.command_type==='capture.edit'&&!id(pinned.capture_id))) return finish({kind:'invalid_request'});
  } catch {return finish({kind:'invalid_request'});}
  if (signal.aborted || !current()) return finish({kind:'superseded'});
  const controller=new AbortController();let body: ReadableStream<Uint8Array>|null|undefined;let reader: ReadableStreamDefaultReader<Uint8Array>|undefined;
  let stop!: (result: RecoveryResult)=>void;
  const stopped=new Promise<RecoveryResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<RecoveryResult> => {
    try {
      const data: RecoverOperationData={url:'/api/v1/operations/{operation_id}',path:{operation_id:pinned.operation_id},query:{command_type:pinned.command_type}};
      const response=await request(data.url.replace('{operation_id}',data.path.operation_id)+'?command_type='+data.query.command_type,{
        method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
      body=response.body;
      if (controller.signal.aborted) {if (response.body) void response.body.cancel().catch(()=>{});return {kind:'cancelled'};}
      const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(v=>v.trim())??[];
      if (response.redirected || !response.body || response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json' || !cache.includes('private') || !cache.includes('no-store')) return invalid();
      reader=response.body.getReader();const chunks: Uint8Array[]=[];let size=0;
      while (true) {
        // Immediate read promises can starve timer tasks, especially on empty
        // chunks. Enforce the same monotonic deadline inside the read loop.
        if (signal.aborted || !current() || performance.now()>=deadline) return finish({kind:'verification_unavailable'});
        const chunk=await reader.read();
        if (signal.aborted || !current() || performance.now()>=deadline) return finish({kind:'verification_unavailable'});
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
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if (reader) void reader.cancel().catch(()=>{});else if (body) void body.cancel().catch(()=>{});}
}
