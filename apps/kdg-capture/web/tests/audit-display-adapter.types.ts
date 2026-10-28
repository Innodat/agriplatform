import {auditDetails,type AuditDetailsResult} from '../src/audit-display';
void auditDetails;
function check(r:AuditDetailsResult){if(r.kind==='loaded'){
// @ts-expect-error immutable labels
r.page.actor_display.status='loaded';
// @ts-expect-error immutable audit
r.page.audit.events.push(r.page.audit.events[0]);
if(r.page.actor_display.status==='loaded'){for(const label of r.page.actor_display.labels){if(label.status==='resolved'){const name:string=label.display_name;void name;}else{
// @ts-expect-error unavailable has no name
label.display_name;
}}}}}void check;
// @ts-expect-error an explicit signal and current-generation lease are required
auditDetails({account_id:'a',access_token:'t'},{account_id:'a',org_id:'o',capture_id:'c'},{});
// @ts-expect-error no implicit session lookup
auditDetails(null,{account_id:'a',org_id:'o',capture_id:'c'},{signal:new AbortController().signal,isCurrent:()=>true});
