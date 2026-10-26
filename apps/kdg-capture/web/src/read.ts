/** Candidate-only current own-detail read; no Auth, queue, UI or storage side effects. */
import type {CaptureDetail, ReadCaptureData, ReadCaptureErrors} from '../../contracts/read-generated/types.gen';
import type {Session} from './entry';

export type PendingRead = Readonly<{account_id:string; org_id:string; capture_id:string}>;
export type ReadOptions = {signal:AbortSignal; isCurrent:()=>boolean; request?:typeof fetch; timeoutMs?:number};
type SafeError = {[S in keyof ReadCaptureErrors]: Readonly<{kind:'error';status:S;error_id:ReadCaptureErrors[S]['error_id']}>}[keyof ReadCaptureErrors];
type Frozen<T> = T extends object ? {readonly [K in keyof T]:Frozen<T[K]>} : T;
export type ReadResult = Readonly<{kind:'loaded';snapshot:Frozen<CaptureDetail>}> | SafeError |
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

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
const decimal=(v:unknown):v is string => typeof v==='string' && v.length<=19 && /^[1-9][0-9]*(?![\s\S])/.test(v) && BigInt(v)<=9223372036854775807n;
// Python str.strip whitespace used by the existing domain validators (FEFF is content).
const nonblank=/[^\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/u;
const text=(v:unknown,max:number,required=false):v is string=>typeof v==='string'&&[...v].length<=max&&(!required||nonblank.test(v));
function date(v:unknown):v is string {
 if(typeof v!=='string'||v.startsWith('0000')||!(/^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])/).test(v))return false;
 const parsed=new Date(v+'T00:00:00Z');return Number.isFinite(parsed.getTime())&&parsed.toISOString().slice(0,10)===v;
}
function instant(v:unknown):v is string {
 return typeof v==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|\+00:00)(?![\s\S])/.test(v)&&date(v.slice(0,10))&&
 Number(v.slice(11,13))<24&&Number(v.slice(14,16))<60&&Number(v.slice(17,19))<60;
}
function freeze<T>(value:T):Frozen<T> {
 if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}
 return value as Frozen<T>;
}
function success(value:unknown,pending:PendingRead):ReadResult {
 const d=object(value,['capture_id','org_id','owner_account_id','owner_actor_id','child_id','child_label','questionnaire_id','questionnaire_version_id','questionnaire_version','definition','revision','observation_date','answers','captured_at','created_by','created_at','updated_by','updated_at']);
 for(const k of ['capture_id','org_id','owner_account_id','owner_actor_id','child_id','questionnaire_id','questionnaire_version_id','created_by','updated_by'])if(!id(d[k]))return invalid();
 if(d.capture_id!==pending.capture_id||d.org_id!==pending.org_id||d.owner_account_id!==pending.account_id||d.created_by!==d.owner_actor_id||
 !decimal(d.revision)||!decimal(d.questionnaire_version)||!text(d.child_label,200,true)||!date(d.observation_date)||
 !instant(d.captured_at)||!instant(d.created_at)||!instant(d.updated_at))return invalid();
 const definition=object(d.definition,['schema_version','questions']);
 if(definition.schema_version!==1||!Array.isArray(definition.questions)||!definition.questions.length||definition.questions.length>50||
 new TextEncoder().encode(JSON.stringify(definition)).byteLength>131072)return invalid();
 const answers=objectMap(d.answers),seen=new Set<string>();
 if(Object.keys(answers).length>50)return invalid();
 for(const raw of definition.questions){
  const q=object(raw,['id','type','label','required'],['minimum','maximum','minimum_label','maximum_label','default','details_enabled','details_label']);
  if(!id(q.id)||seen.has(q.id)||!text(q.label,500,true)||typeof q.required!=='boolean')return invalid();seen.add(q.id);
  if(q.type==='rating'){
   object(q,['id','type','label','required','minimum','maximum','minimum_label','maximum_label']);
   if(q.minimum!==1||q.maximum!==5||q.minimum_label!=='Goed'||q.maximum_label!=='Nie goed nie')return invalid();
  }else if(q.type==='boolean'){
   object(q,['id','type','label','required','default','details_enabled'],['details_label']);
   if(q.default!==false||typeof q.details_enabled!=='boolean'||(q.details_enabled?!text(q.details_label,500,true):(q.details_label!==undefined&&q.details_label!==null)))return invalid();
  }else if(q.type==='text')object(q,['id','type','label','required']);else return invalid();
  if(!Object.hasOwn(answers,q.id)){if(q.required)return invalid();continue;}
  const answer=object(answers[q.id],['value'],q.type==='boolean'?['details']:[]);
  if(q.type==='rating'){if(typeof answer.value!=='number'||!Number.isInteger(answer.value)||answer.value<1||answer.value>5)return invalid();}
  else if(q.type==='text'){if(!text(answer.value,5000,true))return invalid();}
  else if(typeof answer.value!=='boolean'||(Object.hasOwn(answer,'details')&&(answer.value!==true||q.details_enabled!==true||!text(answer.details,5000))))return invalid();
 }
 if(Object.keys(answers).some(k=>!seen.has(k)))return invalid();
 // Shape and all nested relationships were checked above. This is a private
 // parsed object; deep freezing never mutates caller input or a shared response.
 return {kind:'loaded',snapshot:freeze(value as CaptureDetail)};
}
function objectMap(v:unknown):Record<string,unknown>{
 if(!v||typeof v!=='object'||Array.isArray(v))return invalid();return v as Record<string,unknown>;
}
function errorResult(status: number,value: unknown): SafeError {
  const body=object(value,['error','error_id'],['code']);
  if (typeof body.error!=='string' || (body.code!==undefined && body.code!==null && (typeof body.code!=='number'||!Number.isInteger(body.code)))) return invalid();
  const e=body.error_id;
  if (status===401 && e==='authentication_required') return {kind:'error',status,error_id:e};
  if (status===404 && e==='capture_unavailable') return {kind:'error',status,error_id:e};
  if (status===403 && e==='access_denied') return {kind:'error',status,error_id:e};
  if (status===409 && e==='identity.actor_setup_required') return {kind:'error',status,error_id:e};
  if (status===422 && e==='validation_failed') return {kind:'error',status,error_id:e};
  if (status===500 && (e==='internal_error'||e==='invalid_write_context')) return {kind:'error',status,error_id:e};
  if (status===503 && (e==='authorization_unavailable'||e==='capture_read_unavailable'||e==='authorization_observation_expired'||e==='execution_timeout')) return {kind:'error',status,error_id:e};
  return invalid();
}

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
      return response.status===200?success(value,pinned):errorResult(response.status,value);
    } catch (error) {return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
  };
  try {return finish(await Promise.race([work(),stopped]));}
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if (reader) void reader.cancel().catch(()=>{});else if (body) void body.cancel().catch(()=>{});}
}
