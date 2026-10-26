/** Candidate-only own edit; no Auth, queue, UI or storage side effects.
 * A cancelled/timed-out request may still commit. Preserve its original input/identity. */
import type {CaptureReceipt, EditCommand, EditCaptureData, EditCaptureErrors} from '../../contracts/edit-generated/types.gen';
import type {Session} from './entry';

export type PendingEdit = Readonly<{account_id: string; org_id: string; capture_id: string; command: EditCommand}>;
/** Owner captures its existing generation AND pinned account/org. Exceptions mean stale.
 * Owner must abort on logout, organization/session replacement and disposal. This is
 * a local freshness fence, never cached authorization; the server checks current access.
 */
export type EditOptions = {signal: AbortSignal; isCurrent: () => boolean; request?: typeof fetch; timeoutMs?: number};
type SafeVariant<S, E> = E extends {error_id: string} ? Readonly<{
  kind: 'error'; status: S; error_id: E['error_id']
} & (E extends {current_revision: string} ? Pick<E, 'current_revision'> : {})> : never;
type SafeError = {[S in keyof EditCaptureErrors]: SafeVariant<S, EditCaptureErrors[S]>}[keyof EditCaptureErrors];
export type EditResult = Readonly<{kind: 'committed'; receipt: Readonly<Omit<CaptureReceipt,'result'>> & {readonly result: Readonly<CaptureReceipt['result']>}}> | SafeError |
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
const revision=(v: unknown): v is string => typeof v==='string' && v.length<=19 && /^[1-9][0-9]*$/.test(v) && !/[^0-9]/.test(v) && BigInt(v)<=9223372036854775807n;
function success(value: unknown, operation_id: string, capture_id: string): EditResult {
  const base=object(value,['operation_id','command_type','status','command_version','result']);
  if (base.operation_id!==operation_id || base.command_type!=='capture.edit' || base.status!=='committed' || base.command_version!==1) return invalid();
  const result=object(base.result,['capture_id','revision']);
  if (result.capture_id!==capture_id || !revision(result.revision)) return invalid();
  return {kind:'committed',receipt:Object.freeze({operation_id,command_type:'capture.edit',
    command_version:1,status:'committed',result:Object.freeze({capture_id,revision:result.revision})})};
}
function errorResult(status: number,value: unknown): SafeError {
  const body=object(value,['error','error_id'],['code','current_revision']);
  if (typeof body.error!=='string' || (body.code!==undefined && body.code!==null && (typeof body.code!=='number'||!Number.isFinite(body.code)))) return invalid();
  const e=body.error_id;
  if (status===409 && e==='kdg_capture.capture_revision_conflict') {
    if (!revision(body.current_revision)) return invalid();
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

export async function editCapture(session: Session,pending: PendingEdit,options: EditOptions): Promise<EditResult> {
  const duration=options?.timeoutMs??10000;
  if (!options || !(options.signal instanceof AbortSignal) || typeof options.isCurrent!=='function' ||
      (options.request!==undefined && typeof options.request!=='function') ||
      !Number.isFinite(duration)||duration<=0||duration>10000) return Object.freeze({kind:'invalid_request'});
  const signal=options.signal, isCurrent=options.isCurrent, request=options.request??fetch;
  const current=()=>{try {return isCurrent()===true;} catch {return false;}};
  const deadline=performance.now()+duration;
  const finish=(result: EditResult): EditResult => {
    const fresh=current(); // Delegated predicates may synchronously abort the owner.
    return Object.freeze(signal.aborted?{kind:'cancelled'}:
      !fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  };
  if (!current() || signal.aborted) return finish({kind:'superseded'});
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
      command.command_version!==1 || !revision(command.expected_revision)) return finish({kind:'invalid_request'});
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
  let stop!: (result: EditResult)=>void;
  const stopped=new Promise<EditResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<EditResult> => {
    try {
      const data: Pick<EditCaptureData,'url'|'path'>={url:'/api/v1/captures/{capture_id}',path:{capture_id:pinned.capture_id}};
      const response=await request(data.url.replace('{capture_id}',data.path.capture_id),{
        method:'PUT',headers:{Authorization:'Bearer '+auth.access_token,'Content-Type':'application/json'},body:serialized,
        credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
      body=response.body;
      if (controller.signal.aborted) {if (response.body) void response.body.cancel().catch(()=>{});return {kind:'cancelled'};}
      const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(v=>v.trim())??[];
      if (response.redirected || !response.body || response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json' || !cache.includes('private') || !cache.includes('no-store')) return invalid();
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
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if (reader) void reader.cancel().catch(()=>{});else if (body) void body.cancel().catch(()=>{});}
}
