/** Explicit unmounted Auth boundary; each invocation owns exactly one execution lease. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {deliverSavedEdit,type EditDeliveryStore,type SavedEditAction,type EditDeliveryResult} from './edit-delivery.js';
export function createEditDeliveryEntry(configuration:AuthEntryOptions & Readonly<{store:EditDeliveryStore;deliveryTimeoutMs?:number}>){
 const {store,deliveryTimeoutMs,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async deliver(pending:SavedEditAction):Promise<EditDeliveryResult>{
  const started=performance.now(),duration=deliveryTimeoutMs??30000;
  const lease=acquireExecution();if(!lease)return Object.freeze({kind:'superseded'});
  let result:EditDeliveryResult=Object.freeze({kind:'invalid_request'});
  try{
   const pin=Object.freeze({...pending});
   if(pin.account_id===lease.session.account_id&&pin.account_id===lease.context.account_id&&pin.org_id===options.org&&pin.org_id===lease.context.authorization_scope.org_id){
    const remaining=duration-(performance.now()-started);
    result=Number.isFinite(duration)&&duration>0&&duration<=30000&&remaining<=0?Object.freeze({kind:'verification_unavailable'}):
     await deliverSavedEdit(lease.session,pin,{store,request:options.request,signal:lease.signal,isCurrent:lease.isCurrent,timeoutMs:Number.isFinite(duration)&&duration>0&&duration<=30000?remaining:duration});
   }
  }catch{result=Object.freeze({kind:'verification_unavailable'});}
  finally{
   try{if(!lease.isCurrent())result=Object.freeze({kind:'superseded'});}catch{result=Object.freeze({kind:'superseded'});}
   try{lease.release();}catch{result=Object.freeze({kind:'verification_unavailable'});}
   if(Number.isFinite(duration)&&duration>0&&duration<=30000&&performance.now()-started>=duration)result=Object.freeze({kind:'verification_unavailable'});
  }
  return result;
 }};
}
