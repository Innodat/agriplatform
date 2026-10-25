/** Candidate owner consumer; deliberately not connected to browser startup or operation state. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {recoverOperation,type PendingRecovery,type RecoveryResult} from './recovery.js';
export function createRecoveryEntry(configuration: AuthEntryOptions & {recoveryTimeoutMs?:number}) {
 const {recoveryTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async recover(pending:PendingRecovery):Promise<RecoveryResult> {
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  try {
   let captured:PendingRecovery;
   try{captured=Object.freeze({...pending});}catch{return Object.freeze({kind:'invalid_request'});}
   if(captured.account_id!==lease.session.account_id||captured.account_id!==lease.context.account_id||
      captured.org_id!==options.org||captured.org_id!==lease.context.authorization_scope.org_id)return Object.freeze({kind:'invalid_request'});
   const result=await recoverOperation(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:recoveryTimeoutMs});
   return lease.isCurrent()?result:Object.freeze({kind:'superseded'});
  }finally{lease.release();}
 }};
}
