import {auditEvents,type PendingAudit,type AuditResult,type AuditError} from '../src/audit';
import type {AuditPage,AuditEventsErrors} from '../../contracts/audit-generated/types.gen';
const pending:PendingAudit={account_id:'a',org_id:'o',capture_id:'c',limit:2};
// @ts-expect-error no owner selector
const owner:PendingAudit={...pending,owner_account_id:'a'};
// @ts-expect-error no organization query selector
const query:PendingAudit={...pending,query:{org_id:'o'}};
// @ts-expect-error no own authority selector
const permission:PendingAudit={...pending,permission:'kdg_capture.capture.read.own'};
// @ts-expect-error explicit current execution lease is mandatory
auditEvents({account_id:'a',access_token:'t'},pending,{});
// @ts-expect-error no implicit Auth/session lookup
auditEvents(null,pending,{signal:new AbortController().signal,isCurrent:()=>true});
function loaded(result:AuditResult){if(result.kind==='loaded'){
 const original:Readonly<AuditPage['events'][number]>=result.page.events[0];void original;
 // @ts-expect-error returned page is immutable
 result.page.current_revision='3';
 // @ts-expect-error nested event array is immutable
 result.page.events.push(result.page.events[0]);
 // @ts-expect-error nested events are immutable
 result.page.events[0].executor_actor_id='x';
 // @ts-expect-error metadata does not supply capture content
 result.page.answers;
 // @ts-expect-error actor label resolution is absent
 result.page.events[0].executor_name;
 // @ts-expect-error no offline observation or authority
 result.page.observation;
}}
function errors(result:AuditError){if(result.status===403){const id:AuditEventsErrors[403]['error_id']=result.error_id;void id;
 // @ts-expect-error raw error text is never published
 result.error;
}}
void owner;void query;void permission;void loaded;void errors;
