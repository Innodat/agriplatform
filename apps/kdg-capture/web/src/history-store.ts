/** Isolated KDG cache. Explicit caller-owned lifetime; no startup or queue integration. */
import {request,complete} from '../offline-tools/idb.js';
import type {CaptureDetail,EditContext} from '../../contracts/edit-context-generated/types.gen';
import type {HistoryPage} from '../../contracts/history-generated/types.gen';
import {validateHistoryPage,validateOwnReadObservation,type PendingHistory} from './history.js';
import {validateEditContext,type PendingEditContext} from './edit-context.js';
import {validateOwnObservation} from './own-observation.js';
import {id,decimal,object,validateDetail,strictJSON,freeze,type Frozen} from './read-validation.js';
export const HISTORY_DATABASE='kdg-own-history-v1';
export type LocalEditChanges=Pick<CaptureDetail,'observation_date'|'answers'>;
export type ReviewedEdit=Frozen<{account_id:string;org_id:string;capture_id:string;base:CaptureDetail;capture:CaptureDetail;edit_epoch:number;edit_generation:number;predecessor_action_id:string|null;baseline_revision:string;read_observation:EditContext['read_observation'];edit_observation:EditContext['edit_observation']}>;
export type PreparedEdit=Frozen<{account_id:string;org_id:string;capture_id:string;command:LocalEditChanges&{operation_id:string;command_version:1;expected_revision:string}}>;
export type EditDelivery=Frozen<{version:1;pending:PreparedEdit;serialized:string;receipt?:{operation_id:string;command_type:'capture.edit';status:'committed';command_version:1;result:{capture_id:string;revision:string}};conflict?:{kind:'error';status:409;error_id:'kdg_capture.capture_revision_conflict';current_revision:string};readback_revision?:string}>;
export type LocalEditIntent=Frozen<{key:string;partition:string;version:1;type:'capture.edit';action_id:string;capture_id:string;content:string;base:CaptureDetail;changes:LocalEditChanges;predecessor_action_id:string|null;expected_revision:string|null;read_observation:EditContext['read_observation'];edit_observation:EditContext['edit_observation'];status:'Pending'|'Needs attention';delivery?:EditDelivery;result:{kind:'saved_locally'|'needs_attention';action_id:string}}>;
const tables=['records','definitions','partitions','downloads','edit_actions'];
const week=604800000;
type Fence={generation:number;transactions:Set<IDBTransaction>;wall:number;mono:number;knownLock:boolean;clockLock:boolean;lockedCheckedAt:number;deniedAt:number;editGeneration:number;editDenied:boolean;editDeniedAt:number};
type Execution=Readonly<{signal?:AbortSignal;isCurrent?:()=>boolean}>;
class AuthorityFailure extends Error {constructor(readonly kind:'expired'|'denied'){super(kind);}}
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
 const opening=factory.open(options.database??HISTORY_DATABASE,2);
 opening.onupgradeneeded=()=>{for(const name of tables)if(!opening.result.objectStoreNames.contains(name))opening.result.createObjectStore(name,{keyPath:'key'});};
 const db=await request(opening);db.onversionchange=()=>db.close();
 const fenceKey=(options.database??HISTORY_DATABASE)+'/'+partition;
 let fence=fences.get(fenceKey);if(!fence){fence={generation:0,transactions:new Set(),wall:wall(),mono:mono(),knownLock:false,clockLock:false,lockedCheckedAt:0,deniedAt:0,editGeneration:0,editDenied:false,editDeniedAt:0};fences.set(fenceKey,fence);}
 const shared=fence,generation=shared.generation;let closed=false;const ownTransactions=new Set<IDBTransaction>();
 let initialMeta:any;
 try{
  const initial=db.transaction('partitions','readonly'),done=complete(initial);void done.catch(()=>{});
  try{initialMeta=await request<any>(initial.objectStore('partitions').get(partition));await done;}
  catch{try{initial.abort();}catch{}await done.catch(()=>{});throw Error('unavailable');}
 }catch{db.close();throw Error('unavailable');}
 const epoch=initialMeta?.epoch??0;
 observeEditGeneration(initialMeta);
 function observeEditGeneration(meta:any){
  const observed=meta?.editGeneration??0;
  // A newer durable generation may carry another realm's completed restoration.
  // An older/equal row cannot clear a known denial whose write failed locally.
  if(observed>shared.editGeneration){shared.editGeneration=observed;shared.editDenied=meta?.editDenied===true;}
  else if(observed===shared.editGeneration&&meta?.editDenied)shared.editDenied=true;
  shared.editDeniedAt=Math.max(shared.editDeniedAt,meta?.editDeniedAt??0);
 }
 const reviews=new WeakSet<object>();
 const current=()=>!closed&&shared.generation===generation;
 function sensible(observation:any,watermark:number,recovery=false){
  if(observation?.permission==='kdg_capture.capture.edit.own')validateOwnObservation(observation,account_id,org_id,'kdg_capture.capture.edit.own');else validateOwnReadObservation(observation,account_id,org_id);
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
  catch(error){abort();await done.catch(()=>{});if(error instanceof ClockFailure||error instanceof AuthorityFailure)throw error;throw Error('unavailable');}
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
    shared.editGeneration++;shared.editDenied=true;shared.editDeniedAt=wall();
    shared.generation++;for(const active of shared.transactions)try{active.abort();}catch{}
    store.put({...meta,key:partition,epoch:epoch+1,editGeneration:shared.editGeneration,editDenied:true,editDeniedAt:shared.editDeniedAt,denied:true,deniedAt:shared.deniedAt});await done;return result('locked');
   }catch{try{tx.abort();}catch{}await done.catch(()=>{});return result('unavailable');}
  }catch{return result('unavailable');}
 }
 async function importBaseline(tx:IDBTransaction,baseline:any,check:()=>void){
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
        if(before.child_label===baseline.child_label){await reconcileBaseline(tx,stored,baseline,check);return;}
       }else if(BigInt(before.revision)>BigInt(baseline.revision))return;
      }
      // Local IDs, pending overlays, base snapshots and conflict fields are opaque.
      await reconcileBaseline(tx,{...stored,key:recordKey,partition,baseline},baseline,check);
 }
 // Delivery is separate from immutable local intent, and never asserts a send occurred.
 function supported(action:any){return action?.version===1&&action.type==='capture.edit'&&action.partition===partition&&action.key===partition+'/'+action.action_id&&id(action.action_id)&&id(action.capture_id)&&action.status==='Pending';}
 function validateReceipt(pin:PreparedEdit,value:unknown){
  const r=object(value,['operation_id','command_type','status','command_version','result']),v=object(r.result,['capture_id','revision']);
  if(r.operation_id!==pin.command.operation_id||r.command_type!=='capture.edit'||r.command_version!==1||r.status!=='committed'||v.capture_id!==pin.capture_id||!decimal(v.revision)||!decimal(pin.command.expected_revision)||BigInt(v.revision)<BigInt(pin.command.expected_revision)||BigInt(v.revision)>BigInt(pin.command.expected_revision)+1n)throw Error('invalid_receipt');
 }
 function validateConflict(pin:PreparedEdit,value:unknown){
  const c=object(value,['kind','status','error_id','current_revision']);
  if(c.kind!=='error'||c.status!==409||c.error_id!=='kdg_capture.capture_revision_conflict'||!decimal(c.current_revision)||!decimal(pin.command.expected_revision)||BigInt(c.current_revision)<=BigInt(pin.command.expected_revision))throw Error('invalid_conflict');
 }
 function prepared(action:any){
  try{
   if(!supported(action)||action.delivery?.version!==1)return false;
   const d=object(action.delivery,['version','pending','serialized'],['receipt','conflict','readback_revision']),p=object(d.pending,['account_id','org_id','capture_id','command']);
   if(p.account_id!==account_id||p.org_id!==org_id||p.capture_id!==action.capture_id)return false;
   const command=object(p.command,['operation_id','command_version','expected_revision','observation_date','answers']);
   if(command.operation_id!==action.action_id||command.command_version!==1||!decimal(command.expected_revision)||d.serialized!==JSON.stringify(command)||canonical(command)!==canonical({operation_id:action.action_id,command_version:1,expected_revision:command.expected_revision,...action.changes}))return false;
   if(Object.hasOwn(d,'receipt'))validateReceipt(action.delivery.pending,d.receipt);
   if(Object.hasOwn(d,'conflict'))validateConflict(action.delivery.pending,d.conflict);
   if(Object.hasOwn(d,'receipt')&&Object.hasOwn(d,'conflict'))return false;
   if(Object.hasOwn(d,'readback_revision')&&(!decimal(d.readback_revision)||!action.delivery.receipt||BigInt(d.readback_revision)<BigInt(action.delivery.receipt.result.revision)))return false;
   return true;
  }catch{return false;}
 }
 function matches(action:any,baseline:any){return action.capture_id===baseline.capture_id&&canonical(action.changes)===canonical({observation_date:baseline.observation_date,answers:baseline.answers});}
 async function reconcileBaseline(tx:IDBTransaction,row:any,baseline:any,check:()=>void){
  if(row.saved_edit){
   const actions=tx.objectStore('edit_actions'),action=await request<any>(actions.get(partition+'/'+row.saved_edit.action_id));check();
   if(prepared(action)&&!action.delivery.conflict&&action.delivery.receipt&&BigInt(action.delivery.receipt.result.revision)<=BigInt(baseline.revision)&&(action.delivery.receipt.result.revision!==baseline.revision||matches(action,baseline))){
    // Only actual imported detail supplies actor/timestamps; a receipt supplies no content.
    actions.put({...action,delivery:{...action.delivery,readback_revision:baseline.revision}});
    row={...row,saved_edit:undefined,edit_status:'Synced'};
   }
  }
  tx.objectStore('records').put(row);
 }
 async function ownProgress(tx:IDBTransaction,row:any,check:()=>void){
  let action_id=row.saved_edit?.action_id;const seen=new Set<string>();
  while(action_id&&!seen.has(action_id)){
   seen.add(action_id);const action=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+action_id));check();
   if(!supported(action)||action.capture_id!==row.baseline.capture_id||action.delivery&&(!prepared(action)||action.delivery.conflict))return false;
   if(prepared(action)&&action.delivery.receipt?.result.revision===row.baseline.revision&&matches(action,row.baseline))return true;
   action_id=action.predecessor_action_id;
  }
  return false;
 }
 async function readAccess(tx:IDBTransaction,check:()=>void){
  const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();
  if(!meta)throw Error('unavailable');if(meta.denied||(meta.epoch??0)!==epoch)throw new AuthorityFailure('denied');
  if(meta.clockLocked||shared.knownLock)throw Error('unavailable');
  const validate=()=>editObservation(meta.observation,meta.wall),clock=validate();store.put({...meta,wall:clock.now});return {meta,clock,validate};
 }
 async function consumeOutcome(pinned:PreparedEdit,value:unknown,conflict:boolean,execution:Execution){
  let pin:any,outcome:any;
  try{
   pin=structuredClone(pinned);outcome=structuredClone(value);
   object(pin,['account_id','org_id','capture_id','command']);object(pin.command,['operation_id','command_version','expected_revision','observation_date','answers']);
   if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.capture_id)||!id(pin.command.operation_id))return result('invalid');
   if(conflict)validateConflict(pin,outcome);
   else{object(outcome,['kind','receipt']);if(outcome.kind!=='committed')return result('invalid');validateReceipt(pin,outcome.receipt);}
  }catch{return result('invalid');}
  return editOperation<Readonly<{kind:'invalid'|'reconciled'}>>(async(tx,check)=>{
   const {clock,validate}=await readAccess(tx,check),actions=tx.objectStore('edit_actions'),action=await request<any>(actions.get(partition+'/'+pin.command.operation_id));check();validate();
   if(!prepared(action)||canonical(action.delivery.pending)!==canonical(pin))return {value:result('invalid'),clock,validate};
   const d=action.delivery;
   if(conflict?!!d.receipt:!!d.conflict)return {value:result('invalid'),clock,validate};
   const before=conflict?d.conflict:d.receipt,after=conflict?outcome:outcome.receipt;
   if(before&&canonical(before)!==canonical(after))return {value:result('invalid'),clock,validate};
   if(!before)actions.put({...action,delivery:{...d,[conflict?'conflict':'receipt']:after}});
   if(conflict){const records=tx.objectStore('records'),row=await request<any>(records.get(partition+'/'+action.capture_id));check();records.put({...row,edit_status:'Needs attention'});}
   validate();return {value:result('reconciled'),clock,validate};
  },execution);
 }
 function editObservation(observation:any,watermark:number){
  validateOwnObservation(observation,account_id,org_id,observation.permission);
  // Expiry belongs to this observation, not to the independent history authority.
  if(wall()>=Date.parse(observation.expires_at))throw new AuthorityFailure('expired');
  return sensible(observation,watermark);
 }
 function editAuthority(meta:any,row:any,reviewed?:any){
  if(!meta)throw Error('unavailable');
  observeEditGeneration(meta);
  if(meta.denied||meta.editDenied||shared.editDenied||(meta.epoch??0)!==epoch)throw new AuthorityFailure('denied');
  if(meta.clockLocked||shared.knownLock)throw Error('unavailable');
  if(!row?.edit_context)throw Error('unavailable');
  if(row.edit_epoch!==epoch||row.edit_generation!==(meta.editGeneration??0)||row.edit_generation!==shared.editGeneration)throw new AuthorityFailure('denied');
  if(reviewed&&(reviewed.edit_epoch!==epoch||reviewed.edit_generation!==row.edit_generation))throw new AuthorityFailure('denied');
  editObservation(row.edit_context.read_observation,meta.wall);const clock=editObservation(row.edit_context.edit_observation,meta.wall);
  if(reviewed){editObservation(reviewed.read_observation,meta.wall);editObservation(reviewed.edit_observation,meta.wall);}
  return clock;
 }
 async function editAccess(tx:IDBTransaction,capture_id:string,check:()=>void){
  const partitions=tx.objectStore('partitions'),meta=await request<any>(partitions.get(partition));check();
  const row=await request<any>(tx.objectStore('records').get(partition+'/'+capture_id));check();
  const clock=editAuthority(meta,row);partitions.put({...meta,wall:clock.now});return {row,meta,clock};
 }
 async function editOperation<T>(work:(tx:IDBTransaction,check:()=>void)=>Promise<{value:T;clock:{now:number;tick:number};validate?:()=>unknown}>,execution:Execution){
  try{const completed=await transaction(work,execution);completed.validate?.();shared.wall=completed.clock.now;shared.mono=completed.clock.tick;return completed.value;}
  catch(error){if(error instanceof ClockFailure)await clockLock(error.observation);return result(error instanceof AuthorityFailure?error.kind:'unavailable');}
 }
 return {
  /** Import exact verified evidence; history success never supplies edit authority. */
  async importEditContext(value:unknown,pinned:PendingEditContext,execution:Execution&Readonly<{restoreDenied?:boolean}>={}){
   try{
    const pending={...pinned};if(pending.account_id!==account_id||pending.org_id!==org_id)return result('unavailable');
    const context=validateEditContext(structuredClone(value),pending);
    return await editOperation(async(tx,check)=>{
     const partitions=tx.objectStore('partitions'),meta=await request<any>(partitions.get(partition));check();
     if((meta?.epoch??0)!==epoch||meta?.denied)throw new AuthorityFailure('denied');
     if(meta?.clockLocked||shared.knownLock)throw Error('locked');
     observeEditGeneration(meta);
     const denied=meta?.editDenied||shared.editDenied;
     const restoredGeneration=Math.max(meta?.editGeneration??0,shared.editGeneration)+(denied?1:0);
     if(denied&&(!execution.restoreDenied||Math.min(Date.parse(context.read_observation.checked_at),Date.parse(context.edit_observation.checked_at))<=Math.max(meta?.editDeniedAt??0,shared.editDeniedAt)))throw new AuthorityFailure('denied');
     editObservation(context.read_observation,meta?.wall??0);const clock=editObservation(context.edit_observation,meta?.wall??0);
     await importBaseline(tx,context.capture,check);
     const records=tx.objectStore('records'),row=await request<any>(records.get(partition+'/'+pending.capture_id));check();
     // Older evidence cannot replace a newer independent observation or baseline.
     const old=row.edit_context;
     if(!old||(BigInt(context.capture.revision)>=BigInt(old.capture.revision)&&Date.parse(context.read_observation.checked_at)>=Date.parse(old.read_observation.checked_at)&&Date.parse(context.edit_observation.checked_at)>=Date.parse(old.edit_observation.checked_at)))records.put({...row,edit_context:context,edit_epoch:epoch,edit_generation:restoredGeneration});
     const observation=!meta?.observation||Date.parse(context.read_observation.checked_at)>Date.parse(meta.observation.checked_at)?context.read_observation:meta.observation;
     editObservation(context.read_observation,meta?.wall??0);editObservation(context.edit_observation,meta?.wall??0);check();
     partitions.put({...meta,key:partition,epoch,observation,wall:clock.now,editGeneration:restoredGeneration,editDenied:false});
     return {value:result('committed'),clock,validate:()=>{if(shared.editGeneration>restoredGeneration)throw new AuthorityFailure('denied');editObservation(context.read_observation,clock.now);editObservation(context.edit_observation,clock.now);shared.editGeneration=restoredGeneration;shared.editDenied=false;}};
    },execution);
   }catch{return result('unavailable');}
  },
  async openEdit(capture_id:string,execution:Execution={}){
   if(!id(capture_id))return result('unavailable');
   return editOperation(async(tx,check)=>{
    const {row,meta,clock}=await editAccess(tx,capture_id,check);
    // A refresh can update the baseline, never the base of already saved local work.
    const reviewed:ReviewedEdit=freeze(structuredClone({account_id,org_id,capture_id,base:row.saved_edit?.base??row.baseline,
     capture:row.saved_edit?{...row.saved_edit.base,...row.saved_edit.changes}:row.baseline,
     edit_epoch:epoch,edit_generation:row.edit_generation,predecessor_action_id:row.saved_edit?.action_id??null,baseline_revision:row.baseline.revision,
     read_observation:row.edit_context.read_observation,edit_observation:row.edit_context.edit_observation}));
    reviews.add(reviewed);return {value:Object.freeze({kind:'opened' as const,reviewed}),clock,validate:()=>editAuthority(meta,row)};
   },execution);
  },
  async saveEdit(reviewed:unknown,action_id:string,input:unknown,execution:Execution={}){
   // Snapshot before the first await. Caller objects are never frozen or modified.
   let r:any,changes:any;
   try{
    if(!reviewed||typeof reviewed!=='object'||!id(action_id))return result('unavailable');
    r=structuredClone(reviewed);if(r.account_id!==account_id||r.org_id!==org_id||!id(r.capture_id))return result('unavailable');changes=structuredClone(input);
    object(changes,['observation_date','answers']);
    if(changes.answers&&typeof changes.answers==='object'&&!Array.isArray(changes.answers))for(const q of r.base.definition.questions){
     const answer=changes.answers[q.id];if(q.type==='boolean'&&answer&&answer.value===false&&Object.hasOwn(answer,'details'))delete answer.details;
    }
    validateDetail({...structuredClone(r.base),...changes},{account_id,org_id,capture_id:r.capture_id});
    const command=JSON.stringify({operation_id:action_id,command_version:1,expected_revision:'9223372036854775807',...changes});
    strictJSON(command);if(new TextEncoder().encode(command).byteLength>131072)return result('invalid');
   }catch{return result('invalid');}
   return editOperation(async(tx,check)=>{
    const {row,meta,clock}=await editAccess(tx,r.capture_id,check),actions=tx.objectStore('edit_actions');
    // The exact evidence actually reviewed must still be valid independently.
    editAuthority(meta,row,r);
    const key=partition+'/'+action_id,content=canonical({reviewed:r,input:changes}),existing=await request<any>(actions.get(key));check();
    const validate=()=>editAuthority(meta,row,r);validate();
    if(existing){if(existing.content!==content)return {value:result('action_id_reused'),clock};return {value:freeze(structuredClone(existing.result)),clock,validate};}
    if(!reviews.has(reviewed as object))return {value:result('unavailable'),clock};
    const progress=row.baseline.revision===r.base.revision||await ownProgress(tx,row,check);
    const stale=(row.saved_edit?.action_id??null)!==r.predecessor_action_id||row.baseline.revision!==r.baseline_revision||!progress||row.edit_status==='Needs attention'||!!row.pending||!!row.conflict;
    const outcome=Object.freeze({kind:stale?'needs_attention' as const:'saved_locally' as const,action_id});
    const intent={key,partition,version:1,type:'capture.edit',action_id,capture_id:r.capture_id,content,base:r.base,changes,
     predecessor_action_id:r.predecessor_action_id,expected_revision:r.predecessor_action_id===null?r.base.revision:null,
     read_observation:r.read_observation,edit_observation:r.edit_observation,status:stale?'Needs attention':'Pending',result:outcome};
    validate();actions.add(intent);
    if(!stale)tx.objectStore('records').put({...row,saved_edit:{action_id,base:r.base,changes},edit_status:'Pending'});
    return {value:outcome,clock,validate};
   },execution);
  },
  /** Inert preparation only: transactionally freeze bytes before returning any command. */
  async prepareEdit(action_id:string,execution:Execution={}){
   if(!id(action_id))return result('invalid');
   return editOperation<Readonly<{kind:'blocked'|'invalid'}>|Frozen<{kind:'prepared';pending:PreparedEdit;serialized:string}>>(async(tx,check)=>{
    const actions=tx.objectStore('edit_actions'),action=await request<any>(actions.get(partition+'/'+action_id));check();
    if(!supported(action)){const {clock,validate}=await readAccess(tx,check);return {value:result('blocked'),clock,validate};}
    const {row,meta,clock}=await editAccess(tx,action.capture_id,check),validate=()=>editAuthority(meta,row);validate();
    if(action.delivery){
     if(!prepared(action)||action.delivery.conflict)return {value:result('blocked'),clock,validate};
     return {value:freeze({kind:'prepared' as const,pending:action.delivery.pending,serialized:action.delivery.serialized}),clock,validate};
    }
    if(row.pending||row.conflict||row.edit_status==='Needs attention')return {value:result('blocked'),clock,validate};
    if(row.baseline.revision!==action.base.revision&&!await ownProgress(tx,row,check)){
     validate();tx.objectStore('records').put({...row,edit_status:'Needs attention'});
     return {value:result('blocked'),clock,validate};
    }
    let expected_revision=action.expected_revision;
    if(action.predecessor_action_id!==null){
     const parent=await request<any>(actions.get(partition+'/'+action.predecessor_action_id));check();validate();
     if(!prepared(parent)||parent.capture_id!==action.capture_id||parent.delivery.conflict||!parent.delivery.receipt)return {value:result('blocked'),clock,validate};
     expected_revision=parent.delivery.receipt.result.revision;
    }
    if(!decimal(expected_revision))return {value:result('blocked'),clock,validate};
    const command={operation_id:action_id,command_version:1 as const,expected_revision,...action.changes},serialized=JSON.stringify(command);
    strictJSON(serialized);if(new TextEncoder().encode(serialized).byteLength>131072)return {value:result('invalid'),clock,validate};
    const pending={account_id,org_id,capture_id:action.capture_id,command};
    validate();actions.put({...action,delivery:{version:1,pending,serialized}});
    return {value:freeze({kind:'prepared' as const,pending,serialized}),clock,validate};
   },execution);
  },
  consumeEditReceipt(pinned:PreparedEdit,outcome:unknown,execution:Execution={}){return consumeOutcome(pinned,outcome,false,execution);},
  consumeEditConflict(pinned:PreparedEdit,outcome:unknown,execution:Execution={}){return consumeOutcome(pinned,outcome,true,execution);},
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
      await importBaseline(tx,baseline,check);
     }
     if(!Object.hasOwn(seen,token))downloads.put({key,partition,from_date:page.from_date,to_date:page.to_date,limit:page.limit,pages:{...seen,[token]:page.next_cursor},next_cursor:page.next_cursor,status:page.next_cursor===null?'complete':'partial'});
     const observation=!meta?.observation||Date.parse(page.observation.checked_at)>Date.parse(meta.observation.checked_at)?page.observation:meta.observation;
     partitions.put({...meta,key:partition,epoch,observation,wall:now,denied:false,clockLocked:false});check();
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
  /** Current denial affects editing only; a newer explicit context import restores it. */
  async denyEdit(pinned:Readonly<{account_id:string;org_id:string}>={account_id,org_id},execution:Execution={}){
   if(pinned.account_id!==account_id||pinned.org_id!==org_id)return result('unavailable');
   return editOperation(async(tx,check)=>{
    const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();
    if((meta?.epoch??0)!==epoch)throw Error('superseded');
    shared.editGeneration=Math.max(shared.editGeneration,meta?.editGeneration??0)+1;shared.editDenied=true;shared.editDeniedAt=wall();
    store.put({...meta,key:partition,epoch,editGeneration:shared.editGeneration,editDenied:true,editDeniedAt:shared.editDeniedAt});
    return {value:result('denied'),clock:{now:wall(),tick:mono()}};
   },execution);
  },
  /** Retained completed proposals are readable under own-read, including after edit denial. */
  async readEditActions(bounds:Readonly<{limit?:number;after?:string}>={},execution:Execution={}){
   try{
    const limit=bounds.limit??30,after=bounds.after;
    if(!Number.isInteger(limit)||limit<1||limit>100||after!==undefined&&(typeof after!=='string'||!after.startsWith(partition+'/')||after>=partition+'/\uffff'))return result('unavailable');
    return await editOperation(async(tx,check)=>{
     const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();
     if(!meta)throw Error('unavailable');if(meta.denied||(meta.epoch??0)!==epoch)throw new AuthorityFailure('denied');
     if(meta.clockLocked||shared.knownLock)throw Error('unavailable');
     const validate=()=>editObservation(meta.observation,meta.wall),clock=validate();
     const rows=await request<LocalEditIntent[]>(tx.objectStore('edit_actions').getAll(IDBKeyRange.bound(after??partition+'/',partition+'/\uffff',after!==undefined),limit+1));check();validate();store.put({...meta,wall:clock.now});
     return {value:freeze({kind:'available' as const,actions:rows.slice(0,limit),next_key:rows.length>limit?rows[limit-1].key as string:null}),clock,validate};
    },execution);
   }catch{return result('unavailable');}
  },
  deny:lock,
  async logout(){try{return await lock();}finally{closed=true;db.close();}},
  close(){closed=true;for(const tx of ownTransactions)try{tx.abort();}catch{}db.close();},
 };
}
