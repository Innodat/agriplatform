/** Inert aggregate consumer. isCurrent owns the caller's account/org/capture/page/session/access lease. */
import type {AuditDetails,AuditDetailsData,AuditDetailsErrors} from '../../contracts/audit-display-generated/types.gen';
import type {Session} from './entry';
import {type PendingAudit,type AuditOptions,pin,validatePage} from './audit.js';
import {id,token,object,strictJSON,text,freeze,errorResult,InvalidResponse,invalid,type Frozen} from './read-validation.js';
export type AuditDetailsError={[S in keyof AuditDetailsErrors]:Readonly<{kind:'error';status:S;error_id:AuditDetailsErrors[S]['error_id']}>}[keyof AuditDetailsErrors];
export type AuditDetailsResult=Readonly<{kind:'loaded';page:Frozen<AuditDetails>}>|AuditDetailsError|Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;
export type PendingAuditDetails=PendingAudit;
export type AuditDetailsOptions=AuditOptions;

// Measure each original JSON subtree, including whitespace/escapes, rather than
// trusting Content-Length or the smaller normalized parsed representation.
function subtreeBounds(raw:string):void {
 let depth=0,key='',start=0;
 for(const match of raw.matchAll(/"(?:\\[\s\S]|[^"\\])*"|[{}\[\]]/g)){
  const token=match[0];
  if(token.startsWith('"')){if(depth===1)key=JSON.parse(token);continue;}
  if(token==='{'||token==='['){if(depth===1)start=match.index;depth++;}
  else {depth--;if(depth===1){const size=new TextEncoder().encode(raw.slice(start,match.index+1)).byteLength;
   if((key==='audit'&&size>65536)||(key==='actor_display'&&size>262144))return invalid();
  }}
 }
}
function validate(value:unknown,pinned:ReturnType<typeof pin>,raw:string):Frozen<AuditDetails>{
 const aggregate=object(value,['audit','actor_display']);subtreeBounds(raw);
 const audit=validatePage(aggregate.audit,pinned);
 const displays=object(aggregate.actor_display,['status'],['labels']);
 if(displays.status==='temporarily_unavailable')object(displays,['status']);
 else if(displays.status==='loaded'){
  object(displays,['status','labels']);
  const actors=[...new Set([audit.owner_actor_id,audit.created_by,audit.updated_by,...audit.events.flatMap(e=>[e.executor_actor_id,...(e.initiator_actor_id===null?[]:[e.initiator_actor_id])])])].sort();
  if(!Array.isArray(displays.labels)||displays.labels.length!==actors.length||actors.length>203)return invalid();
  for(let i=0;i<actors.length;i++){
   const label=object(displays.labels[i],['actor_id','status'],['display_name']);
   if(!id(label.actor_id)||label.actor_id!==actors[i])return invalid();
   if(label.status==='unavailable')object(label,['actor_id','status']);
   else if(label.status==='resolved'){
    object(label,['actor_id','status','display_name']);
    if(!text(label.display_name,256,true)||new TextEncoder().encode(label.display_name).byteLength>1024||/[\p{Cc}\p{Cs}]/u.test(label.display_name))return invalid();
   }else return invalid();
  }
 }else return invalid();
 return freeze(value as AuditDetails);
}
export async function auditDetails(session:Session,pending:PendingAuditDetails,options:AuditDetailsOptions):Promise<AuditDetailsResult> {
 let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
 try{
  object(options,['signal','isCurrent'],['request','timeoutMs']);
  duration=options.timeoutMs===undefined?10000:options.timeoutMs;signal=options.signal;isCurrent=options.isCurrent;request=options.request===undefined?fetch:options.request;
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const deadline=performance.now()+duration;
 const current=()=>{try{return isCurrent()===true;}catch{return false;}};
 const finish=(result:AuditDetailsResult):AuditDetailsResult=>{
  const fresh=current(); // A caller predicate can synchronously abort or consume time.
  return Object.freeze(signal.aborted?{kind:'cancelled'}:!fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);
 };
 let auth:Session,pinned:ReturnType<typeof pin>;
 try{
  auth={account_id:session?.account_id,access_token:session?.access_token};
  if(!id(auth.account_id)||!token(auth.access_token))return finish({kind:'authentication_required'});
  pinned=pin(pending);
  if(pinned.account_id!==auth.account_id)return finish({kind:'invalid_request'});
 }catch{return finish({kind:'invalid_request'});}
 if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'superseded'});
 const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,body:ReadableStream<Uint8Array>|null|undefined;
 const cancelBody=()=>{try{const work=reader?reader.cancel():body?.cancel();if(work)void work.catch(()=>{});}catch{/* best effort for an owned transport */}};
 let stop!:(result:AuditDetailsResult)=>void;const stopped=new Promise<AuditDetailsResult>(resolve=>{stop=resolve;});
 const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};signal.addEventListener('abort',cancel,{once:true});
 const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<AuditDetailsResult>=>{
  try{
   const data:AuditDetailsData={url:'/api/v1/admin/captures/{capture_id}/audit-details',path:{capture_id:pinned.capture_id},query:{limit:pinned.limit,...(pinned.cursor?{cursor:pinned.cursor}:{})}};
   const query=new URLSearchParams(Object.entries(data.query!).map(([key,value])=>[key,String(value)]));
   const response=await request(data.url.replace('{capture_id}',data.path.capture_id)+'?'+query,{method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
   body=response.body;
   if(controller.signal.aborted){cancelBody();return {kind:'cancelled'};}
   const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(value=>value.trim())??[];
   if(response.redirected||!body||response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json'||!cache.includes('private')||!cache.includes('no-store')||cache.some(v=>['public','max-age','s-maxage'].includes(v.split('=')[0]))||!['','identity'].includes(response.headers.get('content-encoding')?.trim().toLowerCase()??''))return invalid();
   reader=body.getReader();const chunks:Uint8Array[]=[];let size=0;
   while(true){
    // Immediate empty read promises can starve timer tasks; check the original
    // monotonic deadline on both sides of every read as well as at publication.
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    const chunk=await reader.read();
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    if(chunk.done)break;if(!chunk.value.byteLength)continue;
    size+=chunk.value.byteLength;if(size>328704)return invalid();chunks.push(chunk.value);
   }
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   let value:unknown,raw:string;try{raw=new TextDecoder('utf-8',{fatal:true}).decode(bytes);value=strictJSON(raw);}catch{return invalid();}
   return response.status===200?{kind:'loaded',page:validate(value,pinned,raw)}:errorResult(response.status,value);
  }catch(error){return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
 };
 try{return finish(await Promise.race([work(),stopped]));}
 finally{clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
