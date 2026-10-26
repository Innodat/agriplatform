/** Closed metadata only. Never pass view maps, Auth responses or editor lanes here. */
import {parseSnapshot, record, type Snapshot} from './reader-layout';
export type DeviceTab = Snapshot & {incarnation:string;invalid:boolean};
export type PublicSetup = {v:1;updated:number;activeTabKey:string;tabs:DeviceTab[]};
export type PrivateSelection = {tabKey:string;incarnation:string;study?:string;note?:string;label?:string};
export type PrivateSetup = {v:1;updated:number;completed?:number;account:string;tabs:PrivateSelection[]};
export const workspaceDatabase = `scribeswell-workspace:${import.meta.env.BASE_URL}`;
const store='metadata',ttl=30*86400000;
const key=(x:unknown):x is string=>typeof x==='string'&&x.length>0&&x.length<=128;
export const accountId=(x:unknown):x is string=>typeof x==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(x);
const closed=(x:Record<string,unknown>,allowed:string[],required=allowed)=>Object.keys(x).every(k=>allowed.includes(k))&&required.every(k=>Object.prototype.hasOwnProperty.call(x,k));
const bytes=(x:unknown)=>new TextEncoder().encode(JSON.stringify(x)).length;
const timestamp=(x:unknown,now:number)=>typeof x==='number'&&Number.isFinite(x)&&x>=0&&x<=now&&now-x<ttl;
export const isFuture=(x:unknown)=>record(x)&&typeof x.v==='number'&&x.v>1;
export function parsePublic(x:unknown,now=Date.now()):PublicSetup|undefined{
 try{
  if(!record(x)||!closed(x,['v','updated','activeTabKey','tabs'])||x.v!==1||!timestamp(x.updated,now)||bytes(x)>96*1024||!key(x.activeTabKey)||!Array.isArray(x.tabs)||x.tabs.length<1||x.tabs.length>12)return;
  const seen=new Set<string>();
  for(const t of x.tabs){
   if(!record(t)||!closed(t,['v','tabKey','activePaneKey','panes','incarnation','invalid'])||!key(t.incarnation)||typeof t.invalid!=='boolean'||!Array.isArray(t.panes)||t.panes.length<1||t.panes.length>4||seen.has(String(t.tabKey)))return;
   const snapshot={v:t.v,tabKey:t.tabKey,activePaneKey:t.activePaneKey,panes:t.panes};
   const active=t.panes.findIndex(p=>record(p)&&p.paneKey===t.activePaneKey);
   if(!parseSnapshot(snapshot,{refs:t.panes.map(p=>p.ref),active,invalid:t.invalid}))return;
   seen.add(String(t.tabKey));
  }
  if(!seen.has(x.activeTabKey))return;
  return x as PublicSetup;
 }catch{return;}
}
export function parsePrivate(x:unknown,now=Date.now()):PrivateSetup|undefined{
 try{
  if(!record(x)||!closed(x,['v','updated','completed','account','tabs'],['v','updated','account','tabs'])||x.v!==1||x.completed!==undefined&&(!Number.isSafeInteger(x.completed)||typeof x.completed!=='number'||x.completed<1)||!timestamp(x.updated,now)||bytes(x)>32*1024||!accountId(x.account)||!Array.isArray(x.tabs)||x.tabs.length>12)return;
  const seen=new Set<string>();
  for(const t of x.tabs){
   if(!record(t)||!closed(t,['tabKey','incarnation','study','note','label'],['tabKey','incarnation'])||!key(t.tabKey)||!key(t.incarnation)||seen.has(t.tabKey)||t.study!==undefined&&!accountId(t.study)||t.note!==undefined&&(!accountId(t.note)||!t.study)||t.label!==undefined&&(typeof t.label!=='string'||t.label!==t.label.trim()||Array.from(t.label).length<1||Array.from(t.label).length>80||/[\p{Cc}\p{Cs}]/u.test(t.label)))return;
   seen.add(t.tabKey);
  }
  return x as PrivateSetup;
 }catch{return;}
}
export class WorkspaceStorageFailure extends Error {constructor(public reason:'unavailable'|'future'|'invalid'='unavailable'){super('Reading setup not remembered');}}
/** Each operation includes open and transaction in one deadline. Timed-out opens are closed. */
async function transaction<T>(mode:IDBTransactionMode,action:(store:IDBObjectStore,finish:(value:T)=>void,fail:(error:unknown)=>void)=>void):Promise<T>{
 return new Promise((resolve,reject)=>{
  let done=false,db:IDBDatabase|undefined,tx:IDBTransaction|undefined,value:T;
  const finish=(error?:unknown)=>{if(done)return;done=true;clearTimeout(timer);if(error){try{tx?.abort();}catch{/* already finished */}reject(error);}else resolve(value);db?.close();};
  const timer=setTimeout(()=>finish(new WorkspaceStorageFailure()),3000);
  try{
   const open=indexedDB.open(workspaceDatabase,1);
   open.onupgradeneeded=()=>{if(done){open.transaction?.abort();return;}if(!open.result.objectStoreNames.contains(store))open.result.createObjectStore(store);};
   open.onblocked=()=>finish(new WorkspaceStorageFailure());open.onerror=()=>finish(new WorkspaceStorageFailure());
   open.onsuccess=()=>{
    if(done){open.result.close();return;}db=open.result;db.onversionchange=()=>db?.close();
    try{tx=db.transaction(store,mode);tx.oncomplete=()=>finish();tx.onabort=tx.onerror=()=>finish(new WorkspaceStorageFailure());action(tx.objectStore(store),next=>{value=next;},error=>finish(error));}catch{finish(new WorkspaceStorageFailure());}
   };
  }catch{finish(new WorkspaceStorageFailure());}
 });
}
export async function readWorkspace(account?:string):Promise<{public?:PublicSetup;private?:PrivateSetup}>{
 return transaction('readonly',(object,finish,fail)=>{
  const request=object.getAll(undefined,5),keys=object.getAllKeys(undefined,5);let values:unknown[]|undefined,names:IDBValidKey[]|undefined;
  const complete=()=>{if(!values||!names)return;if(values.length>4){fail(new WorkspaceStorageFailure('invalid'));return;}if(values.some(isFuture)){fail(new WorkspaceStorageFailure('future'));return;}const p=values[names.indexOf('public')],a=account?values[names.indexOf(`account:${account}`)]:undefined;finish({public:parsePublic(p),private:parsePrivate(a)});};
  request.onsuccess=()=>{values=request.result;complete();};keys.onsuccess=()=>{names=keys.result;complete();};
 });
}
async function commitWorkspace(publicSetup:PublicSetup,privateSetup?:PrivateSetup):Promise<void>{
 // Revalidate caller projections and cross-window future records inside the write transaction.
 const operation=async()=>{
  if(!parsePublic(publicSetup)||privateSetup&&!parsePrivate(privateSetup))throw new WorkspaceStorageFailure('invalid');
  await transaction<void>('readwrite',(object,finish,fail)=>{
   const request=object.getAll(undefined,5),keys=object.getAllKeys(undefined,5);let values:unknown[]|undefined,names:IDBValidKey[]|undefined;
   const complete=()=>{
    if(!values||!names)return;
    if(values.length>4){fail(new WorkspaceStorageFailure('invalid'));return;}if(values.some(isFuture)){fail(new WorkspaceStorageFailure('future'));return;}
    const completedRecords=values.map((value,i)=>({value:record(value)&&typeof value.updated==='number'?parsePrivate(value,value.updated):undefined,key:names![i]}));
    const completed=1+Math.max(0,...completedRecords.map(item=>item.value?.completed??0));
    if(privateSetup&&!Number.isSafeInteger(completed)){fail(new WorkspaceStorageFailure('invalid'));return;}
    const now=Date.now();
    object.put({...publicSetup,updated:now},'public');
    if(privateSetup){
     object.put({...privateSetup,updated:now,completed},`account:${privateSetup.account}`);
     const others=completedRecords.filter(item=>typeof item.key==='string'&&item.key.startsWith('account:')&&item.key!==`account:${privateSetup.account}`).sort((a,b)=>(b.value?.completed??0)-(a.value?.completed??0)||(b.value?.updated??0)-(a.value?.updated??0));
     for(const item of others.slice(2))object.delete(item.key);
    }
    finish();
   };
   request.onsuccess=()=>{values=request.result;complete();};keys.onsuccess=()=>{names=keys.result;complete();};
  });
 };
 return operation();
}
type PendingWrite={publicSetup:PublicSetup;privateSetup?:PrivateSetup;waiters:{resolve:()=>void;reject:(error:unknown)=>void}[]};
const pendingWrites:PendingWrite[]=[];let running=false;
async function drainWrites(){
 if(running)return;running=true;
 try{while(pendingWrites.length){const next=pendingWrites.shift()!;try{await commitWorkspace(next.publicSetup,next.privateSetup);for(const waiter of next.waiters)waiter.resolve();}catch(error){for(const waiter of next.waiters)waiter.reject(error);}}}
 finally{running=false;}
}
/** Bounded admission: one executing batch, eight pending owner batches, 64 waiters each.
 * Success acknowledges the latest projection in an accepted same-owner batch. */
export function writeWorkspace(publicSetup:PublicSetup,privateSetup?:PrivateSetup):Promise<void>{
 return new Promise((resolve,reject)=>{if(pendingWrites.length>=8){reject(new WorkspaceStorageFailure());return;}const tail=pendingWrites[pendingWrites.length-1],next={publicSetup,privateSetup,waiters:[{resolve,reject}]};if(tail&&tail.privateSetup?.account===privateSetup?.account){if(tail.waiters.length>=64){reject(new WorkspaceStorageFailure());return;}next.waiters.unshift(...tail.waiters);pendingWrites[pendingWrites.length-1]=next;}else {if(pendingWrites.length>=8){reject(new WorkspaceStorageFailure());return;}pendingWrites.push(next);}void drainWrites();});
}
