import {loadAdminEditContext,type PendingAdminEditContext,type AdminEditContextResult,type AdminEditContextError} from '../src/admin-edit-context';
import type {AdminEditContextResponse,AdminEditContextErrors,AdminEditContextData} from '../../contracts/admin-edit-context-generated/types.gen';
const pending:PendingAdminEditContext={account_id:'a',org_id:'o',capture_id:'c'};
// @ts-expect-error no original-owner selector
const owner:PendingAdminEditContext={...pending,owner_account_id:'a'};
// @ts-expect-error no organization query selector
const query:PendingAdminEditContext={...pending,query:{org_id:'o'}};
// @ts-expect-error no local permission selector
const permission:PendingAdminEditContext={...pending,permission:'kdg_capture.capture.edit.all'};
// @ts-expect-error no own-observation input
const observation:PendingAdminEditContext={...pending,edit_observation:{}};
// @ts-expect-error explicit current execution guard is mandatory
loadAdminEditContext({account_id:'a',access_token:'t'},pending,{});
// @ts-expect-error no implicit session lookup
loadAdminEditContext(null,pending,{signal:new AbortController().signal,isCurrent:()=>true});
const request:AdminEditContextData={url:'/api/v1/admin/captures/{capture_id}/edit-context',path:{capture_id:'c'}};
// @ts-expect-error owner contract forbids a query
request.query={};
// @ts-expect-error owner contract forbids a body
request.body={};
function loaded(result:AdminEditContextResult){if(result.kind==='loaded'){
 const provenance:Readonly<Pick<AdminEditContextResponse['capture'],'owner_account_id'|'owner_actor_id'|'created_by'|'updated_by'>>=result.context.capture;void provenance;
 // @ts-expect-error original capture is immutable
 result.context.capture.revision='3';
 // @ts-expect-error original questionnaire is deeply immutable
 result.context.capture.definition.questions.push(result.context.capture.definition.questions[0]);
 // @ts-expect-error nested answers are immutable
 result.context.capture.answers['q'].value=3;
 // @ts-expect-error editable fields do not confer mutation permission
 result.context.editable_fields[0]='answers';
 // @ts-expect-error no reader identity echo
 result.context.account_id;
 // @ts-expect-error no own-only offline authority
 result.context.read_observation;
 // @ts-expect-error no inferred write lease
 result.context.edit_observation;
}}
function errors(result:AdminEditContextError){if(result.status===403){const id:AdminEditContextErrors[403]['error_id']=result.error_id;void id;
 // @ts-expect-error raw backend error text is not exposed
 result.error;
}}
void owner;void query;void permission;void observation;void loaded;void errors;
