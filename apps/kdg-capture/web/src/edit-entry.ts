/** Candidate owner consumer; deliberately unconnected to startup/editor/storage. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {editCapture,type PendingEdit,type EditResult} from './edit.js';
export function createEditEntry(configuration: AuthEntryOptions & {editTimeoutMs?:number}) {
 const {editTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async edit(pending:PendingEdit):Promise<EditResult> {
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  const finish=(result:EditResult):EditResult=>lease.isCurrent()?result:Object.freeze({kind:'superseded'});
  try {
   let captured:PendingEdit;
   try{captured=Object.freeze({...pending});}catch{return finish(Object.freeze({kind:'invalid_request'}));}
   if(captured.account_id!==lease.session.account_id||captured.account_id!==lease.context.account_id||
      captured.org_id!==options.org||captured.org_id!==lease.context.authorization_scope.org_id)return finish(Object.freeze({kind:'invalid_request'}));
   // editCapture synchronously snapshots nested command input before its first await.
   const result=await editCapture(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:editTimeoutMs});
   return finish(result);
  }finally{lease.release();}
 }};
}
