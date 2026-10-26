/** Candidate owner consumer; deliberately unconnected to startup/editor/storage. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {createCapture,type PendingCreate,type CreateResult} from './create.js';
export function createCreateEntry(configuration: AuthEntryOptions & {createTimeoutMs?:number}) {
 const {createTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async create(pending:PendingCreate):Promise<CreateResult> {
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  const finish=(result:CreateResult):CreateResult=>lease.isCurrent()?result:Object.freeze({kind:'superseded'});
  try {
   let captured:PendingCreate;
   try{captured=Object.freeze({...pending});}catch{return finish(Object.freeze({kind:'invalid_request'}));}
   if(captured.account_id!==lease.session.account_id||captured.account_id!==lease.context.account_id||
      captured.org_id!==options.org||captured.org_id!==lease.context.authorization_scope.org_id)return finish(Object.freeze({kind:'invalid_request'}));
   // createCapture synchronously snapshots nested command input before its first await.
   const result=await createCapture(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:createTimeoutMs});
   return finish(result);
  }finally{lease.release();}
 }};
}
