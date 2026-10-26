/** Candidate-only current own-detail read; no Auth, queue, UI or storage side effects. */
import type {CaptureDetail, ReadCaptureData, ReadCaptureErrors} from '../../contracts/read-generated/types.gen';
import type {Session} from './entry';

export type PendingRead = Readonly<{account_id:string; org_id:string; capture_id:string}>;
export type ReadOptions = {signal:AbortSignal; isCurrent:()=>boolean; request?:typeof fetch; timeoutMs?:number};
export type SafeError = {[S in keyof ReadCaptureErrors]: Readonly<{kind:'error';status:S;error_id:ReadCaptureErrors[S]['error_id']}>}[keyof ReadCaptureErrors];
type Frozen<T> = T extends object ? {readonly [K in keyof T]:Frozen<T[K]>} : T;
export type ReadResult = Readonly<{kind:'loaded';snapshot:Frozen<CaptureDetail>}> | SafeError |
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

import {id,token,object,strictJSON,validateDetail,errorResult,InvalidResponse,invalid} from './read-validation.js';

export async function readCapture(session: Session,pending: PendingRead,options: ReadOptions): Promise<ReadResult> {
  const duration=options?.timeoutMs??10000;
  if (!options || !(options.signal instanceof AbortSignal) || typeof options.isCurrent!=='function' ||
      (options.request!==undefined && typeof options.request!=='function') ||
      !Number.isFinite(duration)||duration<=0||duration>10000) return Object.freeze({kind:'invalid_request'});
  const signal=options.signal, isCurrent=options.isCurrent, request=options.request??fetch;
  const current=()=>{try {return isCurrent()===true;} catch {return false;}};
  const deadline=performance.now()+duration;
  const finish=(result: ReadResult): ReadResult => {
    const fresh=current(); // Delegated predicates may synchronously abort the owner.
    return Object.freeze(signal.aborted?{kind:'cancelled'}:
      !fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  };
  // Copy primitives before any await; caller mutation cannot retarget this request.
  let auth: Session, pinned: PendingRead;
  try {
    auth={account_id:session?.account_id,access_token:session?.access_token};pinned={...pending};
    if (!id(auth.account_id)||!token(auth.access_token)) return finish({kind:'authentication_required'});
    object(pinned,['account_id','org_id','capture_id']);
    if(pinned.account_id!==auth.account_id||!id(pinned.org_id)||!id(pinned.capture_id))return finish({kind:'invalid_request'});
  } catch {return finish({kind:'invalid_request'});}
  if (!current() || signal.aborted) return finish({kind:'superseded'});
  const controller=new AbortController();let body: ReadableStream<Uint8Array>|null|undefined;let reader: ReadableStreamDefaultReader<Uint8Array>|undefined;
  let stop!: (result: ReadResult)=>void;
  const stopped=new Promise<ReadResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<ReadResult> => {
    try {
      const data:ReadCaptureData={url:'/api/v1/captures/{capture_id}',path:{capture_id:pinned.capture_id}};
      const response=await request(data.url.replace('{capture_id}',data.path.capture_id),{
        method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
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
        if (size+chunk.value.byteLength>524288) return invalid();
        size+=chunk.value.byteLength;chunks.push(chunk.value);
      }
      const bytes=new Uint8Array(size);let offset=0;for (const chunk of chunks) {bytes.set(chunk,offset);offset+=chunk.byteLength;}
      let value: unknown;
      try {value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));} catch {return invalid();}
      return response.status===200?{kind:'loaded',snapshot:validateDetail(value,pinned)}:errorResult(response.status,value);
    } catch (error) {return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
  };
  try {return finish(await Promise.race([work(),stopped]));}
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if (reader) void reader.cancel().catch(()=>{});else if (body) void body.cancel().catch(()=>{});}
}
