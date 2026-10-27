/** Explicit current organization detail read; no admission, UI, cache or retry effects. */
import type {AdminDetailResponse,AdminDetailData,AdminDetailErrors} from '../../contracts/admin-generated/types.gen';
import type {Session} from './entry';
import {id,token,object,strictJSON,validateDetail,errorResult,InvalidResponse,invalid,type Frozen} from './read-validation.js';
export type PendingAdminDetail=Readonly<{account_id:string;org_id:string;capture_id:string}>;
export type AdminDetailOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
export type AdminDetailError={[S in keyof AdminDetailErrors]:Readonly<{kind:'error';status:S;error_id:AdminDetailErrors[S]['error_id']}>}[keyof AdminDetailErrors];
export type AdminDetailResult=Readonly<{kind:'loaded';snapshot:Frozen<AdminDetailResponse>}>|AdminDetailError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;

function pin(value:PendingAdminDetail):PendingAdminDetail {
 // Primitives in this private copy are the only scope used after awaits.
 const pinned={...value};object(pinned,['account_id','org_id','capture_id']);
 if(!id(pinned.account_id)||!id(pinned.org_id)||!id(pinned.capture_id))return invalid();
 return pinned;
}

function validateSnapshot(value:unknown,pinned:PendingAdminDetail):Frozen<AdminDetailResponse> {
 // An all-read caller can differ from both original owner and actual executor.
 // Detail has no reader echo. Pinning and the current-generation guard bind the
 // request; the original validator still owns every content/provenance check.
 if(!value||typeof value!=='object'||Array.isArray(value))return invalid();
 const owner=(value as Record<string,unknown>).owner_account_id;
 if(!id(owner))return invalid();
 return validateDetail(value,{account_id:owner,org_id:pinned.org_id,capture_id:pinned.capture_id});
}

export async function readAdminCapture(session:Session,pending:PendingAdminDetail,options:AdminDetailOptions):Promise<AdminDetailResult> {
 let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
 try{
  object(options,['signal','isCurrent'],['request','timeoutMs']);
  duration=options.timeoutMs===undefined?10000:options.timeoutMs;signal=options.signal;isCurrent=options.isCurrent;request=options.request===undefined?fetch:options.request;
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const deadline=performance.now()+duration;
 const current=()=>{try{return isCurrent()===true;}catch{return false;}};
 const finish=(result:AdminDetailResult):AdminDetailResult=>{
  const fresh=current(); // A caller predicate can synchronously abort or consume time.
  return Object.freeze(signal.aborted?{kind:'cancelled'}:!fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
 };
 let auth:Session,pinned:PendingAdminDetail;
 try{
  auth={account_id:session?.account_id,access_token:session?.access_token};
  if(!id(auth.account_id)||!token(auth.access_token))return finish({kind:'authentication_required'});
  pinned=pin(pending);
  if(pinned.account_id!==auth.account_id)return finish({kind:'invalid_request'});
 }catch{return finish({kind:'invalid_request'});}
 if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'superseded'});
 const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,body:ReadableStream<Uint8Array>|null|undefined;
 const cancelBody=()=>{try{const work=reader?reader.cancel():body?.cancel();if(work)void work.catch(()=>{});}catch{/* best effort for an owned transport */}};
 let stop!:(result:AdminDetailResult)=>void;const stopped=new Promise<AdminDetailResult>(resolve=>{stop=resolve;});
 const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};signal.addEventListener('abort',cancel,{once:true});
 const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<AdminDetailResult>=>{
  try{
   const data:AdminDetailData={url:'/api/v1/admin/captures/{capture_id}',path:{capture_id:pinned.capture_id}};
   const response=await request(data.url.replace('{capture_id}',data.path.capture_id),{method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
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
    size+=chunk.value.byteLength;if(size>524288)return invalid();chunks.push(chunk.value);
   }
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   let value:unknown;try{value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{return invalid();}
   return response.status===200?{kind:'loaded',snapshot:validateSnapshot(value,pinned)}:errorResult(response.status,value);
  }catch(error){return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
 };
 try{return finish(await Promise.race([work(),stopped]));}
 finally{clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
