import {openHistoryStore} from '../src/history-store';
import type {PendingEditContext} from '../src/edit-context';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>;
declare const pending:PendingEditContext;
store.importEditContext({},pending,{isCurrent:()=>true});
store.openEdit(pending.capture_id,{signal:new AbortController().signal});
store.saveEdit({},pending.capture_id,{observation_date:'2026-10-26',answers:{}});
// @ts-expect-error Scope pinning is required.
store.importEditContext({},{capture_id:pending.capture_id});
// @ts-expect-error An explicit caller-supplied action identity is required.
store.saveEdit({},{});
// @ts-expect-error Invalid execution fence return type.
store.openEdit(pending.capture_id,{isCurrent:()=>1});

store.importEditContext({},pending,{restoreDenied:true});
store.denyEdit({account_id:'a',org_id:'o'},{isCurrent:()=>true});
async function immutableResults(){
 const opened=await store.openEdit(pending.capture_id);
 if(opened.kind==='opened'){
  // @ts-expect-error reviewed original facts are immutable
  opened.reviewed.base.revision='2';
  // @ts-expect-error reviewed answers are immutable
  opened.reviewed.capture.answers.anything={value:1};
 }
 const retained=await store.readEditActions({limit:30});
 if(retained.kind==='available'){
  // @ts-expect-error returned action collection is immutable
  retained.actions.push({});
  // @ts-expect-error immutable retained proposal
  retained.actions[0].changes.observation_date='2026-10-01';
 }
}
void immutableResults;
