import {editCapture,type PendingEdit,type EditOptions,type EditResult} from '../src/edit';
import type {EditCommand,EditCaptureData,EditCaptureResponse} from '../../contracts/edit-generated/types.gen';
import type {Session} from '../src/entry';
declare const session:Session;
declare const options:EditOptions;
const command:EditCommand={operation_id:'op',command_version:1,expected_revision:'1',observation_date:'2026-10-26',answers:{question:{value:true,details:'text'}}};
const pending:PendingEdit={account_id:session.account_id,org_id:'org',capture_id:'capture',command};
const wire:EditCaptureData={url:'/api/v1/captures/{capture_id}',path:{capture_id:pending.capture_id},body:pending.command};
const result:Promise<EditResult>=editCapture(session,pending,options);
// @ts-expect-error Caller-owned cancellation and generation fence are required.
editCapture(session,pending,{});
// @ts-expect-error Capture identity is required.
const missingTarget:PendingEdit={account_id:'account',org_id:'org',command};
// @ts-expect-error Unsupported versions cannot be constructed.
const wrongVersion:EditCommand={...command,command_version:2};
// @ts-expect-error Revision must remain an exact string.
const numericRevision:EditCommand={...command,expected_revision:1};
// @ts-expect-error Fixed generated edit route forbids selectors.
const selectors:EditCaptureData={...wire,query:{account_id:'account'}};
async function consume(){
 const value=await result;
 if(value.kind==='committed'){
  const receipt:EditCaptureResponse=value.receipt;
  // @ts-expect-error Receipt is immutable, including nested exact revision.
  value.receipt.result.revision='2';
  void receipt;
 }
 if(value.kind==='error'){
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
void [wire,missingTarget,wrongVersion,numericRevision,selectors,consume];
