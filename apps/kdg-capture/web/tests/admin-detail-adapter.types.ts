import {readAdminCapture,type PendingAdminDetail,type AdminDetailResult,type AdminDetailError} from '../src/admin-detail';
import type {AdminDetailResponse,AdminDetailErrors} from '../../contracts/admin-generated/types.gen';
const pending:PendingAdminDetail={account_id:'a',org_id:'o',capture_id:'c'};
// @ts-expect-error no owner selector
const owner:PendingAdminDetail={...pending,owner_account_id:'a'};
// @ts-expect-error no organization query selector
const query:PendingAdminDetail={...pending,query:{org_id:'o'}};
// @ts-expect-error no permission selector
const permission:PendingAdminDetail={...pending,permission:'kdg_capture.capture.read.all'};
// @ts-expect-error no history cursor
const cursor:PendingAdminDetail={...pending,cursor:'x'};
// @ts-expect-error explicit current execution lease is mandatory
readAdminCapture({account_id:'a',access_token:'t'},pending,{});
// @ts-expect-error no implicit session lookup
readAdminCapture(null,pending,{signal:new AbortController().signal,isCurrent:()=>true});
function loaded(result:AdminDetailResult){if(result.kind==='loaded'){
 const provenance:Readonly<Pick<AdminDetailResponse,'owner_account_id'|'owner_actor_id'|'created_by'|'updated_by'>>=result.snapshot;void provenance;
 // @ts-expect-error returned snapshot is immutable
 result.snapshot.revision='3';
 // @ts-expect-error original questionnaire is deeply immutable
 result.snapshot.definition.questions.push(result.snapshot.definition.questions[0]);
 // @ts-expect-error nested answers are immutable
 result.snapshot.answers['q'].value=3;
 // @ts-expect-error no reader identity echo in the owner DTO
 result.snapshot.account_id;
 // @ts-expect-error no offline authority
 result.snapshot.observation;
 // @ts-expect-error no inferred write authority
 result.snapshot.editable;
}}
function errors(result:AdminDetailError){if(result.status===403){const id:AdminDetailErrors[403]['error_id']=result.error_id;void id;
 // @ts-expect-error raw backend error text is not exposed
 result.error;
}}
void owner;void query;void permission;void cursor;void loaded;void errors;
