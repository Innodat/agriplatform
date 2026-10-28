import assert from 'node:assert/strict';
import {test} from 'node:test';
import {auditDetails} from '../../../../compiled/web/src/audit-display.js';
import {auditPresentation} from '../../../../compiled/web/src/audit-presentation.js';
const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',org='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',capture='cccccccc-cccc-4ccc-8ccc-cccccccccccc',owner='dddddddd-dddd-4ddd-8ddd-dddddddddddd',author='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',modifier='ffffffff-ffff-4fff-8fff-ffffffffffff',initiator='11111111-1111-4111-8111-111111111111',oldEditor='22222222-2222-4222-8222-222222222222';
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const cursor=(revision,limit=2)=>Buffer.from(JSON.stringify(Object.fromEntries(Object.entries({v:1,account_id:account,org_id:org,capture_id:capture,permission:'kdg_capture.capture.read.all',limit,last_revision:revision}).sort(([a],[b])=>a<b?-1:a>b?1:0)))).toString('base64url');
const event=(revision,executor_actor_id=modifier,initiator_actor_id=null)=>({revision,command_type:revision==='1'?'capture.create':'capture.edit',executor_actor_id,initiator_actor_id,recorded_at:'2026-10-26T11:00:00.000001Z'});
function aggregate(change={}){
 const audit={account_id:account,org_id:org,capture_id:capture,owner_account_id:owner,owner_actor_id:author,created_by:author,created_at:'2026-10-26T10:00:00.000009Z',updated_by:modifier,updated_at:'2026-10-26T09:00:00.000001Z',current_revision:'3',limit:2,events:[event('3',modifier,initiator),event('2',oldEditor)],next_cursor:cursor('2'),...change};
 const ids=[...new Set([audit.owner_actor_id,audit.created_by,audit.updated_by,...audit.events.flatMap(e=>[e.executor_actor_id,...(e.initiator_actor_id===null?[]:[e.initiator_actor_id])])])].sort();
 const names={[author]:'Original capturer',[modifier]:'Latest modifier',[initiator]:'Actual initiator',[oldEditor]:'Earlier editor'};
 return {audit,actor_display:{status:'loaded',labels:ids.map(actor_id=>({actor_id,status:'resolved',display_name:names[actor_id]??'Service actor'}))}};
}
const read=(value=aggregate(),change={},options={})=>auditDetails({account_id:account,access_token:'synthetic'},{account_id:account,org_id:org,capture_id:capture,limit:value.audit.limit,...change},{signal:new AbortController().signal,isCurrent:()=>true,request:async()=>new Response(JSON.stringify(value),{headers}),...options});
const loaded=async(value=aggregate(),change={})=>{const result=await read(value,change);assert.equal(result.kind,'loaded','fixture must cross the real adapter');return result;};
const project=async(value=aggregate(),change={})=>auditPresentation(await loaded(value,change));
function deeplyFrozen(value){if(value&&typeof value==='object'){assert.ok(Object.isFrozen(value));for(const child of Object.values(value))deeplyFrozen(child);}}

test('authorized cross-owner aggregate projects actual audit provenance',async()=>{
 const input=await loaded(),before=JSON.stringify(input),result=auditPresentation(input);
 assert.equal(result.kind,'loaded');const m=result.model;
 assert.deepEqual(m.scope,{account_id:account,org_id:org,capture_id:capture,owner_account_id:owner});
 assert.equal(m.original_capturer.actor_id,author);assert.equal(m.original_capturer.display_name,'Original capturer');
 assert.equal(m.creation.actor.actor_id,author);assert.equal(m.creation.recorded_at,input.page.audit.created_at);
 assert.equal(m.latest_modification.actor.actor_id,modifier);assert.equal(m.latest_modification.recorded_at,input.page.audit.updated_at);
 assert.equal(m.events[0].executor.actor_id,modifier);assert.equal(m.events[0].executor.display_name,'Latest modifier');
 assert.equal(m.events[0].initiator.actor_id,initiator);assert.equal(m.events[0].initiator.display_name,'Actual initiator');
 assert.equal(m.events[1].executor.actor_id,oldEditor);assert.equal(m.events[1].initiator,null);
 assert.equal(m.current_revision,'3');assert.equal(m.limit,2);assert.equal(m.next_cursor,input.page.audit.next_cursor);
 assert.deepEqual(m.names,{status:'loaded',retry_available:false});deeplyFrozen(result);assert.equal(JSON.stringify(input),before);
});

test('unmapped actors are not temporary outages or guessed System names',async()=>{
 const value=aggregate();value.actor_display.labels=value.actor_display.labels.map(l=>l.actor_id===author?{actor_id:author,status:'unavailable'}:l);
 const result=await project(value);assert.equal(result.kind,'loaded');
 assert.deepEqual(result.model.original_capturer,{actor_id:author,status:'unavailable',message_key:'audit.name_unavailable'});
 assert.deepEqual(result.model.creation.actor,result.model.original_capturer);
 assert.equal(result.model.latest_modification.actor.status,'resolved');assert.equal(result.model.names.retry_available,false);
 assert.ok(!JSON.stringify(result).includes('System'));assert.ok(!Object.hasOwn(result.model.original_capturer,'display_name'));
});

test('batch outage preserves authorized metadata and explicit retry semantics',async()=>{
 const value=aggregate();value.actor_display={status:'temporarily_unavailable'};
 const result=await project(value);assert.equal(result.kind,'loaded');const m=result.model;
 assert.deepEqual(m.names,{status:'temporarily_unavailable',retry_available:true});
 for(const label of [m.original_capturer,m.creation.actor,m.latest_modification.actor,...m.events.flatMap(e=>[e.executor,...(e.initiator?[e.initiator]:[])])]){
  assert.equal(label.status,'temporarily_unavailable');assert.equal(label.message_key,'audit.names_temporarily_unavailable');assert.ok(!Object.hasOwn(label,'display_name'));
 }
 assert.equal(m.events[1].initiator,null);assert.equal(m.creation.recorded_at,value.audit.created_at);assert.equal(m.events.length,2);
});

test('older and empty continuation use current header rather than page editors',async()=>{
 for(const events of [[event('2',oldEditor)],[]]){
  const value=aggregate({events,next_cursor:null});const result=await project(value,{cursor:cursor('3')});
  assert.equal(result.kind,'loaded');const m=result.model;
  assert.equal(m.latest_modification.actor.actor_id,modifier);assert.equal(m.original_capturer.actor_id,author);assert.equal(m.creation.actor.actor_id,author);
  assert.equal(m.events.length,events.length);if(events.length)assert.equal(m.events[0].executor.actor_id,oldEditor);
  assert.equal(m.next_cursor,null);assert.equal(m.current_revision,'3');
 }
});

test('exact retained names can change on a fresh read without changing attribution',async()=>{
 const first=await project();const value=aggregate();value.actor_display.labels.find(l=>l.actor_id===author).display_name='  Renamed 😀 service  ';
 const next=await project(value);assert.equal(next.model.original_capturer.display_name,'  Renamed 😀 service  ');
 assert.equal(first.model.original_capturer.display_name,'Original capturer');assert.equal(first.model.original_capturer.actor_id,next.model.original_capturer.actor_id);
 assert.equal(first.model.creation.recorded_at,next.model.creation.recorded_at);
});

test('maximum page preserves bigint numeric order, microseconds and nullable initiators',async()=>{
 const maximum='9223372036854775807';
 const events=Array.from({length:100},(_,i)=>event((BigInt(maximum)-BigInt(i)).toString(),i===0?modifier:oldEditor,i%2===0?initiator:null));
 const value=aggregate({current_revision:maximum,events,limit:100,next_cursor:cursor(events.at(-1).revision,100)});
 const input=await loaded(value),result=auditPresentation(input);assert.equal(result.kind,'loaded');
 assert.equal(result.model.current_revision,maximum);assert.equal(result.model.next_cursor,value.audit.next_cursor);
 assert.deepEqual(result.model.events.map(e=>e.revision),events.map(e=>e.revision));assert.deepEqual(result.model.events.map(e=>e.recorded_at),events.map(e=>e.recorded_at));
 assert.equal(result.model.events.length,100);deeplyFrozen(result);
});

test('a genuine create event is preserved without adding header-based events',async()=>{
 const value=aggregate({events:[event('3'),event('1',author,initiator)],next_cursor:null});const result=await project(value);
 assert.deepEqual(result.model.events.map(e=>[e.revision,e.command_type]),[['3','capture.edit'],['1','capture.create']]);
 assert.equal(result.model.events[1].executor.actor_id,author);assert.equal(result.model.events[1].initiator.actor_id,initiator);
 assert.ok(!Object.hasOwn(result.model,'answers'));assert.ok(!Object.hasOwn(result.model.events[0],'answers'));
});

test('safe errors and local outcomes remain nonloaded, without an empty audit',()=>{
 for(const result of [{kind:'error',status:403,error_id:'access_denied'},{kind:'error',status:503,error_id:'authorization_unavailable'},...['invalid_request','authentication_required','invalid_response','verification_unavailable','cancelled','superseded'].map(kind=>({kind}))]){
  Object.freeze(result);assert.equal(auditPresentation(result),result);assert.ok(!Object.hasOwn(auditPresentation(result),'model'));
 }
});

test('denied, malformed and superseded actual adapter reads cannot project data',async()=>{
 let generation=1;const before=generation;let finish;
 const promise=read(aggregate(),{},{isCurrent:()=>generation===before,request:()=>new Promise(r=>{finish=r;})});
 generation++;finish(new Response(JSON.stringify(aggregate()),{headers}));
 const superseded=await promise;assert.equal(superseded.kind,'superseded');assert.equal(auditPresentation(superseded).kind,'superseded');
 const denied=await read(aggregate(),{},{request:async()=>new Response(JSON.stringify({error:'PRIVATE',error_id:'access_denied'}),{status:403,headers})});
 assert.deepEqual(auditPresentation(denied),{kind:'error',status:403,error_id:'access_denied'});
 const invalid=aggregate();invalid.actor_display.labels=[];assert.equal(auditPresentation(await read(invalid)).kind,'invalid_response');
});
