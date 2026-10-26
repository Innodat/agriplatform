/** Explicit retained own-proposal decisions; no sender or mounted entry. */
import type {Session} from './entry.js';
import type {ConflictPin,ReviewedConflict,openHistoryStore} from './history-store.js';
import {readCapture,type ReadResult} from './read.js';
import {loadEditContext,type EditContextResult} from './edit-context.js';
import {id,object} from './read-validation.js';
export type ConflictResolutionStore=Pick<Awaited<ReturnType<typeof openHistoryStore>>,'lookupResolution'|'openConflict'|'useCurrent'|'saveConflictReplacement'|'deny'|'denyEdit'>;
export type ConflictResolutionRequest=Readonly<{kind:'review';pin:ConflictPin;mode:'current'|'replacement'}>|Readonly<{kind:'current';reviewed:ReviewedConflict;decision_id:string}>|Readonly<{kind:'replacement';reviewed:ReviewedConflict;decision_id:string;action_id:string;changes:unknown}>;
export type ConflictResolutionOptions=Readonly<{store:ConflictResolutionStore;signal:AbortSignal;isCurrent:()=>boolean;request?:typeof fetch;timeoutMs?:number}>;
export type ConflictResolutionResult=Awaited<ReturnType<ConflictResolutionStore['openConflict']|ConflictResolutionStore['useCurrent']|ConflictResolutionStore['saveConflictReplacement']>>|Exclude<ReadResult|EditContextResult,{kind:'loaded'}>;
/** Each call is bounded across authority, HTTP, storage and publication. */
export async function resolveConflict(session:Session,operation:ConflictResolutionRequest,configuration:ConflictResolutionOptions):Promise<ConflictResolutionResult>{
 const started=performance.now();let auth:Session,op:ConflictResolutionRequest,pin:ConflictPin,options:ConflictResolutionOptions;
 try{
  auth=Object.freeze({account_id:session.account_id,access_token:session.access_token});options=Object.freeze({...configuration});
  // Preserve the original branded review; snapshot mutable replacement values before awaiting.
  op=operation.kind==='replacement'?{...operation,changes:structuredClone(operation.changes)}:{...operation};
  const source=op.kind==='review'?op.pin:op.reviewed;pin={account_id:source.account_id,org_id:source.org_id,capture_id:source.capture_id,source_action_id:source.source_action_id};
  if(!['review','current','replacement'].includes(op.kind)||op.kind==='review'&&!['current','replacement'].includes(op.mode)||pin.account_id!==auth.account_id||Object.values(pin).some(value=>!id(value))||!(options.signal instanceof AbortSignal)||typeof options.isCurrent!=='function'||!options.store||options.request!==undefined&&typeof options.request!=='function')return Object.freeze({kind:'invalid_request'});
  if(op.kind==='review')object(op.pin,['account_id','org_id','capture_id','source_action_id']);
  else if(!id(op.decision_id)||op.kind==='replacement'&&!id(op.action_id))return Object.freeze({kind:'invalid_request'});
 }catch{return Object.freeze({kind:'invalid_request'});}
 const duration=options.timeoutMs??30000;if(!Number.isFinite(duration)||duration<=0||duration>30000)return Object.freeze({kind:'invalid_request'});
 const deadline=started+duration,controller=new AbortController();let timedOut=false;
 const stale=():ConflictResolutionResult|undefined=>{let fresh=false;try{fresh=options.isCurrent()===true;}catch{}return options.signal.aborted?{kind:'cancelled'}:!fresh?{kind:'superseded'}:timedOut||performance.now()>=deadline?{kind:'verification_unavailable'}:undefined;};
 const execution={signal:controller.signal,isCurrent:()=>!stale()},guard=()=>{const failure=stale();if(failure){controller.abort();throw failure;}},phase=()=>{guard();return {...execution,request:options.request,timeoutMs:Math.min(10000,deadline-performance.now())};};
 let stop!:(value:ConflictResolutionResult)=>void;const stopped=new Promise<ConflictResolutionResult>(resolve=>{stop=resolve;});
 const abort=()=>{controller.abort();stop(stale()??{kind:'cancelled'});};options.signal.addEventListener('abort',abort,{once:true});
 const timer=setTimeout(()=>{timedOut=true;controller.abort();stop({kind:'verification_unavailable'});},Math.max(0,deadline-performance.now()));
 const work=async():Promise<ConflictResolutionResult>=>{
  guard();const readPin={account_id:pin.account_id,org_id:pin.org_id,capture_id:pin.capture_id};
  if(op.kind!=='review'){
   const retained=await options.store.lookupResolution({reviewed:op.reviewed,decision_id:op.decision_id,action_id:op.kind==='replacement'?op.action_id:null,changes:op.kind==='replacement'?op.changes:null},execution);guard();
   if(retained.kind!=='missing')return retained;
  }
  const replacement=op.kind==='replacement'||op.kind==='review'&&op.mode==='replacement';
  if(replacement){
   const loaded=await loadEditContext(auth,readPin,phase());guard();
   if(loaded.kind==='error'&&loaded.status===403){
    await options.store.denyEdit(pin,execution);guard();
    const probe=await readCapture(auth,readPin,phase());guard();
    // An outage or malformed response is not a verified loss of own-read.
    if(probe.kind==='error'&&probe.status===403){await options.store.deny(pin,execution);guard();}
    return loaded;
   }
   if(loaded.kind!=='loaded')return loaded;
   if(op.kind==='review')return options.store.openConflict(pin,loaded.context,execution);
   if(op.kind!=='replacement')return {kind:'invalid_request'};
   return options.store.saveConflictReplacement(op.reviewed,op.decision_id,op.action_id,op.changes,loaded.context,execution);
  }
  const loaded=await readCapture(auth,readPin,phase());guard();
  if(loaded.kind==='error'&&loaded.status===403){await options.store.deny(pin,execution);guard();return loaded;}
  if(loaded.kind!=='loaded')return loaded;
  if(op.kind==='review')return options.store.openConflict(pin,loaded.snapshot,execution);
  if(op.kind!=='current')return {kind:'invalid_request'};
  return options.store.useCurrent(op.reviewed,op.decision_id,loaded.snapshot,execution);
 };
 try{return Object.freeze(stale()??await Promise.race([work().then(value=>{guard();return value;}),stopped]));}
 catch{return Object.freeze(stale()??{kind:'verification_unavailable'});}
 finally{clearTimeout(timer);options.signal.removeEventListener('abort',abort);controller.abort();}
}
