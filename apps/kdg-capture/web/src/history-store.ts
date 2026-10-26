/** Isolated KDG cache. Explicit caller-owned lifetime; no startup or queue integration. */
import {request,complete} from '../offline-tools/idb.js';
import type {HistoryPage} from '../../contracts/history-generated/types.gen';
import {validateHistoryPage,validateOwnReadObservation,type PendingHistory} from './history.js';
import {id,freeze,type Frozen} from './read-validation.js';
export const HISTORY_DATABASE='kdg-own-history-v1';
const tables=['records','definitions','partitions','downloads'];
const week=604800000;
type Fence={generation:number;transactions:Set<IDBTransaction>;wall:number;mono:number;knownLock:boolean;clockLock:boolean;lockedCheckedAt:number;deniedAt:number};
type Execution=Readonly<{signal?:AbortSignal;isCurrent?:()=>boolean}>;
class ClockFailure extends Error {constructor(readonly observation:any){super('unavailable');}}
const fences=new Map<string,Fence>();
const canonical=(v:unknown):string=>JSON.stringify(v&&typeof v==='object'?Array.isArray(v)?v.map(x=>JSON.parse(canonical(x))):Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b)).map(([k,x])=>[k,JSON.parse(canonical(x))])):v);
const result=<const K extends string>(kind:K)=>Object.freeze({kind});
export function phoneHistoryDates(today=new Date()):Readonly<{from_date:string;to_date:string}>{
 if(!Number.isFinite(today.getTime()))throw Error('invalid_date');
 const day=(d:Date)=>`${String(d.getFullYear()).padStart(4,'0')}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
 const previous=new Date(today.getFullYear(),today.getMonth(),today.getDate()-29);
 return Object.freeze({from_date:day(previous),to_date:day(today)});
}
export async function openHistoryStore(scope:Readonly<{account_id:string;org_id:string}>,options:Readonly<{database?:string;indexedDB?:IDBFactory;wall?:()=>number;monotonic?:()=>number}>={}) {
 const {account_id,org_id}=scope;if(!id(account_id)||!id(org_id))throw Error('invalid_scope');
 const partition=account_id+'/'+org_id,wall=options.wall??Date.now,mono=options.monotonic??(()=>performance.now());
 const factory=options.indexedDB??indexedDB;
 const opening=factory.open(options.database??HISTORY_DATABASE,1);
 opening.onupgradeneeded=()=>{for(const name of tables)opening.result.createObjectStore(name,{keyPath:'key'});};
 const db=await request(opening);db.onversionchange=()=>db.close();
 const fenceKey=(options.database??HISTORY_DATABASE)+'/'+partition;
 let fence=fences.get(fenceKey);if(!fence){fence={generation:0,transactions:new Set(),wall:wall(),mono:mono(),knownLock:false,clockLock:false,lockedCheckedAt:0,deniedAt:0};fences.set(fenceKey,fence);}
 const shared=fence,generation=shared.generation;let closed=false;const ownTransactions=new Set<IDBTransaction>();
 let initialMeta:any;
 try{
  const initial=db.transaction('partitions','readonly'),done=complete(initial);void done.catch(()=>{});
  try{initialMeta=await request<any>(initial.objectStore('partitions').get(partition));await done;}
  catch{try{initial.abort();}catch{}await done.catch(()=>{});throw Error('unavailable');}
 }catch{db.close();throw Error('unavailable');}
 const epoch=initialMeta?.epoch??0;
 const current=()=>!closed&&shared.generation===generation;
 function sensible(observation:any,watermark:number,recovery=false){
  validateOwnReadObservation(observation,account_id,org_id);
  const now=wall(),tick=mono(),elapsed=tick-shared.mono,delta=now-shared.wall;
  if(!Number.isFinite(now)||!Number.isFinite(tick)||(!recovery&&(elapsed<0||delta<0||Math.abs(delta-elapsed)>60000||now<watermark))||now<Date.parse(observation.checked_at)||now>=Date.parse(observation.expires_at)||Date.parse(observation.expires_at)-Date.parse(observation.checked_at)!==week){
   shared.knownLock=true;shared.clockLock=true;shared.lockedCheckedAt=Math.max(shared.lockedCheckedAt,Date.parse(observation.checked_at));throw new ClockFailure(observation);
  }
  return {now,tick};
 }
 async function transaction<T>(fn:(tx:IDBTransaction,check:()=>void)=>Promise<T>,execution:Execution={}):Promise<T>{
  if(!current())throw Error('closed');const tx=db.transaction(tables,'readwrite');shared.transactions.add(tx);ownTransactions.add(tx);const done=complete(tx);void done.catch(()=>{});
  const abort=()=>{try{tx.abort();}catch{}};
  const check=()=>{let fresh=false;try{fresh=current()&&!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
   if(!fresh){abort();throw Error('closed');}};
  execution.signal?.addEventListener('abort',abort,{once:true});
  try{check();const value=await fn(tx,check);check();await done;check();return value;}
  catch(error){abort();await done.catch(()=>{});if(error instanceof ClockFailure)throw error;throw Error('unavailable');}
  finally{execution.signal?.removeEventListener('abort',abort);shared.transactions.delete(tx);ownTransactions.delete(tx);}
 }
 async function clockLock(observation:any){
  // The process latch is already set. Persist it separately from the aborted read/import.
  try{const tx=db.transaction('partitions','readwrite'),done=complete(tx);void done.catch(()=>{});const store=tx.objectStore('partitions');
   try{const meta=await request<any>(store.get(partition));if(!current()||(meta?.epoch??0)!==epoch){tx.abort();await done.catch(()=>{});return;}
    store.put({...meta,key:partition,epoch,clockLocked:true,lockedCheckedAt:Math.max(meta?.lockedCheckedAt??0,Date.parse(observation.checked_at))});await done;
   }catch{try{tx.abort();}catch{}await done.catch(()=>{});}
  }catch{/* A failed durable write never clears the known process lock. */}
 }
 async function lock(pinned:Readonly<{account_id:string;org_id:string}>={account_id,org_id},execution:Execution={}){
  let fresh=false;try{fresh=current()&&pinned.account_id===account_id&&pinned.org_id===org_id&&!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
  if(!fresh)return result('unavailable');
  try{const tx=db.transaction('partitions','readwrite'),done=complete(tx);void done.catch(()=>{});const store=tx.objectStore('partitions');
   try{const meta=await request<any>(store.get(partition));
    let valid=false;try{valid=current()&&(meta?.epoch??0)===epoch&&!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
    if(!valid){tx.abort();await done.catch(()=>{});return result('unavailable');}
    // A confirmed current known denial latches before its durable write can fail.
    shared.knownLock=true;shared.deniedAt=wall();shared.lockedCheckedAt=Math.max(shared.lockedCheckedAt,Date.parse(meta?.observation?.checked_at??'')||0);
    shared.generation++;for(const active of shared.transactions)try{active.abort();}catch{}
    store.put({...meta,key:partition,epoch:epoch+1,denied:true,deniedAt:shared.deniedAt});await done;return result('locked');
   }catch{try{tx.abort();}catch{}await done.catch(()=>{});return result('unavailable');}
  }catch{return result('unavailable');}
 }
 return {
  async importPage(value:unknown,pending:PendingHistory,configuration:Readonly<{restoreDenied?:boolean;signal?:AbortSignal;isCurrent?:()=>boolean}>={}) {
   try{
    if(pending.account_id!==account_id||pending.org_id!==org_id)return result('unavailable');
    const page=validateHistoryPage(structuredClone(value),pending);
    const committed=await transaction(async(tx,check)=>{
     const partitions=tx.objectStore('partitions'),meta=await request<any>(partitions.get(partition));check();
     if((meta?.epoch??0)!==epoch)throw Error('superseded');
     const locked=meta?.denied||meta?.clockLocked||shared.knownLock;
     if(locked&&!configuration.restoreDenied)throw Error('locked');
     const checked=Date.parse(page.observation.checked_at);
     if(locked&&(checked<=Math.max(meta?.lockedCheckedAt??0,shared.lockedCheckedAt)||checked<Math.max(meta?.deniedAt??0,shared.deniedAt)))throw Error('locked');
     const {now,tick}=sensible(page.observation,meta?.wall??0,!!locked);
     const downloads=tx.objectStore('downloads'),key=partition+'/'+page.from_date+'/'+page.to_date+'/'+page.limit;
     const old=await request<any>(downloads.get(key));check();
     const token=pending.cursor??'',seen=token?(old?.pages??{}):{};
     if(token&&(!old||(!Object.hasOwn(seen,token)&&old.next_cursor!==token)))throw Error('chain');
     if(Object.hasOwn(seen,token)&&seen[token]!==page.next_cursor)throw Error('chain');
     for(const baseline of page.items){
      const definitionKey=partition+'/'+baseline.questionnaire_version_id,definitions=tx.objectStore('definitions');
      const definition={questionnaire_id:baseline.questionnaire_id,questionnaire_version:baseline.questionnaire_version,definition:baseline.definition};
      const existing=await request<any>(definitions.get(definitionKey));check();
      if(existing&&canonical(existing.value)!==canonical(definition))throw Error('collision');
      if(!existing)definitions.put({key:definitionKey,value:definition});
      const records=tx.objectStore('records'),recordKey=partition+'/'+baseline.capture_id;
      const stored=await request<any>(records.get(recordKey));check();
      if(stored?.baseline){
       const before=stored.baseline;
       for(const field of ['capture_id','org_id','owner_account_id','owner_actor_id','child_id','questionnaire_id','questionnaire_version_id','questionnaire_version','created_by','created_at','captured_at'])if(before[field]!==baseline[field as keyof typeof baseline])throw Error('collision');
       if(before.revision===baseline.revision){
        for(const field of ['observation_date','answers','updated_by','updated_at'])if(canonical(before[field])!==canonical(baseline[field as keyof typeof baseline]))throw Error('collision');
        if(before.child_label===baseline.child_label)continue;
       }else if(BigInt(before.revision)>BigInt(baseline.revision))continue;
      }
      // Local IDs, pending overlays, base snapshots and conflict fields are opaque.
      records.put({...stored,key:recordKey,partition,baseline});
     }
     if(!Object.hasOwn(seen,token))downloads.put({key,partition,from_date:page.from_date,to_date:page.to_date,limit:page.limit,pages:{...seen,[token]:page.next_cursor},next_cursor:page.next_cursor,status:page.next_cursor===null?'complete':'partial'});
     const observation=!meta?.observation||Date.parse(page.observation.checked_at)>Date.parse(meta.observation.checked_at)?page.observation:meta.observation;
     partitions.put({key:partition,epoch,observation,wall:now,denied:false,clockLocked:false});check();
     return {now,tick};
    },configuration);
    shared.wall=committed.now;shared.mono=committed.tick;shared.knownLock=false;shared.clockLock=false;shared.lockedCheckedAt=0;shared.deniedAt=0;
    return result('committed');
   }catch(error){if(error instanceof ClockFailure)await clockLock(error.observation);return result('unavailable');}
  },
  async read(bounds:Readonly<{limit?:number;after?:string;progressAfter?:string}>={}) :Promise<Readonly<{kind:'available';records:readonly unknown[];downloads:readonly unknown[];next_key:string|null;progress_next_key:string|null;observation:Frozen<HistoryPage['observation']>}>|Readonly<{kind:'unavailable'}>>{
   try{
    const limit=bounds.limit===undefined?30:bounds.limit;
    if(!Number.isInteger(limit)||limit<1||limit>100)throw Error('bounds');
    for(const key of [bounds.after,bounds.progressAfter])if(key!==undefined&&(typeof key!=='string'||!key.startsWith(partition+'/')||key>=partition+'/\uffff'))throw Error('bounds');
    const view=await transaction(async(tx,check)=>{
     const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();if(!meta||meta.denied||meta.clockLocked||shared.knownLock||(meta.epoch??0)!==epoch)throw Error('locked');
     const {now,tick}=sensible(meta.observation,meta.wall);store.put({...meta,wall:now});
     const range=(after?:string)=>IDBKeyRange.bound(after??partition+'/',partition+'/\uffff',after!==undefined);
     const rows=await request<any[]>(tx.objectStore('records').getAll(range(bounds.after),limit+1));check();
     const progress=await request<any[]>(tx.objectStore('downloads').getAll(range(bounds.progressAfter),limit+1));check();
     return {view:freeze({kind:'available' as const,records:rows.slice(0,limit),downloads:progress.slice(0,limit),next_key:rows.length>limit?rows[limit-1].key:null,progress_next_key:progress.length>limit?progress[limit-1].key:null,observation:meta.observation}),now,tick};
    });shared.wall=view.now;shared.mono=view.tick;return view.view;
   }catch(error){if(error instanceof ClockFailure)await clockLock(error.observation);return result('unavailable');}
  },
  deny:lock,
  async logout(){try{return await lock();}finally{closed=true;db.close();}},
  close(){closed=true;for(const tx of ownTransactions)try{tx.abort();}catch{}db.close();},
 };
}
