// Owner API adapter. Every business request goes through Leave; no browser database access.
import type {Organization as WireOrganization,Organizations as WireOrganizations,Receipt as WireReceipt,SelectionResult as WireSelectionResult,Unresolved as WireUnresolved,Language as WireLanguage} from './generated/types.gen';
export type Organization=Readonly<WireOrganization>;
export type Organizations=Readonly<Omit<WireOrganizations,'organizations'>&{organizations:readonly Organization[]}>;
export type Receipt=Readonly<Required<Omit<WireReceipt,'result'>>&{result:Readonly<Required<WireSelectionResult>>}>;
export type Unresolved=Readonly<Required<WireUnresolved>>;
export type Language=Readonly<WireLanguage>;
export type Result<T>=Readonly<{ok:true;value:T}>|Readonly<{ok:false;error_id:string}>;
const object=(v:unknown,keys:string[]):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join()===keys.sort().join();
export const id=(v:unknown):v is string=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(v)&&v!=='00000000-0000-0000-0000-000000000000';
const revision=(v:unknown):v is string=>typeof v==='string'&&/^(0|[1-9][0-9]{0,18})$/.test(v)&&BigInt(v)<=9223372036854775807n;
export function createLeaveClient(request:typeof fetch=fetch){
 async function call<T>(path:string,token:string,signal:AbortSignal,validate:(v:unknown)=>v is T,method='GET',body?:unknown):Promise<Result<T>>{
  const controller=new AbortController(),abort=()=>controller.abort();signal.addEventListener('abort',abort,{once:true});if(signal.aborted)abort();const timer=setTimeout(abort,method==='POST'?12000:10000);
  try{
   const response=await request('/api'+path,{method,signal:controller.signal,headers:{Authorization:'Bearer '+token,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,cache:'no-store',redirect:'error'});
   if(controller.signal.aborted)throw Error();
   const reader=response.body?.getReader();if(!reader)throw Error();let raw='',bytes=0;const decoder=new TextDecoder('utf-8',{fatal:true});
   try{while(true){const part=await reader.read();if(part.done)break;bytes+=part.value.length;if(bytes>65536||controller.signal.aborted)throw Error();raw+=decoder.decode(part.value,{stream:true});}raw+=decoder.decode();}finally{void reader.cancel().catch(()=>{});}
   const value:unknown=JSON.parse(raw);
   if(controller.signal.aborted)throw Error();
   if(response.status===200||response.status===202){if(!validate(value))return{ok:false,error_id:'invalid_response'};return{ok:true,value};}
   if(object(value,['error_id','error','details'])&&typeof value.error_id==='string'&&typeof value.error==='string'&&object(value.details,[])&&[401,403,409,422,503].includes(response.status))return{ok:false,error_id:value.error_id};
   return{ok:false,error_id:'invalid_response'};
  }catch{return{ok:false,error_id:signal.aborted?'cancelled':'api_unavailable'};}
  finally{clearTimeout(timer);signal.removeEventListener('abort',abort);controller.abort();}
 }
 const language=(v:unknown):v is Language=>object(v,['preferred_locale','revision'])&&['en','pt'].includes(String(v.preferred_locale))&&revision(v.revision);
 const outcome=(org:string,operation:string)=>(v:unknown):v is Receipt|Unresolved=>object(v,['operation_id','status'])&&v.operation_id===operation&&v.status==='unresolved'||object(v,['operation_id','status','result'])&&v.operation_id===operation&&v.status==='committed'&&object(v.result,['command','org_id','event_id'])&&v.result.command==='select_organization'&&v.result.org_id===org&&id(v.result.event_id);
 return{
  async organizations(token:string,signal:AbortSignal):Promise<Result<Organizations>>{
   const all:Organization[]=[];let cursor:string|null=null;const seen=new Set<string>();
   do{
    const result:Result<Organizations>=await call('/v1/me/organizations'+(cursor?'?cursor='+encodeURIComponent(cursor):''),token,signal,(v:unknown):v is Organizations=>object(v,['organizations','next_cursor'])&&Array.isArray(v.organizations)&&v.organizations.length<=100&&v.organizations.every(o=>object(o,['org_id','name','membership_id'])&&id(o.org_id)&&typeof o.name==='string'&&o.name.length<=4096&&revision(o.membership_id)&&o.membership_id!=='0')&&(v.next_cursor===null||typeof v.next_cursor==='string'&&/^[A-Za-z0-9_-]{48}$/.test(v.next_cursor)));
    if(!result.ok)return result;
    for(const org of result.value.organizations){if(org.org_id<=(all.at(-1)?.org_id??''))return{ok:false,error_id:'invalid_response'};all.push(org);}
    cursor=result.value.next_cursor;
    if(cursor){if(seen.has(cursor)||!all.length||cursor!==btoa(all.at(-1)!.org_id).replaceAll('+','-').replaceAll('/','_').replaceAll('=',''))return{ok:false,error_id:'invalid_response'};seen.add(cursor);}
    if(all.length>10000)return{ok:false,error_id:'invalid_response'};
   }while(cursor);
   return{ok:true,value:{organizations:all,next_cursor:null}};
  },
  select:(token:string,signal:AbortSignal,org:string,operation:string)=>call('/v1/organizations/'+org+'/context/selection',token,signal,outcome(org,operation),'POST',{operation_id:operation}),
  lookup:(token:string,signal:AbortSignal,org:string,operation:string)=>call('/v1/organizations/'+org+'/context/operations/'+operation,token,signal,outcome(org,operation)),
  language:(token:string,signal:AbortSignal)=>call('/v1/me/preferences/language',token,signal,language),
  setLanguage:(token:string,signal:AbortSignal,command:{operation_id:string;expected_revision:string;preferred_locale:'en'|'pt'})=>call('/v1/me/preferences/language',token,signal,language,'PUT',command),
 };
}
export type LeaveClient=ReturnType<typeof createLeaveClient>;
