/** Candidate only: one protected page, no cache, write, Auth or observation effects. */
import type {HistoryPage,HistoryCapturesData} from '../../contracts/history-generated/types.gen';
import type {Session} from './entry';
import type {SafeError} from './read';
import {id,token,object,strictJSON,date,instant,decimal,freeze,validateDetail,errorResult,InvalidResponse,invalid,type Frozen} from './read-validation.js';

export type PendingHistory=Readonly<{account_id:string;org_id:string;from_date:string;to_date:string;limit?:number;cursor?:string}>;
export type HistoryOptions={signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number};
export type HistoryResult=Readonly<{kind:'loaded';page:Frozen<HistoryPage>}>|SafeError|
 Readonly<{kind:'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>;
const permission='kdg_capture.capture.read.own';
const cursorKeys=['account_id','from_date','last_created_at','last_id','limit','org_id','permission','to_date','v'];
type Pinned=PendingHistory & {limit:number};
const canonical=(v:Record<string,unknown>)=>JSON.stringify(Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])));
function encode(v:Record<string,unknown>):string {return btoa(canonical(v)).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');}
function timestamp(v:unknown):string {
 if(typeof v!=='string'||!date(v.slice(0,10))||!/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.[0-9]{6})?Z(?![\s\S])/.test(v)||v.endsWith('.000000Z'))return invalid();
 return v.slice(0,19)+'.'+(v.slice(19,-1).replace('.','')).padEnd(6,'0')+'Z';
}
function cursor(raw:unknown,pinned:Pinned):Record<string,unknown> {
 if(typeof raw!=='string'||raw.length<1||raw.length>2048||!/^[A-Za-z0-9_-]+$/.test(raw))return invalid();
 let value:Record<string,unknown>;
 try{value=object(strictJSON(atob(raw.replaceAll('-','+').replaceAll('_','/')+'='.repeat((4-raw.length%4)%4))),cursorKeys);}catch{return invalid();}
 let encoded:string;try{encoded=encode(value);}catch{return invalid();}
 if(encoded!==raw||value.v!==1||value.permission!==permission||value.org_id!==pinned.org_id||value.account_id!==pinned.account_id||value.from_date!==pinned.from_date||value.to_date!==pinned.to_date||value.limit!==pinned.limit||!id(value.last_id))return invalid();
 timestamp(value.last_created_at);return value;
}
function compare(a:readonly [string,string],b:readonly [string,string]):number{return a[0]<b[0]?-1:a[0]>b[0]?1:a[1]<b[1]?-1:a[1]>b[1]?1:0;}
export function validateHistoryPage(value:unknown,pending:PendingHistory):Frozen<HistoryPage> {
 object(pending,['account_id','org_id','from_date','to_date'],['limit','cursor']);
 if(Object.hasOwn(pending,'limit')&&pending.limit===undefined)return invalid();
 const pinned={...pending,limit:pending.limit===undefined?30:pending.limit};
 if(!id(pinned.account_id)||!id(pinned.org_id)||!date(pinned.from_date)||!date(pinned.to_date)||pinned.from_date>pinned.to_date||!Number.isInteger(pinned.limit)||pinned.limit<1||pinned.limit>100)return invalid();
 if(Object.hasOwn(pending,'cursor'))cursor(pinned.cursor,pinned);
 const p=object(value,['observation','account_id','org_id','from_date','to_date','limit','items','next_cursor']);
 if(p.account_id!==pinned.account_id||p.org_id!==pinned.org_id||p.from_date!==pinned.from_date||p.to_date!==pinned.to_date||p.limit!==pinned.limit||!Array.isArray(p.items)||p.items.length>pinned.limit)return invalid();
 validateOwnReadObservation(p.observation,pinned.account_id,pinned.org_id);
 let previous:readonly [string,string]|undefined;
 if(pinned.cursor){const last=cursor(pinned.cursor,pinned);previous=[timestamp(last.last_created_at),last.last_id as string];}
 const seen=new Set<string>();let lastDetail:ReturnType<typeof validateDetail>|undefined;
 for(const item of p.items){
  if(!item||typeof item!=='object'||Array.isArray(item))return invalid();
  const d=validateDetail(item,{account_id:pinned.account_id,org_id:pinned.org_id,capture_id:object(item,['capture_id'],Object.keys(item as object)).capture_id as string});
  if(new TextEncoder().encode(JSON.stringify(item)).byteLength>524288||d.observation_date<pinned.from_date||d.observation_date>pinned.to_date||seen.has(d.capture_id))return invalid();
  const current=[timestamp(d.created_at),d.capture_id] as const;
  if(previous&&compare(current,previous)>=0)return invalid();previous=current;seen.add(d.capture_id);lastDetail=d;
 }
 if(p.next_cursor!==null){
  const next=cursor(p.next_cursor,pinned);
  if(!lastDetail||next.last_created_at!==lastDetail.created_at||next.last_id!==lastDetail.capture_id)return invalid();
 }
 return freeze(value as HistoryPage);
}


export function validateOwnReadObservation(value:unknown,account:string,org:string) {
 const o=object(value,['account_id','actor_id','membership_id','authorization_scope','resource_scope','permission','decision_id','checked_at','expires_at']);
 const a=object(o.authorization_scope,['kind','org_id']),r=object(o.resource_scope,['kind','account_id']);
 if(o.account_id!==account||!id(o.actor_id)||!decimal(o.membership_id)||!id(o.decision_id)||a.kind!=='organization'||a.org_id!==org||r.kind!=='own_account'||r.account_id!==account||o.permission!==permission||!instant(o.checked_at)||!instant(o.expires_at)||!o.checked_at.endsWith('Z')||!o.expires_at.endsWith('Z')||Date.parse(o.expires_at)-Date.parse(o.checked_at)!==604800000||o.checked_at.slice(19)!==o.expires_at.slice(19))return invalid();
 return o;
}

export async function historyCaptures(session:Session,pending:PendingHistory,options:HistoryOptions):Promise<HistoryResult> {
 let duration:number,signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch;
 try{
  duration=options?.timeoutMs??10000;signal=options.signal;isCurrent=options.isCurrent;request=options.request??fetch;
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function'||typeof request!=='function'||!Number.isFinite(duration)||duration<=0||duration>10000)return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const current=()=>{try{return isCurrent()===true;}catch{return false;}};
 const deadline=performance.now()+duration;
 const finish=(result:HistoryResult):HistoryResult=>{const fresh=current();return Object.freeze(signal.aborted?{kind:'cancelled'}:!fresh?{kind:'superseded'}:performance.now()>=deadline?{kind:'verification_unavailable'}:result);};
 let auth:Session,pinned:Pinned;
 try{
  auth={account_id:session?.account_id,access_token:session?.access_token};
  if(!id(auth.account_id)||!token(auth.access_token))return finish({kind:'authentication_required'});
  const captured={...pending};object(captured,['account_id','org_id','from_date','to_date'],['limit','cursor']);
  pinned={...captured,limit:captured.limit===undefined?30:captured.limit};
  if(pinned.account_id!==auth.account_id||!id(pinned.org_id)||!date(pinned.from_date)||!date(pinned.to_date)||pinned.from_date>pinned.to_date||!Number.isInteger(pinned.limit)||pinned.limit<1||pinned.limit>100)return finish({kind:'invalid_request'});
  if(Object.hasOwn(captured,'limit')&&captured.limit===undefined)return finish({kind:'invalid_request'});
  if(Object.hasOwn(captured,'cursor'))cursor(pinned.cursor,pinned);
 }catch{return finish({kind:'invalid_request'});}
 if(!current()||signal.aborted)return finish({kind:'superseded'});
 const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,body:ReadableStream<Uint8Array>|null|undefined;
 let stop!:(result:HistoryResult)=>void;const stopped=new Promise<HistoryResult>(resolve=>{stop=resolve;});
 const cancel=()=>{controller.abort();stop({kind:'cancelled'});};signal.addEventListener('abort',cancel,{once:true});
 const timer=setTimeout(()=>{controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<HistoryResult>=>{
  try{
   const data:HistoryCapturesData={url:'/api/v1/captures',query:{from_date:pinned.from_date,to_date:pinned.to_date,limit:pinned.limit,...(pinned.cursor?{cursor:pinned.cursor}:{})}};
   const query=new URLSearchParams(Object.entries(data.query!).map(([k,v])=>[k,String(v)]));
   const response=await request(data.url+'?'+query,{method:'GET',headers:{Authorization:'Bearer '+auth.access_token},credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error',signal:controller.signal});
   body=response.body;
   if(controller.signal.aborted){if(body)void body.cancel().catch(()=>{});return {kind:'cancelled'};}
   const cache=response.headers.get('cache-control')?.toLowerCase().split(',').map(v=>v.trim())??[];
   if(response.redirected||!body||response.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json'||!cache.includes('private')||!cache.includes('no-store'))return invalid();
   reader=body.getReader();const chunks:Uint8Array[]=[];let size=0;
   while(true){
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    const chunk=await reader.read();
    if(!current()||signal.aborted||performance.now()>=deadline)return finish({kind:'verification_unavailable'});
    if(chunk.done)break;if(!chunk.value.byteLength)continue;
    size+=chunk.value.byteLength;if(size>2097152)return invalid();chunks.push(chunk.value);
   }
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   let value:unknown;try{value=strictJSON(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{return invalid();}
   return response.status===200?{kind:'loaded',page:validateHistoryPage(value,pinned)}:errorResult(response.status,value);
  }catch(error){return {kind:error instanceof InvalidResponse?'invalid_response':'verification_unavailable'};}
 };
 try{return finish(await Promise.race([work(),stopped]));}
 finally{clearTimeout(timer);signal.removeEventListener('abort',cancel);controller.abort();if(reader)void reader.cancel().catch(()=>{});else if(body)void body.cancel().catch(()=>{});}
}
