/** Candidate consumer, unconnected to browser startup or operation state. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {loadEditContext,type PendingEditContext,type EditContextResult} from './edit-context.js';
export function createEditContextEntry(configuration:AuthEntryOptions & {editContextTimeoutMs?:number}) {
 const {editContextTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async load(pending:PendingEditContext):Promise<EditContextResult> {
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  let result:EditContextResult=Object.freeze({kind:'invalid_request'});
  try {
   let captured:PendingEditContext|undefined;
   try{captured=Object.freeze({...pending});}catch{/* Invalid caller input stays private. */}
   if(captured && captured.account_id===lease.session.account_id && captured.account_id===lease.context.account_id &&
      captured.org_id===options.org && captured.org_id===lease.context.authorization_scope.org_id){
    result=await loadEditContext(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:editContextTimeoutMs});
   }
  }catch{result=Object.freeze({kind:'verification_unavailable'});}
  finally{
   // Every result, including local validation failure, crosses the same fence
   // before release aborts this lease's signal.
   try{if(!lease.isCurrent())result=Object.freeze({kind:'superseded'});}
   catch{result=Object.freeze({kind:'superseded'});}
   try{lease.release();}catch{result=Object.freeze({kind:'verification_unavailable'});}
  }
  return result;
 }};
}
