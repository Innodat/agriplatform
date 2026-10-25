import {recoverOperation, type PendingRecovery, type RecoveryOptions, type RecoveryResult} from '../src/recovery';
import type {Session} from '../src/entry';
declare const session: Session;
declare const options: RecoveryOptions;
const create: PendingRecovery={account_id:session.account_id,org_id:'org',operation_id:'op',command_type:'capture.create'};
const edit: PendingRecovery={...create,command_type:'capture.edit',capture_id:'target'};
const request: Promise<RecoveryResult>=recoverOperation(session,create,options);
// @ts-expect-error A caller-owned freshness/cancellation lease is required.
recoverOperation(session,create,{});
// @ts-expect-error Edit recovery requires the queued target for acknowledgement binding.
const missingTarget: PendingRecovery={...create,command_type:'capture.edit'};
// @ts-expect-error Runtime adapter never accepts unknown commands.
const unknownCommand: PendingRecovery={...create,command_type:'capture.delete'};
async function consume(){
  const result=await recoverOperation(session,edit,options);
  if(result.kind==='committed'){
    const revision: string=result.receipt.result.revision;
    // @ts-expect-error Caller cannot mutate a returned original receipt.
    result.receipt.result.revision='2';
    void revision;
  }
  if(result.kind==='unresolved'){
    // @ts-expect-error Successful absence has no committed capture result.
    result.outcome.result;
  }
}
void [request,missingTarget,unknownCommand,consume];
