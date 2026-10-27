import {recoverAdminEdit,type PendingAdminRecovery,type AdminRecoveryOptions,type AdminRecoveryResult} from '../src/admin-recovery';
import type {AdminRecoverEditData,AdminRecoverEditResponse,CaptureReceipt,Unresolved} from '../../contracts/admin-edit-generated/types.gen';
import type {Session} from '../src/entry';
declare const session:Session;
declare const options:AdminRecoveryOptions;
const pending:PendingAdminRecovery={account_id:session.account_id,org_id:'org',operation_id:'operation',capture_id:'capture',command_type:'capture.edit'};
const wire:AdminRecoverEditData={url:'/api/v1/admin/operations/{operation_id}',path:{operation_id:pending.operation_id},query:{command_type:pending.command_type}};
const result:Promise<AdminRecoveryResult>=recoverAdminEdit(session,pending,options);
// @ts-expect-error Caller-owned cancellation and generation fence are required.
recoverAdminEdit(session,pending,{});
// @ts-expect-error The original capture target is required.
const missingTarget:PendingAdminRecovery={account_id:'account',org_id:'org',operation_id:'operation',command_type:'capture.edit'};
// @ts-expect-error Recovery supports only the original edit command.
const wrongCommand:PendingAdminRecovery={...pending,command_type:'capture.create'};
// @ts-expect-error The query has no owner selector.
const selectors:AdminRecoverEditData={...wire,query:{command_type:'capture.edit',owner_account_id:'owner'}};
// @ts-expect-error Recovery never sends a command body.
const body:AdminRecoverEditData={...wire,body:{operation_id:'replacement'}};
// @ts-expect-error No original-owner impersonation input.
const owner:PendingAdminRecovery={...pending,owner_account_id:'owner'};
// @ts-expect-error Current server authority cannot be selected locally.
const permission:PendingAdminRecovery={...pending,permission:'kdg_capture.capture.read.all'};
// @ts-expect-error No automatic recovery or retry switch.
const retry:AdminRecoveryOptions={...options,retry:true};
async function consume(){
 const value=await result;
 if(value.kind==='committed'){
  const receipt:CaptureReceipt=value.receipt,wire:AdminRecoverEditResponse=value.receipt;
  // @ts-expect-error Nested original revision is immutable.
  value.receipt.result.revision='2';
  // @ts-expect-error Original operation identity is immutable.
  value.receipt.operation_id='replacement';
  // @ts-expect-error A receipt never supplies original authority provenance.
  value.receipt.surface;
  void [receipt,wire];
 }
 if(value.kind==='unresolved'){
  const outcome:Unresolved=value.outcome,wire:AdminRecoverEditResponse=value.outcome;
  // @ts-expect-error Unresolved is immutable and has no absence guarantee.
  value.outcome.operation_id='replacement';
  // @ts-expect-error No capture snapshot or proposal in unresolved.
  value.outcome.capture;
  void [outcome,wire];
 }
 if(value.kind==='error'){
  // @ts-expect-error Raw upstream messages never cross this boundary.
  value.error;
  // @ts-expect-error Recovery errors do not expose conflict revisions.
  value.current_revision;
  if(value.error_id==='identity.actor_setup_required'){const status:409=value.status;void status;}
 }
 // @ts-expect-error Recovery never publishes Synced.
 if(value.kind==='synced')void value;
}
void [wire,missingTarget,wrongCommand,selectors,body,owner,permission,retry,consume];
