/** Server-current retained-proposal review holds no Auth lease; every explicit invocation acquires and releases one. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {resolveConflict,type ConflictResolutionRequest,type ConflictResolutionResult,type ConflictResolutionStore} from './conflict-resolution.js';
import type {ConflictPin,ReviewedConflict} from './history-store.js';
export function createConflictResolutionEntry(configuration:AuthEntryOptions & Readonly<{store:ConflictResolutionStore;resolutionTimeoutMs?:number}>){
 const {store,resolutionTimeoutMs,...options}=Object.freeze({...configuration}),{acquireExecution,...entry}=createAuthEntry(options);
 const run=async(operation:ConflictResolutionRequest):Promise<ConflictResolutionResult>=>{
  const started=performance.now(),duration=resolutionTimeoutMs??30000,lease=acquireExecution();if(!lease)return Object.freeze({kind:'superseded'});
  let result:ConflictResolutionResult=Object.freeze({kind:'invalid_request'});
  try{
   const pin=operation.kind==='review'?operation.pin:operation.reviewed;
   if(pin.account_id===lease.session.account_id&&pin.account_id===lease.context.account_id&&pin.org_id===options.org&&pin.org_id===lease.context.authorization_scope.org_id){
    const remaining=duration-(performance.now()-started);result=!Number.isFinite(duration)||duration<=0||duration>30000?Object.freeze({kind:'invalid_request'}):remaining<=0?Object.freeze({kind:'verification_unavailable'}):await resolveConflict(lease.session,operation,{store,request:options.request,signal:lease.signal,isCurrent:lease.isCurrent,timeoutMs:remaining});
   }
  }catch{result=Object.freeze({kind:'verification_unavailable'});}
  finally{
   try{if(!lease.isCurrent())result=Object.freeze({kind:'superseded'});}catch{result=Object.freeze({kind:'superseded'});}
   try{lease.release();}catch{result=Object.freeze({kind:'verification_unavailable'});}
   if(performance.now()-started>=duration)result=Object.freeze({kind:'verification_unavailable'});
  }
  return result;
 };
 return {...entry,review:(pin:ConflictPin,mode:'current'|'replacement'='current')=>run({kind:'review',pin,mode}),useCurrent:(reviewed:ReviewedConflict,decision_id:string)=>run({kind:'current',reviewed,decision_id}),saveReplacement:(reviewed:ReviewedConflict,decision_id:string,action_id:string,changes:unknown)=>run({kind:'replacement',reviewed,decision_id,action_id,changes})};
}
