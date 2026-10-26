import {detail,A,O,C,Q} from './read-fixture.mjs';
export {A,O,C,Q};
export const actor='77777777-7777-4777-8777-777777777777';
export const observation=permission=>({account_id:A,actor_id:actor,membership_id:'7',authorization_scope:{kind:'organization',org_id:O},resource_scope:{kind:'own_account',account_id:A},permission,decision_id:Q,checked_at:'2026-10-26T10:00:00Z',expires_at:'2026-11-02T10:00:00Z'});
export const provision=()=>({schema_version:1,org_id:O,account_id:A,actor_id:actor,membership_id:'7',read_observation:observation('kdg_capture.capture.read.own'),edit_observation:observation('kdg_capture.capture.edit.own'),create_all_observation:null,create_assigned_observation:observation('kdg_capture.capture.create.assigned'),create_state:'ready',children:[{child_id:C,child_label:'Child',child_revision:'1',child_eligibility_ref:'a'.repeat(43),create_permission:'kdg_capture.capture.create.assigned',assignment:{assignment_id:Q,assignment_revision:'1'},checked_at:'2026-10-26T10:00:01Z',expires_at:'2026-11-02T10:00:01Z'}],questionnaire:{questionnaire_id:Q,questionnaire_version_id:Q,questionnaire_version:'1',definition:detail().definition}});
export const response=(value=provision(),status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
export const pending=()=>({account_id:A,org_id:O});
