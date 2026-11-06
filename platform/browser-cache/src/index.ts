/** Opt-in JSON reuse. Applications must authorize every read before showing bytes. */
export type JsonStorage=Pick<Storage,'length'|'key'|'getItem'|'setItem'|'removeItem'>;
export type CacheScope={app:string;api:string;account:string;format:number};
type Entry<T>={version:1;scope:CacheScope;path:string;etag:string;value:T;written:number};
export function createJsonCache<T=any>(options:CacheScope & {storage?:JsonStorage;maxEntries?:number;maxBytes?:number;validate?:(value:unknown,path:string)=>boolean}){
 const {app,api,account,format,storage,maxEntries=4,maxBytes=4_000_000}=options;
 const scope={app,api,account,format},scopeId=JSON.stringify(scope);
 const prefix='platform-json-cache:'+encodeURIComponent(app)+':';
 const ownPrefix=prefix+encodeURIComponent(scopeId)+':';
 const memory=new Map<string,Entry<T>>();let epoch=0;
 const key=(path:string)=>ownPrefix+encodeURIComponent(path);
 function keys(){try{return Array.from({length:storage?.length||0},(_,i)=>storage!.key(i)).filter((k):k is string=>Boolean(k?.startsWith(prefix)));}catch{return [];}}
 function remove(k:string){memory.delete(k);try{storage?.removeItem(k);}catch{/* Best effort on unavailable storage. */}}
 function decode(raw:string|null,k:string):Entry<T>|null{
  try{
   if(!raw||raw.length*2>maxBytes)return null;
   const item=JSON.parse(raw) as Entry<T>;
   if(item.version!==1||JSON.stringify(item.scope)!==scopeId||key(item.path)!==k||!/^W\/"[^"\r\n]+"$|^"[^"\r\n]+"$/.test(item.etag)||!Number.isFinite(item.written)||!('value' in item)||options.validate&&!options.validate(item.value,item.path))return null;
   return item;
  }catch{return null;}
 }
 function get(path:string):Entry<T>|null{
  const k=key(path);const hit=memory.get(k);if(hit)return hit;
  try{const raw=storage?.getItem(k)||null;const entry=decode(raw,k);if(entry){memory.set(k,entry);return entry;}if(raw)remove(k);}catch{/* A cache miss must still permit the network. */}
  return null;
 }
 function put(path:string,etag:string,value:T,operation:number){
  if(operation!==epoch)return;
  const entry:Entry<T>={version:1,scope,path,etag,value,written:Date.now()};
  let raw:string;try{raw=JSON.stringify(entry);}catch{return;}
  if(!decode(raw,key(path)))return;
  memory.delete(key(path));memory.set(key(path),entry);
  try{storage?.setItem(key(path),raw);}catch{/* Keep the successful response in memory. */}
  // Total limits include older formats/accounts for this app, not just this object.
  const rows=new Map<string,{written:number;bytes:number}>();
  for(const k of keys())try{const text=storage!.getItem(k);if(text){const item=JSON.parse(text);rows.set(k,{written:Number(item.written)||0,bytes:text.length*2});}}catch{remove(k);}
  for(const [k,v] of memory)rows.set(k,{written:v.written,bytes:JSON.stringify(v).length*2});
  let bytes=[...rows.values()].reduce((sum,v)=>sum+v.bytes,0);
  for(const [k,v] of [...rows].sort((a,b)=>a[1].written-b[1].written)){
   if(rows.size<=maxEntries&&bytes<=maxBytes)break;
   rows.delete(k);bytes-=v.bytes;remove(k);
  }
 }
 function clear(){epoch++;memory.clear();for(const k of keys())remove(k);}
 async function read(path:string,fetchAuthorized:(etag?:string)=>Promise<Response>,current:()=>boolean=()=>true):Promise<T>{
  const operation=epoch,previous=get(path);
  const requireCurrent=()=>{if(operation!==epoch||!current())throw new DOMException('Request changed','AbortError');};
  let response=await fetchAuthorized(previous?.etag);requireCurrent();
  if(response.status===304&&previous)return previous.value;
  // A validator response without usable bytes cannot be displayed.
  if(response.status===304){response=await fetchAuthorized();requireCurrent();}
  if(!response.ok)throw new Error('We could not read the collection. Please retry.');
  const value:unknown=await response.json();requireCurrent();
  if(options.validate&&!options.validate(value,path))throw new Error('We could not read the collection. Please retry.');
  const etag=response.headers.get('etag');if(etag)put(path,etag,value as T,operation);
  return value as T;
 }
 return {get,put,clear,read,operation:()=>epoch};
}

/** One total deadline includes fetch, refresh and response-body parsing. */
export async function withDeadline<T>(run:(signal:AbortSignal)=>Promise<T>,{signal,timeoutMs=15_000}:{signal?:AbortSignal;timeoutMs?:number}={}):Promise<T>{
 const controller=new AbortController();let timer:ReturnType<typeof setTimeout>|undefined;
 let stop:(reason:Error)=>void=()=>{};
 const failure=new Promise<never>((_,reject)=>{stop=reject});
 const abort=()=>{controller.abort();stop(new DOMException('Request cancelled','AbortError'));};
 if(signal?.aborted)abort();else signal?.addEventListener('abort',abort,{once:true});
 timer=setTimeout(()=>{controller.abort();stop(new Error('The request timed out. Please retry.'));},timeoutMs);
 try{return await Promise.race([failure,run(controller.signal)]);}
 finally{clearTimeout(timer);signal?.removeEventListener('abort',abort);}
}
