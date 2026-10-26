/** Candidate consumer, unconnected to browser startup or operation state. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {historyCaptures,type PendingHistory,type HistoryResult} from './history.js';
export function createHistoryEntry(configuration:AuthEntryOptions & {historyTimeoutMs?:number}) {
 const {historyTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async history(pending:PendingHistory):Promise<HistoryResult> {
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  let result:HistoryResult=Object.freeze({kind:'invalid_request'});
  try {
   let captured:PendingHistory|undefined;
   try{captured=Object.freeze({...pending});}catch{/* Invalid caller input stays private. */}
   if(captured && captured.account_id===lease.session.account_id && captured.account_id===lease.context.account_id &&
      captured.org_id===options.org && captured.org_id===lease.context.authorization_scope.org_id){
    result=await historyCaptures(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:historyTimeoutMs});
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
