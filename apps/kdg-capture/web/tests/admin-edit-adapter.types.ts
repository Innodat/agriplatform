import {editAdminCapture,type PendingAdminEdit,type AdminEditOptions,type AdminEditResult} from '../src/admin-edit';
import type {EditCommand,AdminEditCaptureData,AdminEditCaptureResponse} from '../../contracts/admin-edit-generated/types.gen';
import type {Session} from '../src/entry';
declare const session:Session;
declare const options:AdminEditOptions;
const command:EditCommand={operation_id:'op',command_version:1,expected_revision:'1',observation_date:'2026-10-26',answers:{question:{value:true,details:'text'}}};
const pending:PendingAdminEdit={account_id:session.account_id,org_id:'org',capture_id:'capture',command};
const wire:AdminEditCaptureData={url:'/api/v1/admin/captures/{capture_id}',path:{capture_id:pending.capture_id},body:pending.command};
const result:Promise<AdminEditResult>=editAdminCapture(session,pending,options);
// @ts-expect-error Caller-owned cancellation and generation fence are required.
editAdminCapture(session,pending,{});
// @ts-expect-error Capture identity is required.
const missingTarget:PendingAdminEdit={account_id:'account',org_id:'org',command};
// @ts-expect-error Unsupported versions cannot be constructed.
const wrongVersion:EditCommand={...command,command_version:2};
// @ts-expect-error Revision must remain an exact string.
const numericRevision:EditCommand={...command,expected_revision:1};
// @ts-expect-error Fixed generated edit route forbids selectors.
const selectors:AdminEditCaptureData={...wire,query:{account_id:'account'}};
// @ts-expect-error There is no original-owner impersonation input.
const owner:PendingAdminEdit={...pending,owner_account_id:'owner'};
// @ts-expect-error Current server authority cannot be selected locally.
const permission:PendingAdminEdit={...pending,permission:'kdg_capture.capture.edit.all'};
// @ts-expect-error Options have no automatic recovery or retry switch.
const recovery:AdminEditOptions={...options,retry:true};
async function consume(){
 const value=await result;
 if(value.kind==='committed'){
  const receipt:AdminEditCaptureResponse=value.receipt;
  // @ts-expect-error Receipt is immutable, including nested exact revision.
  value.receipt.result.revision='2';
  // @ts-expect-error Original operation receipt identity is immutable.
  value.receipt.operation_id='replacement';
  void receipt;
 }
 if(value.kind==='error'){
  // @ts-expect-error Raw upstream messages never cross this boundary.
  value.error;
  if(value.error_id==='kdg_capture.capture_revision_conflict'){
   const status:409=value.status;
   const current:string=value.current_revision;
   void [status,current];
  }else{
   // @ts-expect-error Other generated error variants have no conflict revision.
   value.current_revision;
  }
 }
 // @ts-expect-error No adapter result claims unresolved or rollback/absence.
 if(value.kind==='unresolved')void value;
}
void [wire,missingTarget,wrongVersion,numericRevision,selectors,owner,permission,recovery,consume];
