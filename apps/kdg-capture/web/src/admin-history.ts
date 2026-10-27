/** One explicit current organization page; no admission, persistence or pagination effects. */
import type {AdminHistoryResponse,AdminHistoryData,AdminHistoryErrors} from '../../contracts/admin-generated/types.gen';
import type {Session} from './entry';
import {id,token,object,strictJSON,date,freeze,validateDetail,errorResult,InvalidResponse,invalid,type Frozen} from './read-validation.js';
export type PendingAdminHistory=Readonly<{account_id:string;org_id:string;from_date:string;to_date:string;limit?:number;cursor?:string}>;
export type AdminHistoryOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
export type AdminHistoryError={[S in keyof AdminHistoryErrors]:Readonly<{kind:'error';status:S;error_id:AdminHistoryErrors[S]['error_id']}>}[keyof AdminHistoryErrors];
export type AdminHistoryResult=Readonly<{kind:'loaded';page:Frozen<AdminHistoryResponse>}>|AdminHistoryError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;
type Pinned=PendingAdminHistory & {limit:number};
const permission='kdg_capture.capture.read.all';
const cursorKeys=['account_id','from_date','last_created_at','last_id','limit','org_id','permission','to_date','v'];

// Match the owner's UTC datetime.isoformat spelling; normalize only for comparison.
// Millisecond Date comparisons would lose the final three position digits.
function timestamp(value:unknown):string {
 if(typeof value!=='string'||!date(value.slice(0,10))||!/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.[0-9]{6})?Z(?![\s\S])/.test(value)||value.endsWith('.000000Z'))return invalid();
 return value.slice(0,19)+'.'+value.slice(19,-1).replace('.','').padEnd(6,'0')+'Z';
}
function cursor(raw:unknown,pinned:Pinned):Record<string,unknown> {
 if(typeof raw!=='string'||raw.length<1||raw.length>2048||!/^[A-Za-z0-9_-]+$/.test(raw))return invalid();
 try{
  const value=object(strictJSON(atob(raw.replaceAll('-','+').replaceAll('_','/')+'='.repeat((4-raw.length%4)%4))),cursorKeys);
  const canonical=JSON.stringify(Object.fromEntries(Object.keys(value).sort().map(key=>[key,value[key]])));
  const encoded=btoa(canonical).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
  if(encoded!==raw||value.v!==1||value.permission!==permission||value.account_id!==pinned.account_id||value.org_id!==pinned.org_id||value.from_date!==pinned.from_date||value.to_date!==pinned.to_date||value.limit!==pinned.limit||!id(value.last_id))return invalid();
  timestamp(value.last_created_at);return value;
 }catch{return invalid();}
}
function pin(value:PendingAdminHistory):Pinned {
 // This private primitive copy is the sole request/validation context after awaits.
 const captured={...value};object(captured,['account_id','org_id','from_date','to_date'],['limit','cursor']);
 if(Object.hasOwn(captured,'limit')&&captured.limit===undefined)return invalid();
 const pinned={...captured,limit:captured.limit===undefined?30:captured.limit};
 if(!id(pinned.account_id)||!id(pinned.org_id)||!date(pinned.from_date)||!date(pinned.to_date)||pinned.from_date>pinned.to_date||!Number.isInteger(pinned.limit)||pinned.limit<1||pinned.limit>100)return invalid();
 if(Object.hasOwn(captured,'cursor'))cursor(pinned.cursor,pinned);
 return pinned;
}
function compare(a:readonly [string,string],b:readonly [string,string]):number {
 return a[0]<b[0]?-1:a[0]>b[0]?1:a[1]<b[1]?-1:a[1]>b[1]?1:0;
}
function validatePage(value:unknown,pinned:Pinned):Frozen<AdminHistoryResponse> {
 const page=object(value,['account_id','org_id','from_date','to_date','limit','items','next_cursor']);
 if(page.account_id!==pinned.account_id||page.org_id!==pinned.org_id||page.from_date!==pinned.from_date||page.to_date!==pinned.to_date||page.limit!==pinned.limit||!Array.isArray(page.items)||page.items.length>pinned.limit)return invalid();
 let previous:readonly [string,string]|undefined;
 if(pinned.cursor){const last=cursor(pinned.cursor,pinned);previous=[timestamp(last.last_created_at),last.last_id as string];}
 const seen=new Set<string>();let lastDetail:ReturnType<typeof validateDetail>|undefined;
 for(const item of page.items){
  if(!item||typeof item!=='object'||Array.isArray(item))return invalid();
  const {owner_account_id:owner,capture_id:capture}=item as Record<string,unknown>;
  // All-read reader identity is never substituted for original ownership.
  if(!id(owner)||!id(capture))return invalid();
  const detail=validateDetail(item,{account_id:owner,org_id:pinned.org_id,capture_id:capture});
  if(new TextEncoder().encode(JSON.stringify(item)).byteLength>524288||detail.observation_date<pinned.from_date||detail.observation_date>pinned.to_date||seen.has(detail.capture_id))return invalid();
  const position=[timestamp(detail.created_at),detail.capture_id] as const;
  if(previous&&compare(position,previous)>=0)return invalid();
  previous=position;seen.add(detail.capture_id);lastDetail=detail;
 }
 if(page.next_cursor!==null){
  const next=cursor(page.next_cursor,pinned);
  // Byte trimming can return fewer than limit rows. Never skip an omitted row.
  if(!lastDetail||next.last_created_at!==lastDetail.created_at||next.last_id!==lastDetail.capture_id)return invalid();
 }
 return freeze(value as AdminHistoryResponse);
}

export async function adminHistoryCaptures(session:Session,pending:PendingAdminHistory,options:AdminHistoryOptions):Promise<AdminHistoryResult> {
 let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
 try{
  object(options,['signal','isCurrent'],['request','timeoutMs']);
  duration=options.timeoutMs===undefined?10000:options.timeoutMs;signal=options.signal;isCurrent=options.isCurrent;request=options.request===undefined?fetch:options.request;
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const deadline=performance.now()+duration;
 const current=()=>{try{return isCurrent()===true;}catch{return false;}};
 const finish=(result:AdminHistoryResult):AdminHistoryResult=>{
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
 let stop!:(result:AdminHistoryResult)=>void;const stopped=new Promise<AdminHistoryResult>(resolve=>{stop=resolve;});
 const cancel=()=>{controller.abort();cancelBody();stop({kind:'cancelled'});};signal.addEventListener('abort',cancel,{once:true});
 const timer=setTimeout(()=>{controller.abort();cancelBody();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<AdminHistoryResult>=>{
  try{
   const data:AdminHistoryData={url:'/api/v1/admin/captures',query:{from_date:pinned.from_date,to_date:pinned.to_date,limit:pinned.limit,...(pinned.cursor?{cursor:pinned.cursor}:{})}};
   const query=new URLSearchParams(Object.entries(data.query).map(([key,value])=>[key,String(value)]));
   const response=await request(data.url+'?'+query,{method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
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
    size+=chunk.value.byteLength;if(size>2097152)return invalid();chunks.push(chunk.value);
   }
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   let value:unknown;try{value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{return invalid();}
   return response.status===200?{kind:'loaded',page:validatePage(value,pinned)}:errorResult(response.status,value);
  }catch(error){return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
 };
 try{return finish(await Promise.race([work(),stopped]));}
 finally{clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();cancelBody();}
}
