import {openHistoryStore,phoneHistoryDates} from '../src/history-store';
async function example(){
 const store=await openHistoryStore({account_id:'a',org_id:'o'});
 const value=await store.read();if(value.kind==='available'){
  // @ts-expect-error committed observations cannot be locally renewed
  value.observation.expires_at='2099-01-01T00:00:00Z';
  // @ts-expect-error read collection is immutable
  value.records.push({});
 }
 // @ts-expect-error explicit account/org namespace required
 await openHistoryStore({account_id:'a'});
 const dates=phoneHistoryDates();
 // @ts-expect-error phone date bounds are pinned
 dates.from_date='2026-01-01';
 store.close();
}
void example;
