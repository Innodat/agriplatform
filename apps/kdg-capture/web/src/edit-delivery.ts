/** Explicit single-action consumer. No startup, queue or automatic retry integration. */
import type {Session} from './entry.js';
import type {openHistoryStore,PreparedEdit} from './history-store.js';
import {recoverOperation,type RecoveryResult} from './recovery.js';
import {editCapture,type EditResult} from './edit.js';
import {readCapture,type ReadResult} from './read.js';
import {id,freeze} from './read-validation.js';
export type SavedEditAction=Readonly<{account_id:string;org_id:string;action_id:string}>;
export type EditDeliveryStore=Pick<Awaited<ReturnType<typeof openHistoryStore>>,'lookupPreparedEdit'|'prepareEdit'|'consumeEditReceipt'|'consumeEditConflict'|'importCurrentDetail'|'deny'|'denyEdit'>;
export type EditDeliveryOptions=Readonly<{store:EditDeliveryStore;signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number}>;
export type EditDeliveryResult=Readonly<{kind:'acknowledged';readback:'imported'|'unavailable'}>|Readonly<{kind:'conflict';readback:'imported'|'unavailable'}>|
 Readonly<{kind:'blocked'|'invalid'|'expired'|'denied'|'unavailable'|'invalid_request'|'authentication_required'|'invalid_response'|'verification_unavailable'|'cancelled'|'superseded'}>|
 Extract<RecoveryResult|EditResult|ReadResult,{kind:'error'}>;
const safe=<T extends EditDeliveryResult>(result:T):T=>Object.freeze(result);
/** Own-read gates retained commands; own-edit is checked independently before each send. */
export async function deliverSavedEdit(session:Session,pending:SavedEditAction,configuration:EditDeliveryOptions):Promise<EditDeliveryResult>{
 const started=performance.now();
 let auth:Session,pin:SavedEditAction,options:EditDeliveryOptions;
 try{
  auth=Object.freeze({account_id:session.account_id,access_token:session.access_token});pin=Object.freeze({...pending});options=Object.freeze({...configuration});
  if(!id(pin.account_id)||!id(pin.org_id)||!id(pin.action_id)||pin.account_id!==auth.account_id||!(options.signal instanceof AbortSignal)||typeof options.isCurrent!=='function'||!options.store||options.request!==undefined&&typeof options.request!=='function')return safe({kind:'invalid_request'});
 }catch{return safe({kind:'invalid_request'});}
 const duration=options.timeoutMs??30000;
 if(!Number.isFinite(duration)||duration<=0||duration>30000)return safe({kind:'invalid_request'});
 const deadline=started+duration,controller=new AbortController();let timedOut=false;
 const current=()=>{try{return options.isCurrent()===true;}catch{return false;}};
 const stale=():EditDeliveryResult|undefined=>{
  const fresh=current();
  return options.signal.aborted?safe({kind:'cancelled'}):!fresh?safe({kind:'superseded'}):timedOut||performance.now()>=deadline?safe({kind:'verification_unavailable'}):undefined;
 };
 const execution={signal:controller.signal,isCurrent:()=>!stale()};
 const stop=()=>controller.abort();options.signal.addEventListener('abort',stop,{once:true});
 let expire!:()=>void;
 const stopped=new Promise<EditDeliveryResult>(resolve=>{expire=()=>resolve(stale()??safe({kind:'verification_unavailable'}));});
 const abort=()=>{stop();expire();};options.signal.addEventListener('abort',abort,{once:true});
 const timer=setTimeout(()=>{timedOut=true;stop();expire();},Math.max(0,deadline-performance.now()));
 const guard=()=>{const failure=stale();if(failure){controller.abort();throw failure;}};
 const phase=()=>{guard();return {...execution,request:options.request,timeoutMs:Math.min(10000,deadline-performance.now())};};
 const store=options.store;
 const readback=async(command:PreparedEdit):Promise<'imported'|'unavailable'>=>{
  try{
  guard();const detail=await readCapture(auth,{account_id:command.account_id,org_id:command.org_id,capture_id:command.capture_id},phase());guard();
  if(detail.kind==='error'&&detail.status===403){await store.deny(pin,execution);guard();return 'unavailable';}
  if(detail.kind!=='loaded')return 'unavailable';
  const imported=await store.importCurrentDetail(detail.snapshot,command,execution);guard();return imported.kind==='imported'?'imported':'unavailable';
  }catch{guard();return 'unavailable';}
 };
 const work=async():Promise<EditDeliveryResult>=>{
  guard();let prepared=await store.lookupPreparedEdit(pin,execution);guard();
  if(prepared.kind==='missing'){prepared=await store.prepareEdit(pin.action_id,execution);guard();}
  if(prepared.kind!=='prepared')return prepared.kind==='missing'?safe({kind:'blocked'}):safe({kind:prepared.kind});
  let command:PreparedEdit,serialized:string;
  try{serialized=prepared.serialized;command=freeze(structuredClone(prepared.pending));}catch{return safe({kind:'invalid_request'});}
  // Validate the store's returned scope before any HTTP, including custom adapters.
  if(command.account_id!==pin.account_id||command.org_id!==pin.org_id||command.command.operation_id!==pin.action_id||!id(command.capture_id)||typeof serialized!=='string'||serialized!==JSON.stringify(command.command))return safe({kind:'invalid_request'});
  const recovered=await recoverOperation(auth,{account_id:pin.account_id,org_id:pin.org_id,operation_id:pin.action_id,command_type:'capture.edit',capture_id:command.capture_id},phase());guard();
  if(recovered.kind==='error'&&recovered.status===403){await store.deny(pin,execution);guard();return safe({kind:'denied'});}
  let outcome:EditResult|RecoveryResult=recovered;
  if(recovered.kind==='unresolved'){
   // Recovery may take time: current edit authority must be rechecked before PUT.
   const authorized=await store.prepareEdit(pin.action_id,execution);guard();
   if(authorized.kind!=='prepared')return authorized;
   if(authorized.serialized!==serialized||JSON.stringify(authorized.pending)!==JSON.stringify(command))return safe({kind:'invalid_request'});
   outcome=await editCapture(auth,command,phase());guard();
   if(outcome.kind==='error'&&outcome.status===403){
    await store.denyEdit(pin,execution);guard();
    const probe=await readCapture(auth,{account_id:command.account_id,org_id:command.org_id,capture_id:command.capture_id},phase());guard();
    if(probe.kind==='loaded'){
     await store.importCurrentDetail(probe.snapshot,command,execution);guard();
    }else{await store.deny(pin,execution);guard();}
    return safe({kind:'denied'});
   }
  }
  if(outcome.kind==='committed'){
   const consumed=await store.consumeEditReceipt(command,outcome,execution);guard();
   if(consumed.kind!=='reconciled')return safe({kind:consumed.kind});
   return safe({kind:'acknowledged',readback:await readback(command)});
  }
  if(outcome.kind==='error'&&outcome.status===409&&outcome.error_id==='kdg_capture.capture_revision_conflict'){
   const consumed=await store.consumeEditConflict(command,outcome,execution);guard();
   if(consumed.kind!=='reconciled')return safe({kind:consumed.kind});
   return safe({kind:'conflict',readback:await readback(command)});
  }
  // Only unresolved recovery enters sending; every other outcome remains uncertain.
  return outcome.kind==='unresolved'?safe({kind:'verification_unavailable'}):outcome;
 };
 try{
  const value=await Promise.race([work(),stopped]);return stale()??safe(value);
 }catch{return stale()??safe({kind:'verification_unavailable'});}
 finally{clearTimeout(timer);options.signal.removeEventListener('abort',stop);options.signal.removeEventListener('abort',abort);controller.abort();}
}
