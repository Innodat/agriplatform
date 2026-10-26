/** Candidate consumer, unconnected to browser startup or operation state. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {loadProvision,type PendingProvision,type ProvisionResult} from './provision.js';
export function createProvisionEntry(configuration:AuthEntryOptions & {provisionTimeoutMs?:number}) {
 const {provisionTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async load(pending:PendingProvision):Promise<ProvisionResult> {
  const started=performance.now(),duration=provisionTimeoutMs??10000;
  const lease=acquireExecution();
  if(!lease)return Object.freeze({kind:'superseded'});
  let result:ProvisionResult=Object.freeze({kind:'invalid_request'});
  try {
   let captured:PendingProvision|undefined;
   try{captured=Object.freeze({...pending});}catch{/* Invalid caller input stays private. */}
   if(captured && captured.account_id===lease.session.account_id && captured.account_id===lease.context.account_id &&
      captured.org_id===options.org && captured.org_id===lease.context.authorization_scope.org_id){
    const remaining=duration-(performance.now()-started);
    result=Number.isFinite(duration)&&duration>0&&duration<=10000&&remaining<=0?Object.freeze({kind:'verification_unavailable'}):
     await loadProvision(lease.session,captured,{signal:lease.signal,isCurrent:lease.isCurrent,request:options.request,timeoutMs:Number.isFinite(duration)&&duration>0&&duration<=10000?remaining:duration});
   }
  }catch{result=Object.freeze({kind:'verification_unavailable'});}
  finally{
   // Every result, including local validation failure, crosses the same fence
   // before release aborts this lease's signal.
   try{if(!lease.isCurrent())result=Object.freeze({kind:'superseded'});}
   catch{result=Object.freeze({kind:'superseded'});}
   try{lease.release();}catch{result=Object.freeze({kind:'verification_unavailable'});}
   if(Number.isFinite(duration)&&duration>0&&duration<=10000&&performance.now()-started>=duration)result=Object.freeze({kind:'verification_unavailable'});
  }
  return result;
 }};
}
