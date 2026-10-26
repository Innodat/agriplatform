import type {EditCommand,CaptureReceipt,AdminEditCaptureData,AdminEditCaptureResponse,AdminEditCaptureError,AdminRecoverEditData,AdminRecoverEditResponse} from '../../contracts/admin-edit-generated';
import type {EditCommand as OwnCommand,CaptureReceipt as OwnReceipt} from '../../contracts/edit-generated';
type Equal<A,B>=(<T>()=>T extends A?1:2) extends (<T>()=>T extends B?1:2)?true:false;
type Assert<T extends true>=T;
type SameCommand=Assert<Equal<EditCommand,OwnCommand>>;
type SameReceipt=Assert<Equal<CaptureReceipt,OwnReceipt>>;
type ExactCommand=Assert<Equal<keyof EditCommand,'operation_id'|'command_version'|'expected_revision'|'observation_date'|'answers'>>;
type ExactReceipt=Assert<Equal<keyof CaptureReceipt,'operation_id'|'command_type'|'command_version'|'status'|'result'>>;
declare const command:EditCommand;
const input:AdminEditCaptureData={body:command,path:{capture_id:'c'},url:'/api/v1/admin/captures/{capture_id}'};
declare const saved:AdminEditCaptureResponse;
const receipt:CaptureReceipt=saved;
// @ts-expect-error no owner impersonation
const owner:EditCommand={...command,owner_account_id:'a'};
// @ts-expect-error no tenant selector
const org:AdminEditCaptureData={...input,query:{org_id:'o'}};
// @ts-expect-error no reusable edit authority
const authority=saved.edit_observation;
// @ts-expect-error no corrected proposal in a receipt
const proposal=saved.answers;
// @ts-expect-error no captured owner metadata
const provenance=saved.result.owner_account_id;
declare const error:AdminEditCaptureError;
if(error.error_id==='kdg_capture.capture_revision_conflict'){
 const revision:string=error.current_revision;
 // @ts-expect-error conflict discloses no record
 const answers=error.answers;
 void revision;void answers;
}else{
 // @ts-expect-error revision exists only on conflict
 const revision=error.current_revision;
 void revision;
}
const lookup:AdminRecoverEditData={path:{operation_id:'o'},query:{command_type:'capture.edit'},url:'/api/v1/admin/operations/{operation_id}'};
// @ts-expect-error discriminator is exactly capture.edit
const other:AdminRecoverEditData={...lookup,query:{command_type:'capture.create'}};
// @ts-expect-error discriminator required
const missing:AdminRecoverEditData={path:{operation_id:'o'},url:'/api/v1/admin/operations/{operation_id}'};
// @ts-expect-error no body, target or write proposal
const recoveryBody:AdminRecoverEditData={...lookup,body:command};
declare const recovery:AdminRecoverEditResponse;
if(recovery.status==='committed'){
 const original:CaptureReceipt=recovery;
 void original;
}else{
 const status:'unresolved'=recovery.status;
 // @ts-expect-error absence has no record result
 const result=recovery.result;
 void status;void result;
}
void receipt;void owner;void org;void authority;void proposal;void provenance;void other;void missing;void recoveryBody;
