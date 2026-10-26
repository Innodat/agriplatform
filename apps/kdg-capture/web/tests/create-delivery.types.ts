import {deliverSavedCreate,type CreateDeliveryResult} from '../src/create-delivery.js';
import {openHistoryStore} from '../src/history-store.js';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>;
async function checks(){
 const pin={account_id:'id',org_id:'id',action_id:'id'};
 const prepared=await store.lookupPreparedCreate(pin);
 if(prepared.kind==='prepared'){
  // @ts-expect-error the frozen command must remain immutable
  prepared.pending.command.capture_id='other';
  await store.consumeCreateReceipt(prepared.pending,{});
 }
 const result:CreateDeliveryResult=await deliverSavedCreate({account_id:'id',access_token:'token'},pin,{store,signal:new AbortController().signal,isCurrent:()=>true});
 if(result.kind==='acknowledged'){const readback:'imported'|'unavailable'=result.readback;void readback;}
}
void checks;
