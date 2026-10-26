import type {AuditPage, AuditEvent, AuditEventsData, AuditEventsResponse} from '../../contracts/audit-generated';

declare const page: AuditPage;
declare const event: AuditEvent;
declare const response: AuditEventsResponse;
const typed: AuditPage=response;
const request: AuditEventsData={path:{capture_id:'capture'},query:{limit:30,cursor:'cursor'},url:'/api/v1/admin/captures/{capture_id}/events'};
const revision: string=event.revision;
const initiator: string|null=event.initiator_actor_id;
// @ts-expect-error audit is metadata only
const answers=page.answers;
// @ts-expect-error no snapshot definition
const definition=event.definition;
// @ts-expect-error no offline authorization observation
const observation=page.observation;
// @ts-expect-error no outcome identifiers
const outcome=event.outcome_id;
// @ts-expect-error no operation identifiers
const operation=event.operation_id;
// @ts-expect-error durable actor ID is not a resolved display name
const display=event.executor_name;
// @ts-expect-error no owner selector
const owner: AuditEventsData={path:{capture_id:'c'},query:{owner_account_id:'a'},url:'/api/v1/admin/captures/{capture_id}/events'};
// @ts-expect-error no organization selector
const organization: AuditEventsData={path:{capture_id:'c'},query:{org_id:'o'},url:'/api/v1/admin/captures/{capture_id}/events'};
// @ts-expect-error no observation date filter
const date: AuditEventsData={path:{capture_id:'c'},query:{from_date:'2026-10-01'},url:'/api/v1/admin/captures/{capture_id}/events'};
// @ts-expect-error GET body is prohibited
const body: AuditEventsData={path:{capture_id:'c'},body:{answers:{}},url:'/api/v1/admin/captures/{capture_id}/events'};
// @ts-expect-error capture path is mandatory
const path: AuditEventsData={url:'/api/v1/admin/captures/{capture_id}/events'};
// @ts-expect-error only real create/edit event types exist
const command: AuditEvent={...event,command_type:'capture.retry'};
void typed;void request;void revision;void initiator;void answers;void definition;void observation;void outcome;void operation;void display;void owner;void organization;void date;void body;void path;void command;
