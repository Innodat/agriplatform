import {adminHistoryCaptures,type PendingAdminHistory,type AdminHistoryResult,type AdminHistoryError} from '../src/admin-history';
import type {AdminHistoryResponse,AdminHistoryData,AdminHistoryErrors} from '../../contracts/admin-generated/types.gen';
const pending:PendingAdminHistory={account_id:'a',org_id:'o',from_date:'2026-10-01',to_date:'2026-10-27'};
const cursorPage:PendingAdminHistory={...pending,limit:100,cursor:'cursor'};
// @ts-expect-error no owner selector
const owner:PendingAdminHistory={...pending,owner_account_id:'a'};
// @ts-expect-error no organization query selector
const query:PendingAdminHistory={...pending,query:{org_id:'o'}};
// @ts-expect-error no permission selector
const permission:PendingAdminHistory={...pending,permission:'kdg_capture.capture.read.all'};
// @ts-expect-error no individual capture selector
const capture:PendingAdminHistory={...pending,capture_id:'c'};
// @ts-expect-error explicit inclusive date range is mandatory
const dates:PendingAdminHistory={account_id:'a',org_id:'o'};
// @ts-expect-error explicit current execution lease is mandatory
adminHistoryCaptures({account_id:'a',access_token:'t'},pending,{});
// @ts-expect-error no implicit session lookup
adminHistoryCaptures(null,pending,{signal:new AbortController().signal,isCurrent:()=>true});
const request:AdminHistoryData={url:'/api/v1/admin/captures',query:{from_date:pending.from_date,to_date:pending.to_date,limit:30}};
function loaded(result:AdminHistoryResult){if(result.kind==='loaded'){
 const echo:Readonly<Pick<AdminHistoryResponse,'account_id'|'org_id'|'from_date'|'to_date'|'limit'|'next_cursor'>>=result.page;void echo;
 const provenance:Readonly<Pick<AdminHistoryResponse['items'][number],'owner_account_id'|'owner_actor_id'|'created_by'|'updated_by'>>=result.page.items[0];void provenance;
 // @ts-expect-error returned page is immutable
 result.page.next_cursor='changed';
 // @ts-expect-error items are immutable
 result.page.items.push(result.page.items[0]);
 // @ts-expect-error original questionnaire is deeply immutable
 result.page.items[0].definition.questions[0].label='changed';
 // @ts-expect-error nested answers are immutable
 result.page.items[0].answers['q'].value=3;
 // @ts-expect-error no offline authority
 result.page.observation;
 // @ts-expect-error no inferred write authority
 result.page.editable;
}}
function errors(result:AdminHistoryError){if(result.status===403){const id:AdminHistoryErrors[403]['error_id']=result.error_id;void id;
 // @ts-expect-error raw backend error text is not exposed
 result.error;
}}
void owner;void query;void permission;void capture;void dates;void cursorPage;void request;void loaded;void errors;
