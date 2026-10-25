import type {EditCaptureData, EditCaptureResponse, EditCaptureErrors} from '../contracts/edit-generated/index';
const request: EditCaptureData = {
  url: '/api/v1/captures/{capture_id}', path: {capture_id:'11111111-1111-4111-8111-111111111111'},
  body: {operation_id:'22222222-2222-4222-8222-222222222222',command_version:1,
    expected_revision:'1',observation_date:'2026-10-25',answers:{}},
};
const receipt: EditCaptureResponse = {operation_id:request.body.operation_id,command_type:'capture.edit',
  command_version:1,status:'committed',result:{capture_id:request.path.capture_id,revision:'2'}};
const conflict: EditCaptureErrors[409] = {error:'Safe message',error_id:'kdg_capture.capture_revision_conflict',current_revision:'4'};
function currentRevision(error: EditCaptureErrors[409]): string | undefined {
  if (error.error_id==='kdg_capture.capture_revision_conflict') return error.current_revision;
  // @ts-expect-error Only a revision conflict carries current revision.
  return error.current_revision;
}
// @ts-expect-error Input needs its original expected revision.
const missingRevision: EditCaptureData['body'] = {operation_id:request.body.operation_id,command_version:1,observation_date:'2026-10-25',answers:{}};
// @ts-expect-error Revisions are decimal strings, never JS numbers.
const numericRevision: EditCaptureData['body'] = {...request.body,expected_revision:1};
// @ts-expect-error Capture identity belongs in path, not editable command.
const editableTarget: EditCaptureData['body'] = {...request.body,capture_id:request.path.capture_id};
// @ts-expect-error Caller-selected organization is not a query parameter.
const selector: EditCaptureData = {...request,query:{org_id:request.path.capture_id}};
// @ts-expect-error This endpoint only returns edit receipts.
const createReceipt: EditCaptureResponse = {...receipt,command_type:'capture.create'};
// @ts-expect-error Revision conflict metadata is required.
const missingMetadata: EditCaptureErrors[409] = {error:'Safe',error_id:'kdg_capture.capture_revision_conflict'};
// @ts-expect-error Revision metadata stays a string.
const numericMetadata: EditCaptureErrors[409] = {...conflict,current_revision:4};
// @ts-expect-error Other409 errors cannot carry revision metadata.
const falseConflict: EditCaptureErrors[409] = {error:'Safe',error_id:'identity.actor_setup_required',current_revision:'4'};
// @ts-expect-error Error identifiers preserve their HTTP status family.
const wrongStatus: EditCaptureErrors[403] = {error:'Safe',error_id:'authorization_unavailable'};
// @ts-expect-error Failed authorization is not a committed response.
const falseSuccess: EditCaptureResponse = {error:'Safe',error_id:'access_denied'};
const trueDetails: EditCaptureData['body']['answers'] = {'11111111-1111-4111-8111-111111111111':{value:true,details:'more'}};
// @ts-expect-error False answers cannot include details.
const falseDetails: EditCaptureData['body']['answers'] = {'11111111-1111-4111-8111-111111111111':{value:false,details:'hidden'}};
void [trueDetails,falseDetails,request,receipt,conflict,currentRevision,missingRevision,numericRevision,editableTarget,selector,createReceipt,missingMetadata,numericMetadata,falseConflict,wrongStatus,falseSuccess];
