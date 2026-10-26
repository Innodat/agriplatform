import assert from 'node:assert/strict';
import {test} from 'node:test';
import {loadProvision} from '../../../../compiled/web/src/provision.js';
import {A,O,provision,response,pending} from './provision-fixture.mjs';
const session={account_id:A,access_token:'synthetic-token'};
const options=()=>({signal:new AbortController().signal,isCurrent:()=>true});
test('acceptance: protected setup retains exact independently verified scope and eligible definition',async()=>{
 const calls=[];const result=await loadProvision(session,pending(),{...options(),request:async(...args)=>{calls.push(args);return response();}});
 assert.equal(result.kind,'loaded');assert.deepEqual(result.provision,provision());assert.equal(calls.length,1);assert.equal(calls[0][0],'/api/v1/provision');assert.equal(calls[0][1].cache,'no-store');assert.equal(calls[0][1].headers.Authorization,'Bearer synthetic-token');assert.ok(Object.isFrozen(result.provision.children[0]));
});
for(const mode of ['all','both','edit_denied','not_permitted','no_eligible_children','no_published_questionnaire'])test('setup state '+mode+' keeps independent positive evidence',async()=>{
 const value=provision();
 if(mode==='all'||mode==='both'){value.create_all_observation={...value.create_assigned_observation,permission:'kdg_capture.capture.create.all'};if(mode==='all')value.create_assigned_observation=null;value.children[0].create_permission='kdg_capture.capture.create.all';value.children[0].assignment=null;}
 if(mode==='edit_denied')value.edit_observation=null;
 if(mode==='not_permitted'){value.create_assigned_observation=null;value.children=[];value.create_state=mode;}
 if(mode==='no_eligible_children'){value.children=[];value.create_state=mode;}
 if(mode==='no_published_questionnaire'){value.questionnaire=null;value.create_state=mode;}
 const result=await loadProvision(session,pending(),{...options(),request:async()=>response(value)});assert.equal(result.kind,'loaded');assert.deepEqual(result.provision,value);
});
const corruptions={
 account:v=>v.account_id=O,org:v=>v.org_id=A,actor:v=>v.actor_id='invalid',membership:v=>v.membership_id='0',schema:v=>v.schema_version=2,
 extra:v=>v.access_token='SENSITIVE',missing:v=>delete v.edit_observation,read_missing:v=>v.read_observation=null,
 read_permission:v=>v.read_observation.permission='kdg_capture.capture.edit.own',all_inference:v=>{v.create_all_observation=structuredClone(v.create_assigned_observation);},
 edit_identity:v=>v.edit_observation.actor_id=A,create_membership:v=>v.create_assigned_observation.membership_id='8',create_scope:v=>v.create_assigned_observation.resource_scope.account_id=O,
 capability_expiry:v=>v.edit_observation.expires_at='2026-11-03T10:00:00Z',capability_case:v=>v.read_observation.checked_at='2026-10-26t10:00:00Z',
 child_scope:v=>v.children[0].create_permission='kdg_capture.capture.create.all',child_extra:v=>v.children[0].account_id=A,child_id:v=>v.children[0].child_id='invalid',
 child_label:v=>v.children[0].child_label=' ',child_label_bound:v=>v.children[0].child_label='👩'.repeat(201),child_revision:v=>v.children[0].child_revision='01',
 eligibility:v=>v.children[0].child_eligibility_ref='invalid',assignment:v=>v.children[0].assignment=null,assignment_revision:v=>v.children[0].assignment.assignment_revision='0',
 child_expiry:v=>v.children[0].expires_at='2026-11-02T10:00:02Z',child_time:v=>v.children[0].checked_at='2026-02-30T10:00:01Z',
 duplicate_child:v=>v.children.push(structuredClone(v.children[0])),duplicate_ref:v=>v.children.push({...structuredClone(v.children[0]),child_id:O}),too_many:v=>v.children=Array.from({length:1001},()=>v.children[0]),
 state:v=>v.create_state='not_permitted',empty_ready:v=>v.children=[],no_version_ready:v=>v.questionnaire=null,
 version:v=>v.questionnaire.questionnaire_version='0',questionnaire_extra:v=>v.questionnaire.answers={},definition_unknown:v=>v.questionnaire.definition.schema_version=2,
 duplicate_question:v=>v.questionnaire.definition.questions.push(structuredClone(v.questionnaire.definition.questions[0])),definition_bound:v=>v.questionnaire.definition.questions=Array.from({length:51},()=>v.questionnaire.definition.questions[0]),
 question_label:v=>v.questionnaire.definition.questions[0].label=' ',question_scale:v=>v.questionnaire.definition.questions[0].minimum=0,
 false_assignment_all:v=>{v.create_all_observation={...v.create_assigned_observation,permission:'kdg_capture.capture.create.all'};v.children[0].create_permission='kdg_capture.capture.create.all';},
 no_create_children:v=>{v.create_assigned_observation=null;v.create_state='not_permitted';},
};
for(const [name,mutate] of Object.entries(corruptions))test('refuse malformed or inconsistent setup '+name,async()=>{
 const value=provision();mutate(value);assert.equal((await loadProvision(session,pending(),{...options(),request:async()=>response(value)})).kind,'invalid_response');
});
for(const [status,id] of [[401,'authentication_required'],[403,'access_denied'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'invalid_write_context'],[500,'internal_error'],[503,'authorization_unavailable'],[503,'provision_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe setup error '+status+' '+id,async()=>{
 assert.deepEqual(await loadProvision(session,pending(),{...options(),request:async()=>response({error:'SENSITIVE',error_id:id},status)}),{kind:'error',status,error_id:id});
});
for(const [name,request] of Object.entries({
 outage:async()=>{throw Error('SENSITIVE');},unknown:async()=>response({error:'SENSITIVE',error_id:'unknown'},503),cache:async()=>new Response(JSON.stringify(provision()),{headers:{'content-type':'application/json'}}),
 malformed:async()=>new Response('x',{headers:{'content-type':'application/json','cache-control':'private,no-store'}}),
 duplicate:async()=>new Response(JSON.stringify(provision()).replace('"schema_version":1','"schema_version":1,"schema_version":1'),{headers:{'content-type':'application/json','cache-control':'private,no-store'}}),
 unicode:async()=>response({...provision(),children:[{...provision().children[0],child_label:'bad\u0000text'}]}),
 invalid_utf8:async()=>new Response(Uint8Array.from([255]),{headers:{'content-type':'application/json','cache-control':'private,no-store'}}),
 oversized:async()=>new Response(' '.repeat(1048577),{headers:{'content-type':'application/json','cache-control':'private,no-store'}}),
}))test('transport refuses '+name,async()=>{const result=await loadProvision(session,pending(),{...options(),request});assert.equal(result.kind,name==='outage'?'verification_unavailable':'invalid_response');assert.ok(!JSON.stringify(result).includes('SENSITIVE'));});
for(const invalid of [null,{},undefined,{account_id:O,org_id:O},{account_id:A,org_id:O,extra:true}])test('invalid caller never dispatches '+JSON.stringify(invalid),async()=>{
 let calls=0;const result=await loadProvision(session,invalid,{...options(),request:async()=>{calls++;return response();}});assert.equal(result.kind,'invalid_request');assert.equal(calls,0);
});
for(const phase of ['headers','body'])test('one deadline bounds ignored '+phase,async()=>{
 const result=await loadProvision(session,pending(),{...options(),timeoutMs:20,request:async()=>phase==='headers'?new Promise(()=>{}):new Response(new ReadableStream({start(){}}),{headers:{'content-type':'application/json','cache-control':'private,no-store'}})});assert.equal(result.kind,'verification_unavailable');
});
for(const reason of ['abort','stale'])test('late '+reason+' cannot publish setup',async()=>{
 const controller=new AbortController();let fresh=true;
 const result=await loadProvision(session,pending(),{signal:controller.signal,isCurrent:()=>fresh,request:async()=>{if(reason==='abort')controller.abort();else fresh=false;return response();}});assert.equal(result.kind,reason==='abort'?'cancelled':'superseded');
});
test('caller primitives pinned before transport await',async()=>{
 const caller=pending(),auth={...session};let release;const held=new Promise(r=>release=r);
 const result=loadProvision(auth,caller,{...options(),request:async(_url,init)=>{await held;assert.equal(init.headers.Authorization,'Bearer synthetic-token');return response();}});caller.account_id=O;auth.access_token='changed';release();assert.equal((await result).kind,'loaded');
});
