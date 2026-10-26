/** Isolated KDG cache. Explicit caller-owned lifetime; no startup or queue integration. */
import {request,complete} from '../offline-tools/idb.js';
import type {CaptureDetail,EditContext} from '../../contracts/edit-context-generated/types.gen';
import type {HistoryPage} from '../../contracts/history-generated/types.gen';
import {validateHistoryPage,validateOwnReadObservation,type PendingHistory} from './history.js';
import {validateEditContext,type PendingEditContext} from './edit-context.js';
import {validateOwnObservation} from './own-observation.js';
import {id,decimal,object,validateDetail,validateAnswers,date,instant,strictJSON,freeze,type Frozen} from './read-validation.js';
import {validateProvision} from './provision.js';
import type {Provision} from '../../contracts/provision-generated/types.gen';
import type {PendingCreate} from './create.js';
export type SetupTicket=Readonly<{account_id:string;org_id:string;generation:number;nonce:string}>;
export type ReviewedCreate=Frozen<{account_id:string;org_id:string;actor_id:string;membership_id:string;epoch:number;create_generation:number;child:Provision['children'][number];questionnaire:NonNullable<Provision['questionnaire']>;read_observation:Provision['read_observation'];create_observation:NonNullable<Provision['create_all_observation']>}>;
export type CreateDelivery=Frozen<{version:1;receipt?:{operation_id:string;command_type:'capture.create';status:'committed';command_version:1;result:{capture_id:string;revision:string}};attention?:string;readback_revision?:string}>;
export type LocalCreateIntent=Frozen<{key:string;partition:string;version:1;type:'capture.create';action_id:string;capture_id:string;pending:PendingCreate;serialized:string;content:string;status:'Pending';delivery?:CreateDelivery;result:{kind:'saved_locally';capture_id:string;operation_id:string}}>;
export const HISTORY_DATABASE='kdg-own-history-v1';
export type LocalEditChanges=Pick<CaptureDetail,'observation_date'|'answers'>;
type ServerReviewedEdit=Frozen<{account_id:string;org_id:string;capture_id:string;base:CaptureDetail;capture:CaptureDetail;edit_epoch:number;edit_generation:number;predecessor_action_id:string|null;baseline_revision:string;read_observation:EditContext['read_observation'];edit_observation:EditContext['edit_observation']}>;
export type PreparedEdit=Frozen<{account_id:string;org_id:string;capture_id:string;command:LocalEditChanges&{operation_id:string;command_version:1;expected_revision:string}}>;
export type EditDelivery=Frozen<{version:1;pending:PreparedEdit;serialized:string;receipt?:{operation_id:string;command_type:'capture.edit';status:'committed';command_version:1;result:{capture_id:string;revision:string}};conflict?:{kind:'error';status:409;error_id:'kdg_capture.capture_revision_conflict';current_revision:string};readback_revision?:string}>;
type ServerLocalEditIntent=Frozen<{key:string;partition:string;version:1;type:'capture.edit';action_id:string;capture_id:string;content:string;base:CaptureDetail;changes:LocalEditChanges;predecessor_action_id:string|null;expected_revision:string|null;read_observation:EditContext['read_observation'];edit_observation:EditContext['edit_observation'];status:'Pending'|'Needs attention';delivery?:EditDelivery;result:{kind:'saved_locally'|'needs_attention';action_id:string}}>;
/** A completed local create has no server revision or server attribution. */
export type LocalCaptureBase=Omit<CaptureDetail,'revision'|'created_by'|'created_at'|'updated_by'|'updated_at'>;
export type EditPredecessor=Readonly<{type:'capture.create'|'capture.edit';action_id:string}>;
export type PendingReviewedEdit=Frozen<{version:2;base_kind:'local_create';account_id:string;org_id:string;capture_id:string;base:LocalCaptureBase;capture:LocalCaptureBase;edit_epoch:number;edit_generation:number;predecessor:EditPredecessor;predecessor_action_id:string;baseline_revision:string|null;read_observation:EditContext['read_observation'];edit_observation:EditContext['edit_observation']}>;
export type ReviewedEdit=ServerReviewedEdit|PendingReviewedEdit;
export type LocalEditIntent=ServerLocalEditIntent|Frozen<Omit<ServerLocalEditIntent,'version'|'base'|'predecessor_action_id'> & {version:2;base_kind:'local_create';base:LocalCaptureBase;predecessor:EditPredecessor;predecessor_action_id:string}>;
const tables=['records','definitions','partitions','downloads','edit_actions','setups','create_actions'];
const week=604800000;
type ChildLoss={generation:number;deniedAt:number;denied:boolean};
type Fence={childLosses:Map<string,ChildLoss>;createLatches:Map<string,{generation:number;deniedAt:number}>;generation:number;transactions:Set<IDBTransaction>;wall:number;mono:number;knownLock:boolean;clockLock:boolean;lockedCheckedAt:number;deniedAt:number;editGeneration:number;editDenied:boolean;editDeniedAt:number};
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
 const opening=factory.open(options.database??HISTORY_DATABASE,3);
 opening.onupgradeneeded=()=>{for(const name of tables)if(!opening.result.objectStoreNames.contains(name))opening.result.createObjectStore(name,{keyPath:'key'});};
 const db=await request(opening);db.onversionchange=()=>db.close();
 const fenceKey=(options.database??HISTORY_DATABASE)+'/'+partition;
 let fence=fences.get(fenceKey);if(!fence){fence={childLosses:new Map(),createLatches:new Map(),generation:0,transactions:new Set(),wall:wall(),mono:mono(),knownLock:false,clockLock:false,lockedCheckedAt:0,deniedAt:0,editGeneration:0,editDenied:false,editDeniedAt:0};fences.set(fenceKey,fence);}
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
  if(observed>shared.editGeneration){shared.editGeneration=observed;shared.editDenied=meta?.editDenied===true||shared.editDenied&&(meta?.editRestoredAt??0)<=shared.editDeniedAt;}
  else if(observed===shared.editGeneration&&meta?.editDenied)shared.editDenied=true;
  shared.editDeniedAt=Math.max(shared.editDeniedAt,meta?.editDeniedAt??0);
 }
 const reviews=new WeakSet<object>(),createReviews=new WeakSet<object>(),createBindings=new WeakMap<object,number>();
 const createLatches=shared.createLatches;
 const current=()=>!closed&&shared.generation===generation;
 function sensible(observation:any,watermark:number,recovery=false){
  if(['kdg_capture.capture.read.own','kdg_capture.capture.edit.own','kdg_capture.capture.create.all','kdg_capture.capture.create.assigned'].includes(observation?.permission))validateOwnObservation(observation,account_id,org_id,observation.permission);else throw Error('invalid_observation');
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
 async function lock(pinned:Readonly<{account_id:string;org_id:string}>={account_id,org_id},execution:Execution={},ticket?:SetupTicket){
  let fresh=false;try{fresh=current()&&pinned.account_id===account_id&&pinned.org_id===org_id&&!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
  if(!fresh)return result('unavailable');
  try{const tx=db.transaction('partitions','readwrite'),done=complete(tx);void done.catch(()=>{});const store=tx.objectStore('partitions'),abort=()=>{try{tx.abort();}catch{}};
   execution.signal?.addEventListener('abort',abort,{once:true});
   try{if(execution.signal?.aborted)abort();const meta=await request<any>(store.get(partition));
    let valid=false;try{valid=current()&&(meta?.epoch??0)===epoch&&!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
    if(!valid){tx.abort();await done.catch(()=>{});return result('unavailable');}
    if(ticket&&(meta?.setupGeneration!==ticket.generation||meta?.setupNonce!==ticket.nonce)){tx.abort();await done.catch(()=>{});return result('superseded');}
    // A confirmed current known denial latches before its durable write can fail.
    shared.knownLock=true;shared.deniedAt=wall();shared.lockedCheckedAt=Math.max(shared.lockedCheckedAt,Date.parse(meta?.observation?.checked_at??'')||0);
    shared.editGeneration++;shared.editDenied=true;shared.editDeniedAt=wall();
    shared.generation++;for(const active of shared.transactions)try{active.abort();}catch{}
    store.put({...meta,key:partition,epoch:epoch+1,...(ticket?{setupNonce:null}:{}),editGeneration:shared.editGeneration,editDenied:true,editDeniedAt:shared.editDeniedAt,denied:true,deniedAt:shared.deniedAt});await done;
    let published=false;try{published=!execution.signal?.aborted&&(!execution.isCurrent||execution.isCurrent()===true);}catch{}
    return published?result('locked'):result('unavailable');
   }catch{try{tx.abort();}catch{}await done.catch(()=>{});return result('unavailable');}
   finally{execution.signal?.removeEventListener('abort',abort);}
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
 function supportedAction(action:any){
  if(action?.version===2){try{
   const identity=object(JSON.parse(action.content),['reviewed','input']),r=identity.reviewed as any;
   if(r.version!==2||r.base_kind!=='local_create'||r.account_id!==account_id||r.org_id!==org_id||r.capture_id!==action.capture_id||r.predecessor_action_id!==r.predecessor?.action_id||r.predecessor_action_id!==action.predecessor_action_id||canonical(r.base)!==canonical(action.base)||canonical(r.predecessor)!==canonical(action.predecessor)||canonical(identity.input)!==canonical(action.changes)||action.expected_revision!==null||Object.hasOwn(action.base,'revision')||Object.hasOwn(action.base,'created_at'))return false;
   const outcome=object(action.result,['kind','action_id']);if(outcome.action_id!==action.action_id||outcome.kind!==(action.status==='Pending'?'saved_locally':'needs_attention'))return false;
   if(!date(action.changes.observation_date))return false;validateAnswers(action.base.definition,action.changes.answers);
  }catch{return false;}}
  return (action?.version===1||action?.version===2&&action.base_kind==='local_create'&&['capture.create','capture.edit'].includes(action.predecessor?.type)&&action.predecessor.action_id===action.predecessor_action_id)&&action.type==='capture.edit'&&action.partition===partition&&action.key===partition+'/'+action.action_id&&id(action.action_id)&&id(action.capture_id)&&['Pending','Needs attention'].includes(action.status);}
 function supported(action:any){return supportedAction(action)&&action.status==='Pending';}
 async function originalLocalBase(tx:IDBTransaction,action:any,check:()=>void){
  if(action.version!==2)return true;
  const row=await request<any>(tx.objectStore('records').get(partition+'/'+action.capture_id));check();
  if(!row?.create_action_id)return false;
  const original=await request<any>(tx.objectStore('create_actions').get(partition+'/'+row.create_action_id));check();
  return supportedCreate(original)&&validCreateDelivery(original)&&original.capture_id===action.capture_id&&canonical(action.base)===canonical(localBase(original));
 }
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
 async function checkedPrepared(tx:IDBTransaction,action:any,check:()=>void,seen=new Set<string>()):Promise<boolean>{
  if(!prepared(action))return false;
  if(action.version!==2)return true;
  if(seen.has(action.action_id)||!await originalLocalBase(tx,action,check))return false;
  seen.add(action.action_id);
  let revision:string|undefined;
  if(action.predecessor.type==='capture.create'){
   const row=await request<any>(tx.objectStore('records').get(partition+'/'+action.capture_id));check();
   if(row?.create_action_id!==action.predecessor.action_id)return false;
   const parent=await request<any>(tx.objectStore('create_actions').get(partition+'/'+action.predecessor.action_id));check();
   if(!supportedCreate(parent)||!validCreateDelivery(parent)||parent.capture_id!==action.capture_id)return false;
   revision=parent.delivery?.receipt?.result.revision;
  }else{
   const parent=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+action.predecessor.action_id));check();
   if(!await checkedPrepared(tx,parent,check,seen)||parent.capture_id!==action.capture_id||parent.delivery.conflict)return false;
   revision=parent.delivery.receipt?.result.revision;
  }
  return decimal(revision)&&action.delivery.pending.command.expected_revision===revision;
 }
 function matches(action:any,baseline:any){return action.capture_id===baseline.capture_id&&canonical(action.changes)===canonical({observation_date:baseline.observation_date,answers:baseline.answers});}
 async function reconcileBaseline(tx:IDBTransaction,row:any,baseline:any,check:()=>void){
  if(row.create_action_id){
   const actions=tx.objectStore('create_actions'),action=await request<any>(actions.get(partition+'/'+row.create_action_id));check();
   if(supportedCreate(action)&&validCreateDelivery(action)&&action.delivery?.receipt&&createMatches(action,baseline)){
    actions.put({...action,delivery:{...action.delivery,readback_revision:baseline.revision}});
    row={...row,create_status:'Synced'};
   }
  }
  if(row.saved_edit){
   const actions=tx.objectStore('edit_actions'),action=await request<any>(actions.get(partition+'/'+row.saved_edit.action_id));check();
   if(await checkedPrepared(tx,action,check)&&!action.delivery.conflict&&action.delivery.receipt&&BigInt(action.delivery.receipt.result.revision)<=BigInt(baseline.revision)&&(action.delivery.receipt.result.revision!==baseline.revision||matches(action,baseline))){
    // Only actual imported detail supplies actor/timestamps; a receipt supplies no content.
    actions.put({...action,delivery:{...action.delivery,readback_revision:baseline.revision}});
    row={...row,saved_edit:undefined,edit_status:'Synced'};
   }
  }
  tx.objectStore('records').put(row);
 }
 async function ownProgress(tx:IDBTransaction,row:any,check:()=>void){
  if(!row.saved_edit&&row.baseline&&row.create_action_id){const parent=await request<any>(tx.objectStore('create_actions').get(partition+'/'+row.create_action_id));check();if(supportedCreate(parent)&&validCreateDelivery(parent)&&parent.delivery?.receipt&&parent.delivery.receipt.result.revision===row.baseline.revision&&createMatches(parent,row.baseline))return true;}
  let action_id=row.saved_edit?.action_id;const seen=new Set<string>();
  while(action_id&&!seen.has(action_id)){
   seen.add(action_id);const action=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+action_id));check();
   if(!supported(action)||action.capture_id!==(row.baseline??row.local_capture).capture_id||action.delivery&&(!await checkedPrepared(tx,action,check)||action.delivery.conflict))return false;
   if(row.baseline&&await checkedPrepared(tx,action,check)&&action.delivery.receipt?.result.revision===row.baseline.revision&&matches(action,row.baseline))return true;
   if(action.version===2&&action.predecessor.type==='capture.create'){
    const parent=await request<any>(tx.objectStore('create_actions').get(partition+'/'+action.predecessor.action_id));check();
    return supportedCreate(parent)&&validCreateDelivery(parent)&&!!parent.delivery?.receipt&&!!row.baseline&&createMatches(parent,row.baseline)&&row.baseline.revision===parent.delivery.receipt.result.revision;
   }
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
   if(!await checkedPrepared(tx,action,check)||!await originalLocalBase(tx,action,check)||canonical(action.delivery.pending)!==canonical(pin))return {value:result('invalid'),clock,validate};
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
  if(row?.pending_edit_context){
   if(reviewed&&(reviewed.edit_epoch!==epoch||reviewed.edit_generation!==(meta.editGeneration??0)||reviewed.edit_generation!==shared.editGeneration))throw new AuthorityFailure('denied');
   const context=row.pending_edit_context;
   if(context.read_observation?.permission!=='kdg_capture.capture.read.own'||context.edit_observation?.permission!=='kdg_capture.capture.edit.own')throw new AuthorityFailure('denied');
   if(!context.edit_observation)throw new AuthorityFailure('denied');
   if(context.actor_id!==row.local_capture.owner_actor_id||context.read_observation.actor_id!==context.actor_id||context.edit_observation.actor_id!==context.actor_id||context.read_observation.membership_id!==context.membership_id||context.edit_observation.membership_id!==context.membership_id)throw new AuthorityFailure('denied');
   editObservation(context.read_observation,meta.wall);const clock=editObservation(context.edit_observation,meta.wall);
   if(reviewed){if(Math.min(Date.parse(reviewed.read_observation.checked_at),Date.parse(reviewed.edit_observation.checked_at))<=Math.max(meta.editDeniedAt??0,shared.editDeniedAt))throw new AuthorityFailure('denied');editObservation(reviewed.read_observation,meta.wall);editObservation(reviewed.edit_observation,meta.wall);}
   return clock;
  }
  if(!row?.baseline||!row?.edit_context)throw Error('unavailable');
  if(row.edit_epoch!==epoch||row.edit_generation!==(meta.editGeneration??0)||row.edit_generation!==shared.editGeneration)throw new AuthorityFailure('denied');
  if(reviewed&&(reviewed.edit_epoch!==epoch||reviewed.edit_generation!==row.edit_generation))throw new AuthorityFailure('denied');
  editObservation(row.edit_context.read_observation,meta.wall);const clock=editObservation(row.edit_context.edit_observation,meta.wall);
  if(reviewed){if(Math.min(Date.parse(reviewed.read_observation.checked_at),Date.parse(reviewed.edit_observation.checked_at))<=Math.max(meta.editDeniedAt??0,shared.editDeniedAt))throw new AuthorityFailure('denied');editObservation(reviewed.read_observation,meta.wall);editObservation(reviewed.edit_observation,meta.wall);}
  return clock;
 }
 async function editAccess(tx:IDBTransaction,capture_id:string,check:()=>void){
  const partitions=tx.objectStore('partitions'),meta=await request<any>(partitions.get(partition));check();
  const row=await request<any>(tx.objectStore('records').get(partition+'/'+capture_id));check();
  if(row?.local_capture&&(!row.edit_context||row.saved_edit?.base_kind==='local_create')){
   const action=await request<any>(tx.objectStore('create_actions').get(partition+'/'+row.create_action_id));check();
   if(!supportedCreate(action)||!validCreateDelivery(action)||canonical(row.local_capture)!==canonical(localBase(action)))throw Error('unavailable');
   const setup=await request<any>(tx.objectStore('setups').get(partition));check();Object.defineProperty(row,'pending_edit_context',{value:setup?.value,enumerable:false});
   if(!row.pending_edit_context)throw Error('unavailable');
  }
  if(row?.saved_edit){const saved=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+row.saved_edit.action_id));check();if(!supported(saved)||!await originalLocalBase(tx,saved,check)||saved.capture_id!==capture_id||canonical(saved.base)!==canonical(row.saved_edit.base)||canonical(saved.changes)!==canonical(row.saved_edit.changes))throw Error('unsupported_overlay');}
  const clock=editAuthority(meta,row);partitions.put({...meta,wall:clock.now});return {row,meta,clock};
 }
 async function editOperation<T>(work:(tx:IDBTransaction,check:()=>void)=>Promise<{value:T;clock:{now:number;tick:number};validate?:()=>unknown}>,execution:Execution){
  try{const completed=await transaction(work,execution);completed.validate?.();shared.wall=completed.clock.now;shared.mono=completed.clock.tick;return completed.value;}
  catch(error){if(error instanceof ClockFailure)await clockLock(error.observation);return result(error instanceof AuthorityFailure?error.kind:'unavailable');}
 }
 function supportedCreate(action:any):action is LocalCreateIntent {
  try{
   if(action?.version!==1||action.type!=='capture.create'||action.partition!==partition||action.key!==partition+'/'+action.action_id||!id(action.action_id)||!id(action.capture_id)||action.action_id===action.capture_id||action.status!=='Pending')return false;
   const p=object(action.pending,['account_id','org_id','command']),c=object(p.command,['operation_id','command_version','capture_id','child_id','questionnaire_version_id','child_eligibility_ref','observation_date','captured_at','answers']);
   if(p.account_id!==account_id||p.org_id!==org_id||c.operation_id!==action.action_id||c.capture_id!==action.capture_id||c.command_version!==1||!id(c.child_id)||!id(c.questionnaire_version_id)||(typeof c.child_eligibility_ref!=='string'||c.child_eligibility_ref.length!==43||!/^[A-Za-z0-9_-]+$/.test(c.child_eligibility_ref))||!date(c.observation_date)||!instant(c.captured_at)||action.serialized!==JSON.stringify(c)||new TextEncoder().encode(action.serialized).byteLength>131072)return false;
   strictJSON(action.serialized);const identity=object(JSON.parse(action.content),['reviewed','pending']);
   if(canonical(identity.pending)!==canonical(p))return false;
   const reviewed=identity.reviewed as any;
   if(reviewed.account_id!==account_id||reviewed.org_id!==org_id||reviewed.child.child_id!==c.child_id||reviewed.child.child_eligibility_ref!==c.child_eligibility_ref||reviewed.questionnaire.questionnaire_version_id!==c.questionnaire_version_id)return false;
   validateAnswers(reviewed.questionnaire.definition,c.answers);
   const outcome=object(action.result,['kind','capture_id','operation_id']);
   return outcome.kind==='saved_locally'&&outcome.capture_id===action.capture_id&&outcome.operation_id===action.action_id;
  }catch{return false;}
 }
 function localBase(action:LocalCreateIntent){const {reviewed:r}=JSON.parse(action.content);const {operation_id,command_version,capture_id,child_id,questionnaire_version_id,child_eligibility_ref,...changes}=action.pending.command;return {capture_id,org_id,owner_account_id:account_id,owner_actor_id:r.actor_id,child_id,child_label:r.child.child_label,...r.questionnaire,...changes};}
 function validateCreateReceipt(action:LocalCreateIntent,value:unknown){
  const r=object(value,['operation_id','command_type','status','command_version','result']),v=object(r.result,['capture_id','revision']);
  if(r.operation_id!==action.action_id||r.command_type!=='capture.create'||r.command_version!==1||r.status!=='committed'||v.capture_id!==action.capture_id||v.revision!=='1')throw Error('invalid_receipt');
 }
 function validCreateDelivery(action:LocalCreateIntent){
  try{if(!Object.hasOwn(action,'delivery'))return true;const d=object(action.delivery,['version'],['receipt','attention','readback_revision']);if(d.version!==1)return false;
   const receipt=Object.hasOwn(d,'receipt'),attention=Object.hasOwn(d,'attention');
   if(receipt)validateCreateReceipt(action,d.receipt);
   if(attention&&(typeof d.attention!=='string'||receipt))return false;
   if(Object.hasOwn(d,'readback_revision')&&(!receipt||!decimal(d.readback_revision)||BigInt(d.readback_revision)<BigInt((d.receipt as any).result.revision)))return false;
   return true;
  }catch{return false;}
 }
 function createMatches(action:LocalCreateIntent,baseline:any){
  const {reviewed:r}=JSON.parse(action.content),c=action.pending.command,receipt=action.delivery?.receipt;
  if(!receipt||BigInt(baseline.revision)<BigInt(receipt.result.revision))return false;
  if(baseline.capture_id!==c.capture_id||baseline.org_id!==org_id||baseline.owner_account_id!==account_id||baseline.owner_actor_id!==r.actor_id||baseline.child_id!==c.child_id||baseline.questionnaire_version_id!==c.questionnaire_version_id||baseline.captured_at!==c.captured_at||baseline.questionnaire_id!==r.questionnaire.questionnaire_id||baseline.questionnaire_version!==r.questionnaire.questionnaire_version||canonical(baseline.definition)!==canonical(r.questionnaire.definition))return false;
  return baseline.revision!==receipt.result.revision||(baseline.observation_date===c.observation_date&&canonical(baseline.answers)===canonical(c.answers));
 }
 function createSlot(permission:string){return permission==='kdg_capture.capture.create.all'?'create_all_observation':'create_assigned_observation';}
 function childScope(reviewed:any){return reviewed.actor_id+'/'+reviewed.membership_id+'/'+reviewed.child.create_permission+'/'+reviewed.child.child_id;}
 function childLoss(meta:any,key:string):ChildLoss {
  const durable=meta?.childLosses?.[key],process=shared.childLosses.get(key);
  return process&&(!durable||process.generation>durable.generation)?process:durable??{generation:0,deniedAt:0,denied:false};
 }
 function createAuthority(meta:any,setup:any,reviewed?:any,childGeneration?:number){
  if(!meta||meta.denied||(meta.epoch??0)!==epoch)throw new AuthorityFailure('denied');
  if(meta.clockLocked||shared.knownLock)throw Error('unavailable');
  const p=setup?.value;if(!p)throw Error('unavailable');
  const validateObservation=(o:any)=>{if(!o)throw new AuthorityFailure('denied');return editObservation(o,meta.wall??0);};
  const clock=validateObservation(meta.observation);
  if(reviewed){
   const loss=childLoss(meta,childScope(reviewed));if(loss.denied||childGeneration!==loss.generation)throw new AuthorityFailure('denied');
   const slot=createSlot(reviewed.child.create_permission),current=p[slot],latch=createLatches.get(slot),negativeFloor=Math.max(meta.createDeniedAt?.[slot]??0,latch?.deniedAt??0);
   if(negativeFloor&&(!current||Date.parse(current.checked_at)<=negativeFloor||Date.parse(reviewed.create_observation.checked_at)<=negativeFloor))throw new AuthorityFailure('denied');
   if(!current||(meta.createGenerations?.[slot]??0)!==reviewed.create_generation||(latch&&latch.generation>reviewed.create_generation)||reviewed.epoch!==epoch)throw new AuthorityFailure('denied');
   if(p.actor_id!==reviewed.actor_id||p.membership_id!==reviewed.membership_id||meta.observation.actor_id!==reviewed.actor_id||meta.observation.membership_id!==reviewed.membership_id)throw new AuthorityFailure('denied');
   const child=p.children.find((c:any)=>c.child_id===reviewed.child.child_id);
   if(!child||child.create_permission!==reviewed.child.create_permission||child.child_revision!==reviewed.child.child_revision||canonical(child.assignment)!==canonical(reviewed.child.assignment))throw new AuthorityFailure('denied');
   validateObservation(current);validateObservation(reviewed.read_observation);validateObservation(reviewed.create_observation);
   for(const c of [child,reviewed.child]){if(wall()>=Date.parse(c.expires_at))throw new AuthorityFailure('expired');sensible({...reviewed.create_observation,checked_at:c.checked_at,expires_at:c.expires_at},meta.wall??0);}
  }
  return clock;
 }
 return {
  /** Publish only the latest setup request's confirmed HTTP denial. */
  async denySetup(ticket:SetupTicket,execution:Execution={}){
   let t:SetupTicket;try{t={...ticket};object(t,['account_id','org_id','generation','nonce']);if(t.account_id!==account_id||t.org_id!==org_id||!Number.isSafeInteger(t.generation)||!id(t.nonce))return result('invalid');}catch{return result('invalid');}
   return lock({account_id,org_id},execution,t);
  },
  /** Mint before the HTTP request. Only the latest durable request may publish setup. */
  async beginSetupRefresh(execution:Execution={}){
   return editOperation(async(tx,check)=>{
    const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();
    if((meta?.epoch??0)!==epoch)throw new AuthorityFailure('denied');
    const ticket=Object.freeze({account_id,org_id,generation:(meta?.setupGeneration??0)+1,nonce:crypto.randomUUID()});
    store.put({...meta,key:partition,epoch,setupGeneration:ticket.generation,setupNonce:ticket.nonce});
    return {value:Object.freeze({kind:'started' as const,ticket}),clock:{now:shared.wall,tick:shared.mono}};
   },execution);
  },
  async importProvision(value:unknown,ticket:SetupTicket,execution:Execution&Readonly<{restoreDenied?:boolean}>={}){
   let p:Frozen<Provision>,t:SetupTicket;
   try{t={...ticket};if(t.account_id!==account_id||t.org_id!==org_id||!Number.isSafeInteger(t.generation)||!id(t.nonce))return result('invalid');p=validateProvision(structuredClone(value),{account_id,org_id});strictJSON(JSON.stringify(p));}catch{return result('invalid');}
   return editOperation(async(tx,check)=>{
    const partitions=tx.objectStore('partitions'),meta=await request<any>(partitions.get(partition));check();
    if((meta?.epoch??0)!==epoch||meta?.setupGeneration!==t.generation||meta?.setupNonce!==t.nonce)throw new AuthorityFailure('denied');
    const locked=meta?.denied||meta?.clockLocked||shared.knownLock;
    if(locked&&(!execution.restoreDenied||Date.parse(p.read_observation.checked_at)<=Math.max(meta?.lockedCheckedAt??0,shared.lockedCheckedAt,meta?.deniedAt??0,shared.deniedAt)))throw new AuthorityFailure('denied');
    const clock=sensible(p.read_observation,meta?.wall??0,!!locked);
    observeEditGeneration(meta);
    let restoredEditGeneration=Math.max(meta?.editGeneration??0,shared.editGeneration);
    const editDenied=meta?.editDenied||shared.editDenied;
    const restoreEdit=!!(p.edit_observation&&editDenied&&execution.restoreDenied&&Math.min(Date.parse(p.read_observation.checked_at),Date.parse(p.edit_observation.checked_at))>Math.max(meta?.editDeniedAt??0,shared.editDeniedAt)&&wall()<Date.parse(p.edit_observation.expires_at));
    if(restoreEdit){editObservation(p.edit_observation,meta?.wall??0);restoredEditGeneration++;}
    const retainEditDenial=editDenied&&!restoreEdit;
    if(p.edit_observation===null){shared.editGeneration=Math.max(shared.editGeneration,meta?.editGeneration??0)+1;shared.editDenied=true;shared.editDeniedAt=wall();}

    const setups=tx.objectStore('setups'),old=await request<any>(setups.get(partition));check();
    const childLosses={...meta?.childLosses};
    // A complete current child set discloses scoped losses even if later writes fail.
    for(const before of old?.value?.children??[]){
     const binding={actor_id:old.value.actor_id,membership_id:old.value.membership_id,child:before},key=childScope(binding),loss=childLoss(meta,key);
     if(old.value.actor_id!==p.actor_id||old.value.membership_id!==p.membership_id||!p.children.some(c=>c.child_id===before.child_id&&c.create_permission===before.create_permission)){
      const next={generation:loss.generation+1,deniedAt:wall(),denied:true};shared.childLosses.set(key,next);childLosses[key]=next;
     }
    }
    for(const child of p.children){
     const key=childScope({actor_id:p.actor_id,membership_id:p.membership_id,child}),loss=childLoss(meta,key);
     if(loss.denied&&Date.parse(child.checked_at)<=loss.deniedAt)throw new AuthorityFailure('denied');
     childLosses[key]={...loss,denied:false};
    }
    const sameBinding=old?.value?.actor_id===p.actor_id&&old?.value?.membership_id===p.membership_id;
    const merged:any=structuredClone(p),generations={...meta?.createGenerations},deniedAt={...meta?.createDeniedAt};
    // Nullable denial has no server timestamp: request order establishes freshness.
    for(const slot of ['create_all_observation','create_assigned_observation']){
     const latch=createLatches.get(slot);generations[slot]=Math.max(generations[slot]??0,latch?.generation??0);
     deniedAt[slot]=Math.max(deniedAt[slot]??0,latch?.deniedAt??0);
     if(p[slot as keyof Provision]===null){generations[slot]++;deniedAt[slot]=wall();createLatches.set(slot,{generation:generations[slot],deniedAt:deniedAt[slot]});}
     else{
      const incoming=(p as any)[slot];editObservation(incoming,meta?.wall??0);
      if(deniedAt[slot]&&Date.parse(incoming.checked_at)<=deniedAt[slot])throw new AuthorityFailure('denied');
      const before=old?.value?.[slot];if(sameBinding&&before&&Date.parse(before.checked_at)>Date.parse(incoming.checked_at))merged[slot]=before;
     }
    }
    if(merged.questionnaire){const q=merged.questionnaire,key=partition+'/'+q.questionnaire_version_id,definitions=tx.objectStore('definitions'),definition={questionnaire_id:q.questionnaire_id,questionnaire_version:q.questionnaire_version,definition:q.definition};const existing=await request<any>(definitions.get(key));check();if(existing&&canonical(existing.value)!==canonical(definition))throw Error('collision');if(!existing)definitions.put({key,value:definition});}
    if(sameBinding&&old?.value?.edit_observation&&merged.edit_observation&&Date.parse(old.value.edit_observation.checked_at)>Date.parse(merged.edit_observation.checked_at))merged.edit_observation=old.value.edit_observation;
    merged.children=merged.children.map((child:any)=>{const before=old?.value?.children?.find((c:any)=>c.child_id===child.child_id);return sameBinding&&before&&before.create_permission===child.create_permission&&before.child_revision===child.child_revision&&canonical(before.assignment)===canonical(child.assignment)&&Date.parse(before.checked_at)>Date.parse(child.checked_at)?before:child;});
    const observation=!meta?.observation||meta.observation.actor_id!==p.actor_id||meta.observation.membership_id!==p.membership_id||Date.parse(p.read_observation.checked_at)>Date.parse(meta.observation.checked_at)?p.read_observation:meta.observation;
    merged.read_observation=observation;validateProvision(merged,{account_id,org_id});
    // Provision may convey an edit denial; a setup response never fabricates per-record edit context.
    const next={...meta,key:partition,epoch,setupNonce:null,observation,wall:clock.now,denied:false,clockLocked:false,childLosses,createGenerations:generations,createDeniedAt:deniedAt,...(p.edit_observation===null||retainEditDenial?{editGeneration:Math.max(shared.editGeneration,meta?.editGeneration??0),editDenied:true,editDeniedAt:Math.max(shared.editDeniedAt,meta?.editDeniedAt??0)}:{editGeneration:restoredEditGeneration,editDenied:false,...(restoreEdit?{editRestoredAt:Math.min(Date.parse(p.read_observation.checked_at),Date.parse(p.edit_observation!.checked_at))}:{})})};
    setups.put({key:partition,value:merged});partitions.put(next);
    return {value:result('committed'),clock,validate:()=>{sensible(p.read_observation,clock.now,!!locked);if(p.edit_observation&&!retainEditDenial){if(shared.editGeneration>restoredEditGeneration)throw new AuthorityFailure('denied');shared.editGeneration=restoredEditGeneration;shared.editDenied=false;}shared.knownLock=false;shared.clockLock=false;shared.lockedCheckedAt=0;shared.deniedAt=0;for(const [key,loss] of Object.entries(childLosses))shared.childLosses.set(key,loss as ChildLoss);}};
   },execution);
  },
  async openCreate(child_id:string,execution:Execution={}){
   if(!id(child_id))return result('invalid');
   return editOperation(async(tx,check)=>{
    const meta=await request<any>(tx.objectStore('partitions').get(partition));check();const setup=await request<any>(tx.objectStore('setups').get(partition));check();
    const p=setup?.value,child=p?.children.find((c:any)=>c.child_id===child_id);if(!child||!p.questionnaire||p.create_state!=='ready')throw new AuthorityFailure('denied');
    const slot=createSlot(child.create_permission),reviewed:ReviewedCreate=freeze(structuredClone({account_id,org_id,actor_id:p.actor_id,membership_id:p.membership_id,epoch,create_generation:meta?.createGenerations?.[slot]??0,child,questionnaire:p.questionnaire,read_observation:p.read_observation,create_observation:p[slot]}));
    const childGeneration=childLoss(meta,childScope(reviewed)).generation;createBindings.set(reviewed,childGeneration);
    const validate=()=>createAuthority(meta,setup,reviewed,childGeneration),clock=validate();tx.objectStore('partitions').put({...meta,wall:clock.now});createReviews.add(reviewed);
    return {value:Object.freeze({kind:'opened' as const,reviewed}),clock,validate};
   },execution);
  },
  async saveCreate(reviewed:unknown,identities:Readonly<{capture_id:string;operation_id:string}>,input:unknown,execution:Execution={}){
   let r:any,ids:typeof identities,changes:any,pending:PendingCreate,serialized:string,content:string;
   try{
    r=structuredClone(reviewed);ids={...identities};object(ids,['capture_id','operation_id']);if(!id(ids.capture_id)||!id(ids.operation_id)||ids.capture_id===ids.operation_id||r.account_id!==account_id||r.org_id!==org_id)return result('invalid');
    changes=structuredClone(input);object(changes,['observation_date','answers','captured_at']);if(!date(changes.observation_date)||!instant(changes.captured_at))return result('invalid');
    for(const q of r.questionnaire.definition.questions){const a=changes.answers?.[q.id];if(q.type==='boolean'&&a&&a.value===false&&Object.hasOwn(a,'details'))delete a.details;}
    validateAnswers(r.questionnaire.definition,changes.answers);
    pending={account_id,org_id,command:{operation_id:ids.operation_id,command_version:1,capture_id:ids.capture_id,child_id:r.child.child_id,questionnaire_version_id:r.questionnaire.questionnaire_version_id,child_eligibility_ref:r.child.child_eligibility_ref,...changes}};
    serialized=JSON.stringify(pending.command);strictJSON(serialized);if(new TextEncoder().encode(serialized).byteLength>131072)return result('invalid');content=canonical({reviewed:r,pending});
   }catch{return result('invalid');}
   return editOperation<LocalCreateIntent['result']|Readonly<{kind:'action_id_reused'|'capture_id_reused'|'unavailable'}>>(async(tx,check)=>{
    const {meta,clock:readClock,validate:readValidate}=await readAccess(tx,check),actions=tx.objectStore('create_actions'),records=tx.objectStore('records'),key=partition+'/'+ids.operation_id;
    const existing=await request<any>(actions.get(key));check();readValidate();
    if(existing){if(!supportedCreate(existing)||existing.content!==content)return {value:result('action_id_reused'),clock:readClock,validate:readValidate};return {value:freeze(structuredClone(existing.result)),clock:readClock,validate:readValidate};}
    const setup=await request<any>(tx.objectStore('setups').get(partition));check();
    const validate=()=>createAuthority(meta,setup,r,createBindings.get(reviewed as object)??childLoss(meta,childScope(r)).generation),clock=validate();
    if(!createReviews.has(reviewed as object))return {value:result('unavailable'),clock,validate};
    const row=await request<any>(records.get(partition+'/'+ids.capture_id));check();validate();if(row)return {value:result('capture_id_reused'),clock};
    // IDs are disjoint across local command identities and captures, including other attempts.
    const cross=await request<any>(records.get(partition+'/'+ids.operation_id));check();const crossAction=await request<any>(actions.get(partition+'/'+ids.capture_id));check();const editIdentity=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+ids.operation_id));check();const editCaptureIdentity=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+ids.capture_id));check();if(cross||crossAction||editIdentity||editCaptureIdentity)return {value:result('action_id_reused'),clock};
    const definitions=tx.objectStore('definitions'),definitionKey=partition+'/'+r.questionnaire.questionnaire_version_id,definition={questionnaire_id:r.questionnaire.questionnaire_id,questionnaire_version:r.questionnaire.questionnaire_version,definition:r.questionnaire.definition},prior=await request<any>(definitions.get(definitionKey));check();if(prior&&canonical(prior.value)!==canonical(definition))throw Error('collision');if(!prior)definitions.add({key:definitionKey,value:definition});
    const outcome=Object.freeze({kind:'saved_locally' as const,...ids});
    const local_capture={capture_id:ids.capture_id,org_id,owner_account_id:account_id,owner_actor_id:r.actor_id,child_id:r.child.child_id,child_label:r.child.child_label,...r.questionnaire,...changes};
    validate();actions.add({key,partition,version:1,type:'capture.create',action_id:ids.operation_id,capture_id:ids.capture_id,pending,serialized,content,status:'Pending',result:outcome});
    records.add({key:partition+'/'+ids.capture_id,partition,local_capture,create_status:'Pending',create_action_id:ids.operation_id});tx.objectStore('partitions').put({...meta,wall:clock.now});
    return {value:outcome,clock,validate};
   },execution);
  },
  /** Retained immutable create is visible under own-read; setup expiry cannot veto recovery. */
  async lookupPreparedCreate(pinned:Readonly<{account_id:string;org_id:string;action_id:string}>,execution:Execution={}){
   let pin:typeof pinned;try{pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.action_id))return result('invalid');}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'blocked'}>|Frozen<{kind:'prepared';pending:PendingCreate;serialized:string;receipt?:NonNullable<CreateDelivery['receipt']>}>>(async(tx,check)=>{
    const {clock,validate}=await readAccess(tx,check),action=await request<any>(tx.objectStore('create_actions').get(partition+'/'+pin.action_id));check();validate();
    if(!supportedCreate(action)||!validCreateDelivery(action))return {value:result('blocked'),clock,validate};
    return {value:freeze({kind:'prepared' as const,pending:action.pending,serialized:action.serialized,...(action.delivery?.receipt?{receipt:action.delivery.receipt}:{})}),clock,validate};
   },execution);
  },
  /** Delayed sending honors known denial, but the POST owns current creation validation. */
  async prepareCreate(pinned:Readonly<{account_id:string;org_id:string;action_id:string}>,execution:Execution={}){
   let pin:typeof pinned;try{pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.action_id))return result('invalid');}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'blocked'|'denied'}>|Frozen<{kind:'prepared';pending:PendingCreate;serialized:string}>>(async(tx,check)=>{
    const {meta,clock,validate}=await readAccess(tx,check),action=await request<any>(tx.objectStore('create_actions').get(partition+'/'+pin.action_id));check();validate();
    if(!supportedCreate(action)||!validCreateDelivery(action)||action.delivery?.receipt)return {value:result('blocked'),clock,validate};
    const setup=await request<any>(tx.objectStore('setups').get(partition));check();validate();
    // A later explicit positive verification of either creation capability restores sending.
    // Expiry and today's child list remain server-owned for delayed delivery.
    const permitted=['create_all_observation','create_assigned_observation'].some(slot=>{
     const positive=setup?.value?.[slot],latch=createLatches.get(slot),deniedAt=Math.max(meta.createDeniedAt?.[slot]??0,latch?.deniedAt??0);
     return positive&&(!deniedAt||Date.parse(positive.checked_at)>deniedAt);
    });
    if(!permitted)return {value:result('denied'),clock,validate};
    return {value:freeze({kind:'prepared' as const,pending:action.pending,serialized:action.serialized}),clock,validate};
   },execution);
  },
  async consumeCreateReceipt(pinned:PendingCreate,value:unknown,execution:Execution={}){
   let pin:PendingCreate,outcome:any;try{pin=structuredClone(pinned);outcome=structuredClone(value);if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.command.operation_id))return result('invalid');object(outcome,['kind','receipt']);if(outcome.kind!=='committed')return result('invalid');}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'invalid'|'reconciled'}>>(async(tx,check)=>{
    const {clock,validate}=await readAccess(tx,check),actions=tx.objectStore('create_actions'),action=await request<any>(actions.get(partition+'/'+pin.command.operation_id));check();validate();
    if(!supportedCreate(action)||!validCreateDelivery(action)||canonical(action.pending)!==canonical(pin))return {value:result('invalid'),clock,validate};
    try{validateCreateReceipt(action,outcome.receipt);}catch{return {value:result('invalid'),clock,validate};}
    if(action.delivery?.receipt&&canonical(action.delivery.receipt)!==canonical(outcome.receipt))return {value:result('invalid'),clock,validate};
    const {attention:_,...delivery}=action.delivery??{};actions.put({...action,delivery:{...delivery,version:1,receipt:outcome.receipt}});
    const records=tx.objectStore('records'),row=await request<any>(records.get(partition+'/'+action.capture_id));check();if(row?.create_action_id===action.action_id&&row.create_status==='Needs attention')records.put({...row,create_status:'Pending'});
    // Existing history alone cannot acknowledge this operation: an explicit bound detail follows.
    return {value:result('reconciled'),clock,validate};
   },execution);
  },
  async attentionCreate(pinned:Readonly<{account_id:string;org_id:string;action_id:string}>,reason:string,execution:Execution={}){
   let pin:typeof pinned;try{pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.action_id)||!['assignment_unavailable','identity.actor_setup_required','questionnaire_version_unavailable','child_eligibility_unavailable','validation_failed','unsupported_command_version','access_denied'].includes(reason))return result('invalid');}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'blocked'|'retained'}>>(async(tx,check)=>{const {clock,validate}=await readAccess(tx,check),actions=tx.objectStore('create_actions'),action=await request<any>(actions.get(partition+'/'+pin.action_id));check();validate();if(!supportedCreate(action)||!validCreateDelivery(action))return {value:result('blocked'),clock,validate};if(action.delivery?.receipt)return {value:result('retained'),clock,validate};actions.put({...action,delivery:{...action.delivery,version:1,attention:reason}});const records=tx.objectStore('records'),row=await request<any>(records.get(partition+'/'+action.capture_id));check();if(row?.create_action_id===action.action_id&&row.create_status!=='Synced')records.put({...row,create_status:'Needs attention'});return {value:result('retained'),clock,validate};},execution);
  },
  async denyCreate(pinned:Readonly<{account_id:string;org_id:string;action_id:string}>,execution:Execution={}){
   let pin:typeof pinned;try{pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.action_id)||!current()||execution.signal?.aborted||execution.isCurrent&&execution.isCurrent()!==true)return result('invalid');}catch{return result('invalid');}
   // A verified current scoped denial survives failure to acquire/read/write IndexedDB.
   const deniedAt=wall();for(const slot of ['create_all_observation','create_assigned_observation']){const prior=createLatches.get(slot);createLatches.set(slot,{generation:(prior?.generation??0)+1,deniedAt:Math.max(deniedAt,prior?.deniedAt??0)});}
   return editOperation<Readonly<{kind:'denied'}>>(async(tx,check)=>{
    const {meta,clock,validate}=await readAccess(tx,check),generations={...meta.createGenerations},denials={...meta.createDeniedAt};
    for(const slot of ['create_all_observation','create_assigned_observation']){const latch=createLatches.get(slot)!;generations[slot]=Math.max(generations[slot]??0,latch.generation);denials[slot]=Math.max(denials[slot]??0,latch.deniedAt);}
    tx.objectStore('partitions').put({...meta,createGenerations:generations,createDeniedAt:denials});return {value:result('denied'),clock,validate};
   },execution);
  },
  async readCreateActions(bounds:Readonly<{limit?:number;after?:string}>={},execution:Execution={}){
   const limit=bounds.limit??30,after=bounds.after;if(!Number.isInteger(limit)||limit<1||limit>100||after!==undefined&&(typeof after!=='string'||!after.startsWith(partition+'/')||after>=partition+'/\uffff'))return result('unavailable');
   return editOperation(async(tx,check)=>{const {clock,validate}=await readAccess(tx,check);const rows=await request<LocalCreateIntent[]>(tx.objectStore('create_actions').getAll(IDBKeyRange.bound(after??partition+'/',partition+'/\uffff',after!==undefined),limit+1));check();validate();return {value:freeze({kind:'available' as const,actions:rows.slice(0,limit).filter(supportedCreate),next_key:rows.length>limit?rows[limit-1].key:null}),clock,validate};},execution);
  },
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
     partitions.put({...meta,key:partition,epoch,observation,wall:clock.now,editGeneration:restoredGeneration,editDenied:false,...(denied?{editRestoredAt:Math.min(Date.parse(context.read_observation.checked_at),Date.parse(context.edit_observation.checked_at))}:{})});
     return {value:result('committed'),clock,validate:()=>{if(shared.editGeneration>restoredGeneration)throw new AuthorityFailure('denied');editObservation(context.read_observation,clock.now);editObservation(context.edit_observation,clock.now);shared.editGeneration=restoredGeneration;shared.editDenied=false;}};
    },execution);
   }catch{return result('unavailable');}
  },
  async openEdit(capture_id:string,execution:Execution={}){
   if(!id(capture_id))return result('unavailable');
   return editOperation(async(tx,check)=>{
    const {row,meta,clock}=await editAccess(tx,capture_id,check);
    if(row.pending_edit_context&&!row.saved_edit&&row.baseline&&row.baseline.revision!=='1')throw Error('current_context_required');
    // A refresh can update the baseline, never the base of already saved local work.
    const local=!!row.pending_edit_context,context=local?row.pending_edit_context:row.edit_context;
    const reviewed:ReviewedEdit=freeze(structuredClone({account_id,org_id,capture_id,base:row.saved_edit?.base??(local?row.local_capture:row.baseline),
     capture:row.saved_edit?{...row.saved_edit.base,...row.saved_edit.changes}:(local?row.local_capture:row.baseline),
     edit_epoch:epoch,edit_generation:local?(meta.editGeneration??0):row.edit_generation,predecessor_action_id:row.saved_edit?.action_id??(local?row.create_action_id:null),baseline_revision:row.baseline?.revision??null,
     ...(local?{version:2,base_kind:'local_create',predecessor:{type:row.saved_edit?'capture.edit':'capture.create',action_id:row.saved_edit?.action_id??row.create_action_id}}:{}),
     read_observation:context.read_observation,edit_observation:context.edit_observation}));
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
    if(r.version===2){if(!date(changes.observation_date))throw Error('invalid_date');validateAnswers(r.base.definition,changes.answers);}else validateDetail({...structuredClone(r.base),...changes},{account_id,org_id,capture_id:r.capture_id});
    const command=JSON.stringify({operation_id:action_id,command_version:1,expected_revision:'9223372036854775807',...changes});
    strictJSON(command);if(new TextEncoder().encode(command).byteLength>131072)return result('invalid');
   }catch{return result('invalid');}
   return editOperation(async(tx,check)=>{
    const {row,meta,clock}=await editAccess(tx,r.capture_id,check),actions=tx.objectStore('edit_actions');
    // The exact evidence actually reviewed must still be valid independently.
    editAuthority(meta,row,r);
    const key=partition+'/'+action_id,content=canonical({reviewed:r,input:changes}),existing=await request<any>(actions.get(key));check();
    const validate=()=>editAuthority(meta,row,r);validate();
    if(existing){if(existing.content!==content)return {value:result('action_id_reused'),clock};if(r.version===2&&(existing.version!==2||!supportedAction(existing)||!await originalLocalBase(tx,existing,check)))return {value:result('unavailable'),clock,validate};return {value:freeze(structuredClone(existing.result)),clock,validate};}
    const createIdentity=await request<any>(tx.objectStore('create_actions').get(key));check();
    if(createIdentity)return {value:result('action_id_reused'),clock,validate};
    if(!reviews.has(reviewed as object))return {value:result('unavailable'),clock};
    const progress=r.version===2?(!row.baseline||await ownProgress(tx,row,check)):row.baseline.revision===r.base.revision||await ownProgress(tx,row,check);
    const stale=(row.saved_edit?.action_id??(r.version===2?row.create_action_id:null))!==r.predecessor_action_id||(row.baseline?.revision??null)!==r.baseline_revision||!progress||row.edit_status==='Needs attention'||!!row.pending||!!row.conflict;
    const outcome=Object.freeze({kind:stale?'needs_attention' as const:'saved_locally' as const,action_id});
    const intent={key,partition,version:r.version===2?2:1,...(r.version===2?{base_kind:'local_create',predecessor:r.predecessor}:{}),type:'capture.edit',action_id,capture_id:r.capture_id,content,base:r.base,changes,
     predecessor_action_id:r.predecessor_action_id,expected_revision:r.predecessor_action_id===null?r.base.revision:null,
     read_observation:r.read_observation,edit_observation:r.edit_observation,status:stale?'Needs attention':'Pending',result:outcome};
    validate();actions.add(intent);
    if(!stale)tx.objectStore('records').put({...row,saved_edit:{action_id,base:r.base,changes,...(r.version===2?{base_kind:'local_create'}:{})},edit_status:'Pending'});
    return {value:outcome,clock,validate};
   },execution);
  },
  /** Inert preparation only: transactionally freeze bytes before returning any command. */
  async lookupPreparedEdit(pinned:Readonly<{account_id:string;org_id:string;action_id:string}>,execution:Execution={}){
   let pin:typeof pinned;
   try{pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.action_id))return result('invalid');}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'missing'|'blocked'}>|Frozen<{kind:'prepared';pending:PreparedEdit;serialized:string}>>(async(tx,check)=>{
    const {clock,validate}=await readAccess(tx,check);
    const action=await request<any>(tx.objectStore('edit_actions').get(partition+'/'+pin.action_id));check();validate();
    if(!supported(action)||!await originalLocalBase(tx,action,check))return {value:result('blocked'),clock,validate};
    if(!action.delivery)return {value:result('missing'),clock,validate};
    if(!await checkedPrepared(tx,action,check)||action.delivery.conflict)return {value:result('blocked'),clock,validate};
    return {value:freeze({kind:'prepared' as const,pending:action.delivery.pending,serialized:action.delivery.serialized}),clock,validate};
   },execution);
  },
  /** Current own-detail adds no new read/edit observation and cannot restore denial. */
  async importCurrentDetail(value:unknown,pinned:Readonly<{account_id:string;org_id:string;capture_id:string}>,execution:Execution={}){
   let baseline:Frozen<CaptureDetail>;
   try{const pin={...pinned};if(pin.account_id!==account_id||pin.org_id!==org_id||!id(pin.capture_id))return result('invalid');const captured=structuredClone(value);if(new TextEncoder().encode(JSON.stringify(captured)).byteLength>524288)return result('invalid');baseline=validateDetail(captured,pin);}catch{return result('invalid');}
   return editOperation<Readonly<{kind:'invalid'|'imported'}>>(async(tx,check)=>{
    const {clock,validate}=await readAccess(tx,check);
    const row=await request<any>(tx.objectStore('records').get(partition+'/'+baseline.capture_id));check();
    if(row?.create_action_id){const action=await request<any>(tx.objectStore('create_actions').get(partition+'/'+row.create_action_id));check();if(supportedCreate(action)&&action.delivery?.receipt&&(!validCreateDelivery(action)||!createMatches(action,baseline)))return {value:result('invalid'),clock,validate};}
    await importBaseline(tx,baseline,check);validate();
    return {value:result('imported'),clock,validate};
   },execution);
  },
  async prepareEdit(action_id:string,execution:Execution={}){
   if(!id(action_id))return result('invalid');
   return editOperation<Readonly<{kind:'blocked'|'invalid'}>|Frozen<{kind:'prepared';pending:PreparedEdit;serialized:string}>>(async(tx,check)=>{
    const actions=tx.objectStore('edit_actions'),action=await request<any>(actions.get(partition+'/'+action_id));check();
    if(!supported(action)||!await originalLocalBase(tx,action,check)){const {clock,validate}=await readAccess(tx,check);return {value:result('blocked'),clock,validate};}
    const {row,meta,clock}=await editAccess(tx,action.capture_id,check),validate=()=>editAuthority(meta,row);validate();
    if(action.delivery){
     if(!await checkedPrepared(tx,action,check)||action.delivery.conflict)return {value:result('blocked'),clock,validate};
     return {value:freeze({kind:'prepared' as const,pending:action.delivery.pending,serialized:action.delivery.serialized}),clock,validate};
    }
    if(row.pending||row.conflict||row.edit_status==='Needs attention')return {value:result('blocked'),clock,validate};
    if((action.version===2?!!row.baseline:row.baseline.revision!==action.base.revision)&&!await ownProgress(tx,row,check)){
     validate();tx.objectStore('records').put({...row,edit_status:'Needs attention'});
     return {value:result('blocked'),clock,validate};
    }
    let expected_revision=action.expected_revision;
    if(action.version===2&&action.predecessor.type==='capture.create'){
     if(row.create_action_id!==action.predecessor.action_id)return {value:result('blocked'),clock,validate};
     const parent=await request<any>(tx.objectStore('create_actions').get(partition+'/'+action.predecessor.action_id));check();validate();
     if(!supportedCreate(parent)||!validCreateDelivery(parent)||parent.capture_id!==action.capture_id||!parent.delivery?.receipt)return {value:result('blocked'),clock,validate};
     expected_revision=parent.delivery.receipt.result.revision;
    }else if(action.predecessor_action_id!==null){
     const parent=await request<any>(actions.get(partition+'/'+action.predecessor_action_id));check();validate();
     if(!await checkedPrepared(tx,parent,check)||parent.capture_id!==action.capture_id||parent.delivery.conflict||!parent.delivery.receipt)return {value:result('blocked'),clock,validate};
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
   try{if(!current()||execution.signal?.aborted||execution.isCurrent&&execution.isCurrent()!==true)return result('unavailable');}catch{return result('unavailable');}
   const previous={generation:shared.editGeneration,denied:shared.editDenied,deniedAt:shared.editDeniedAt};
   const provisional={generation:previous.generation+1,deniedAt:Math.max(previous.deniedAt,wall())};
   shared.editGeneration=provisional.generation;shared.editDenied=true;shared.editDeniedAt=provisional.deniedAt;
   const outcome=await editOperation(async(tx,check)=>{
    const store=tx.objectStore('partitions'),meta=await request<any>(store.get(partition));check();
    if((meta?.epoch??0)!==epoch){
     // Retract only this invocation's provisional negative. Never clear another
     // denial or restoration observed while the epoch check was queued.
     if(shared.editGeneration===provisional.generation&&shared.editDeniedAt===provisional.deniedAt){shared.editGeneration=previous.generation;shared.editDenied=previous.denied;shared.editDeniedAt=previous.deniedAt;}
     throw Error('superseded');
    }
    shared.editGeneration=Math.max(shared.editGeneration,meta?.editGeneration??0)+1;shared.editDenied=true;shared.editDeniedAt=Math.max(shared.editDeniedAt,wall());
    store.put({...meta,key:partition,epoch,editGeneration:shared.editGeneration,editDenied:true,editDeniedAt:shared.editDeniedAt});
    return {value:result('denied'),clock:{now:wall(),tick:mono()}};
   },execution);
   return outcome;
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
