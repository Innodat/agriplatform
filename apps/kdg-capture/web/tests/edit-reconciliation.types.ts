import {openHistoryStore,type PreparedEdit} from '../src/history-store';
import type {PendingEdit} from '../src/edit';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>;
declare const pending:PreparedEdit;
const compatible:PendingEdit=pending;
store.consumeEditReceipt(compatible,{kind:'committed'});
store.consumeEditConflict(pending,{kind:'error'});
store.prepareEdit('operation',{signal:new AbortController().signal,isCurrent:()=>true});
// @ts-expect-error preparation requires the original action identity
store.prepareEdit();
// @ts-expect-error consumption requires all scope and command pins
store.consumeEditReceipt({capture_id:'c'},{});
// @ts-expect-error execution predicates must return boolean
store.consumeEditConflict(pending,{}, {isCurrent:()=>1});
async function immutableDelivery(){
 const outcome=await store.prepareEdit('operation');
 if(outcome.kind==='prepared'){
  // @ts-expect-error complete frozen command cannot be retargeted
  outcome.pending.command.expected_revision='2';
  // @ts-expect-error frozen command answers cannot be replaced
  outcome.pending.command.answers={};
 }
 const retained=await store.readEditActions();
 if(retained.kind==='available'&&retained.actions[0].delivery){
  // @ts-expect-error retained delivery identity cannot be replaced
  retained.actions[0].delivery.pending.capture_id='other';
 }
}
void immutableDelivery;
