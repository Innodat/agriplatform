/** Unmounted current setup consumer; no persistence, provisioning or startup activation. */
import type {Provision, ProvisionSetupData, ProvisionSetupErrors} from '../../contracts/provision-generated/types.gen';
import type {Session} from './entry';

import {validateOwnObservation} from './own-observation.js';

export type PendingProvision = Readonly<{account_id:string; org_id:string; }>;
export type ProvisionOptions = {signal:AbortSignal; isCurrent:()=>boolean; request?:typeof fetch; timeoutMs?:number};
export type SafeError = {[S in keyof ProvisionSetupErrors]: Readonly<{kind:'error';status:S;error_id:ProvisionSetupErrors[S]['error_id']}>}[keyof ProvisionSetupErrors];
type Frozen<T> = T extends object ? {readonly [K in keyof T]:Frozen<T[K]>} : T;
export type ProvisionResult = Readonly<{kind:'loaded';provision:Frozen<Provision>}> | SafeError |
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

import {id,token,object,strictJSON,validateDefinition,freeze,InvalidResponse,invalid,decimal,text,instant} from './read-validation.js';


const prefix='kdg_capture.capture.';
const canonicalInstant=(v:unknown):v is string=>instant(v)&&v[10]==='T'&&v.endsWith('Z');
function windowEvidence(value:Record<string,unknown>){
 if(!canonicalInstant(value.checked_at)||!canonicalInstant(value.expires_at)||Date.parse(value.expires_at)-Date.parse(value.checked_at)!==604800000||value.checked_at.slice(19)!==value.expires_at.slice(19))return invalid();
}
/** Validates a private parsed response. No local permission is granted or persisted. */
export function validateProvision(value:unknown,pinned:PendingProvision):Frozen<Provision>{
 const p=object(value,['schema_version','org_id','account_id','actor_id','membership_id','read_observation','edit_observation','create_all_observation','create_assigned_observation','create_state','children','questionnaire']);
 if(!id(pinned.account_id)||!id(pinned.org_id)||p.schema_version!==1||p.account_id!==pinned.account_id||p.org_id!==pinned.org_id||!id(p.actor_id)||!decimal(p.membership_id)||new TextEncoder().encode(JSON.stringify(value)).byteLength>1048576)return invalid();
 const observations=[['read_observation','read.own'],['edit_observation','edit.own'],['create_all_observation','create.all'],['create_assigned_observation','create.assigned']] as const;
 for(const [slot,capability] of observations){
  const raw=p[slot];if(raw===null&&slot!=='read_observation')continue;
  const observed=validateOwnObservation(raw,pinned.account_id,pinned.org_id,`${prefix}${capability}`);
  windowEvidence(observed);
  if(observed.actor_id!==p.actor_id||observed.membership_id!==p.membership_id)return invalid();
 }
 if(!Array.isArray(p.children)||p.children.length>1000)return invalid();
 const permission=p.create_all_observation!==null?`${prefix}create.all`:p.create_assigned_observation!==null?`${prefix}create.assigned`:null;
 const ids=new Set<string>(),refs=new Set<string>();
 for(const raw of p.children){
  const c=object(raw,['child_id','child_label','child_revision','child_eligibility_ref','create_permission','assignment','checked_at','expires_at']);
  if(!id(c.child_id)||ids.has(c.child_id)||!text(c.child_label,200,true)||!decimal(c.child_revision)||typeof c.child_eligibility_ref!=='string'||c.child_eligibility_ref.length!==43||!/^[A-Za-z0-9_-]+$/.test(c.child_eligibility_ref)||refs.has(c.child_eligibility_ref)||c.create_permission!==permission||permission===null)return invalid();
  ids.add(c.child_id);refs.add(c.child_eligibility_ref);windowEvidence(c);
  if(permission===`${prefix}create.all`){if(c.assignment!==null)return invalid();}
  else{const a=object(c.assignment,['assignment_id','assignment_revision']);if(!id(a.assignment_id)||!decimal(a.assignment_revision))return invalid();}
 }
 if(p.questionnaire!==null){
  const q=object(p.questionnaire,['questionnaire_id','questionnaire_version_id','questionnaire_version','definition']);
  if(!id(q.questionnaire_id)||!id(q.questionnaire_version_id)||!decimal(q.questionnaire_version))return invalid();
  validateDefinition(q.definition);
 }
 const state=permission===null?'not_permitted':p.questionnaire===null?'no_published_questionnaire':p.children.length===0?'no_eligible_children':'ready';
 if(p.create_state!==state)return invalid();
 return freeze(value as Provision);
}
function errorResult(status:number,value:unknown):SafeError{
 const body=object(value,['error','error_id'],['code']);
 if(typeof body.error!=='string'||body.code!==undefined&&body.code!==null&&(typeof body.code!=='number'||!Number.isInteger(body.code)))return invalid();
 const pairs:Record<number,readonly string[]>={401:['authentication_required'],403:['access_denied'],409:['identity.actor_setup_required'],422:['validation_failed'],500:['invalid_write_context','internal_error'],503:['authorization_unavailable','provision_unavailable','authorization_observation_expired','execution_timeout']};
 if(typeof body.error_id!=='string'||!pairs[status]?.includes(body.error_id))return invalid();
 return {kind:'error',status,error_id:body.error_id} as SafeError;
}

export async function loadProvision(session: Session,pending: PendingProvision,options: ProvisionOptions): Promise<ProvisionResult> {
  let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
  try {
    duration=options?.timeoutMs??10000;signal=options.signal;isCurrent=options.isCurrent;request=options.request??fetch;
    if (!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
  } catch {return Object.freeze({kind:'invalid_request'});}
  const current=()=>{try {return isCurrent()===true;} catch {return false;}};
  const deadline=performance.now()+duration;
  const finish=(result: ProvisionResult): ProvisionResult => {
    const fresh=current(); // Delegated predicates may synchronously abort the owner.
    return Object.freeze(signal.aborted?{kind:'cancelled'}:
      !fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
  };
  // Copy primitives before any await; caller mutation cannot retarget this request.
  let auth: Session, pinned: PendingProvision;
  try {
    auth={account_id:session?.account_id,access_token:session?.access_token};pinned={...pending};
    if (!id(auth.account_id)||!token(auth.access_token)) return finish({kind:'authentication_required'});
    object(pinned,['account_id','org_id']);
    if(pinned.account_id!==auth.account_id||!id(pinned.org_id))return finish({kind:'invalid_request'});
  } catch {return finish({kind:'invalid_request'});}
  if (!current() || signal.aborted) return finish({kind:'superseded'});
  const controller=new AbortController();let body: ReadableStream<Uint8Array>|null|undefined;let reader: ReadableStreamDefaultReader<Uint8Array>|undefined;
  let stop!: (result: ProvisionResult)=>void;
  const stopped=new Promise<ProvisionResult>(resolve=>{stop=resolve;});
  const cancel=()=>{controller.abort();stop({kind:'cancelled'});};
  signal.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>{controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
  const work=async(): Promise<ProvisionResult> => {
    try {
      const data:ProvisionSetupData={url:'/api/v1/provision'};
      const response=await request(data.url,{
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
        if (size+chunk.value.byteLength>1048576) return invalid();
        size+=chunk.value.byteLength;chunks.push(chunk.value);
      }
      const bytes=new Uint8Array(size);let offset=0;for (const chunk of chunks) {bytes.set(chunk,offset);offset+=chunk.byteLength;}
      let value: unknown;
      try {value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));} catch {return invalid();}
      return response.status===200?{kind:'loaded',provision:validateProvision(value,pinned)}:errorResult(response.status,value);
    } catch (error) {return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
  };
  try {return finish(await Promise.race([work(),stopped]));}
  finally {clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if (reader) void reader.cancel().catch(()=>{});else if (body) void body.cancel().catch(()=>{});}
}
