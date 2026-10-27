import assert from 'node:assert/strict';
import {test} from 'node:test';
import {auditEvents} from '../../../../compiled/web/src/audit.js';
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',O='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',C='cccccccc-cccc-4ccc-8ccc-cccccccccccc',OWNER='dddddddd-dddd-4ddd-8ddd-dddddddddddd',ACTOR='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',EXEC='ffffffff-ffff-4fff-8fff-ffffffffffff';
const pending=(change={})=>({account_id:A,org_id:O,capture_id:C,limit:2,...change});
const event=(change={})=>({revision:'2',command_type:'capture.edit',executor_actor_id:EXEC,initiator_actor_id:null,recorded_at:'2026-10-26T09:00:00.000001Z',...change});
const page=(change={})=>({account_id:A,org_id:O,capture_id:C,owner_account_id:OWNER,owner_actor_id:ACTOR,created_by:ACTOR,created_at:'2026-10-26T10:00:00Z',updated_by:EXEC,updated_at:'2026-10-26T08:00:00Z',current_revision:'2',limit:2,events:[event(),event({revision:'1',command_type:'capture.create',executor_actor_id:ACTOR,initiator_actor_id:ACTOR,recorded_at:'2026-10-26T11:00:00Z'})],next_cursor:null,...change});
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const response=(value=page(),status=200)=>new Response(JSON.stringify(value),{status,headers});
const audit=(request,options={},work=pending(),session={account_id:A,access_token:'synthetic'})=>auditEvents(session,work,{signal:new AbortController().signal,isCurrent:()=>true,request,timeoutMs:1000,...options});
const cursor=(last_revision='2',change={})=>Buffer.from(JSON.stringify(Object.fromEntries(Object.entries({v:1,account_id:A,org_id:O,capture_id:C,permission:'kdg_capture.capture.read.all',limit:2,last_revision,...change}).sort(([a],[b])=>a<b?-1:a>b?1:0)))).toString('base64url');
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return{promise,resolve};};
test('authorized cross-owner audit returns one closed immutable metadata page',async()=>{
 let calls=0;const result=await audit(async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/admin/captures/'+C+'/events?limit=2');
  assert.equal(init.method,'GET');assert.equal(init.body,undefined);assert.equal(init.headers.Authorization,'Bearer synthetic');
  assert.equal(init.credentials,'same-origin');assert.equal(init.mode,'same-origin');assert.equal(init.cache,'no-store');assert.equal(init.redirect,'error');
  return response();
 });
 assert.equal(result.kind,'loaded');assert.equal(calls,1);assert.deepEqual(result.page,page());
 for(const value of [result,result.page,result.page.events,...result.page.events])assert.ok(Object.isFrozen(value));
 assert.notEqual(result.page.owner_account_id,result.page.account_id);assert.equal(result.page.events[0].initiator_actor_id,null);
});

test('default limit, numeric bigint revisions, sparse history and independent statement times',async()=>{
 const work=pending();delete work.limit;
 const defaulted=await audit(async url=>{assert.equal(url,'/api/v1/admin/captures/'+C+'/events?limit=30');return response(page({limit:30}));},{},work);
 assert.equal(defaulted.kind,'loaded');assert.equal(defaulted.page.limit,30);
 const maximum='9223372036854775807',large=page({current_revision:maximum,events:[event({revision:maximum}),event({revision:'10',recorded_at:'2026-10-26T11:00:00Z'})],next_cursor:cursor('10')});
 assert.deepEqual((await audit(async()=>response(large))).page,large);
 const middle=page({current_revision:maximum,events:[event({revision:'9'}),event({revision:'2'})],next_cursor:cursor('2')});
 const result=await audit(async url=>{assert.equal(new URL(url,'https://synthetic.invalid').searchParams.get('cursor'),cursor('10'));return response(middle);},{},pending({cursor:cursor('10')}));
 assert.equal(result.kind,'loaded');
 assert.equal((await audit(async()=>response(page({events:[]})),{},pending({cursor:cursor('1')}))).kind,'loaded');
 assert.equal((await audit(async()=>response(page({events:[event({revision:'1',command_type:'capture.create',executor_actor_id:ACTOR})]})),{},pending({cursor:cursor('2')}))).kind,'loaded');
});

const malformedPages={
 foreign_reader:{account_id:OWNER},foreign_org:{org_id:C},foreign_capture:{capture_id:O},wrong_limit:{limit:30},unknown:{answers:{}},
 missing_events:{events:null},empty_first:{events:[]},over_limit:{events:[event(),event(),event()]},null_event:{events:[null]},
 bad_owner_account:{owner_account_id:'bad'},bad_owner_actor:{owner_actor_id:'bad'},bad_updated_actor:{updated_by:'bad'},bad_creation_actor:{created_by:EXEC},
 revision_zero:{current_revision:'0'},revision_leading_zero:{current_revision:'02'},revision_number:{current_revision:2},revision_overflow:{current_revision:'9223372036854775808'},
 bad_created_time:{created_at:'2026-02-30T10:00:00Z'},bad_updated_time:{updated_at:'0000-01-01T10:00:00Z'},
 wrong_current:{current_revision:'3'},above_current:{events:[event({revision:'3'})]},duplicate_revision:{events:[event(),event()]},ascending:{events:[page().events[1],event()]},
 bad_event_revision:{events:[event({revision:'02'})]},wrong_command:{events:[event({command_type:'capture.create'})]},wrong_latest_executor:{events:[event({executor_actor_id:ACTOR})]},
 wrong_create_executor:{events:[event(),page().events[1]&&event({revision:'1',command_type:'capture.create',executor_actor_id:EXEC})]},
 wrong_create_command:{events:[event(),event({revision:'1'})]},bad_executor:{events:[event({executor_actor_id:'bad'})]},bad_initiator:{events:[event({initiator_actor_id:'bad'})]},
 event_unknown:{events:[event({outcome_id:C})]},missing_initiator:{events:[(({initiator_actor_id,...rest})=>rest)(event())]},bad_event_time:{events:[event({recorded_at:'2026-10-26T10:60:00Z'})]},
 wrong_next_position:{next_cursor:cursor('2')},wrong_next_reader:{next_cursor:cursor('1',{account_id:OWNER})},wrong_next_capture:{next_cursor:cursor('1',{capture_id:O})},
 wrong_next_org:{next_cursor:cursor('1',{org_id:C})},wrong_next_permission:{next_cursor:cursor('1',{permission:'kdg_capture.capture.read.own'})},wrong_next_limit:{next_cursor:cursor('1',{limit:30})},
 wrong_next_version:{next_cursor:cursor('1',{v:2})},unknown_next_field:{next_cursor:cursor('1',{actor_id:EXEC})},malformed_next:{next_cursor:'x'},undefined_next:{next_cursor:undefined}
};
for(const [name,change] of Object.entries(malformedPages))test('invalid complete page '+name,async()=>assert.deepEqual(await audit(async()=>response(page(change))),{kind:'invalid_response'}));

test('every continuation event is strictly below the input revision and bounded by current',async()=>{
 for(const revision of ['3','2'])assert.equal((await audit(async()=>response(page({events:[event({revision})]})),{},pending({cursor:cursor('2')}))).kind,'invalid_response');
 assert.equal((await audit(async()=>response(page({events:[],next_cursor:cursor('1')})),{},pending({cursor:cursor('1')}))).kind,'invalid_response');
 // Current headers can advance between requests; continuation is navigation only.
 const advanced=page({current_revision:'4',events:[event({revision:'2'})]});
 assert.equal((await audit(async()=>response(advanced),{},pending({cursor:cursor('3')}))).kind,'loaded');
});

test('next cursor requires the full page produced by audit limit-plus-one lookahead',async()=>{
 const short=page({events:[event()],next_cursor:cursor('2')});
 assert.deepEqual(await audit(async()=>response(short)),{kind:'invalid_response'});
 const continued=page({events:[event({revision:'2'})],next_cursor:cursor('2')});
 assert.deepEqual(await audit(async()=>response(continued),{},pending({cursor:cursor('3')})),{kind:'invalid_response'});
});

test('revision one ends audit history even when a full page has a matching next cursor',async()=>{
 const exhausted=page({next_cursor:cursor('1')});
 for(const work of [pending(),pending({cursor:cursor('3')})]){
  assert.deepEqual(await audit(async()=>response(exhausted),{},work),{kind:'invalid_response'});
 }
});

test('local identity, scope and selector refusal happens without dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{account_id:OWNER},{account_id:'bad'},{org_id:'bad'},{capture_id:'bad'},{limit:0},{limit:101},{limit:1.5},{limit:'2'},{limit:null},{limit:undefined},{cursor:undefined},{cursor:null},{cursor:''},{owner_account_id:OWNER},{permission:'kdg_capture.capture.read.all'},{from_date:'2026-10-01'},{query:{limit:2}}])assert.equal((await audit(request,{},pending(change))).kind,'invalid_request');
 for(const session of [null,{}, {account_id:'bad',access_token:'synthetic'},{account_id:A,access_token:'bad token'},{account_id:A,access_token:'bad,token'}])assert.equal((await audit(request,{},pending(),session)).kind,'authentication_required');
 const bad=Object.defineProperty({},'org_id',{enumerable:true,get(){throw Error('PRIVATE');}});
 assert.equal((await audit(request,{},bad)).kind,'invalid_request');
 assert.equal(calls,0);
});

test('invalid options and throwing getters refuse locally',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{signal:null},{isCurrent:null},{request:null},{request:'bad'},{timeoutMs:null},{timeoutMs:0},{timeoutMs:-1},{timeoutMs:10001},{timeoutMs:NaN},{timeoutMs:Infinity},{owner_account_id:OWNER}])assert.equal((await audit(request,change)).kind,'invalid_request');
 const opts=Object.defineProperty({signal:new AbortController().signal,isCurrent:()=>true},'timeoutMs',{enumerable:true,get(){throw Error('PRIVATE');}});
 assert.deepEqual(await auditEvents({account_id:A,access_token:'synthetic'},pending(),opts),{kind:'invalid_request'});
 assert.equal(calls,0);
});

test('noncanonical, duplicate-key, foreign and malformed cursors never dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 const value=JSON.parse(Buffer.from(cursor(),'base64url').toString());
 const raw=text=>Buffer.from(text).toString('base64url');
 for(const c of ['x','x'.repeat(2049),cursor()+'=',raw(JSON.stringify(value,null,2)),raw(JSON.stringify(value).replace('"v":1','"v":1.0')),raw(JSON.stringify(value).replace('"v":1','"v":1,"v":1')),cursor('0'),cursor('01'),cursor('9223372036854775808'),cursor('2',{v:true}),cursor('2',{account_id:OWNER}),cursor('2',{org_id:C}),cursor('2',{capture_id:O}),cursor('2',{permission:'kdg_capture.capture.read.own'}),cursor('2',{limit:30}),cursor('2',{extra:'PRIVATE'}),cursor('漢')])assert.equal((await audit(request,{},pending({cursor:c}))).kind,'invalid_request');
 assert.equal(calls,0);
});

test('strict duplicate-key, grammar, UTF8 and Unicode validation fail as complete responses',async()=>{
 const raw=JSON.stringify(page());
 for(const body of ['{',raw+'x',raw.replace('"events":','"\\u0065vents":[],"events":'),raw.replace('"revision":"2"','"revision":"2","revision":"2"'),raw.replace('"limit":2','"limit":1e999'),raw.replace('"revision":"2"','"revision":"\\ud800"'),raw.replace('"revision":"2"','"revision":"\\u0000"'),new Uint8Array([255]),new Uint8Array([0xc3,0x28])])assert.deepEqual(await audit(async()=>new Response(body,{headers})),{kind:'invalid_response'});
});

test('actual streamed UTF8 bytes accept exactly 64KiB and refuse one extra despite Content-Length',async()=>{
 const raw=JSON.stringify(page()),encoded=new TextEncoder().encode(raw);
 for(const size of [65536,65537]){
  const bytes=new Uint8Array(size);bytes.fill(32);bytes.set(encoded);let cancelled=0;
  const stream=new ReadableStream({start(controller){controller.enqueue(bytes.subarray(0,200));controller.enqueue(bytes.subarray(200));controller.close();},cancel(){cancelled++;}});
  const result=await audit(async()=>new Response(stream,{headers:{...headers,'Content-Length':'1'}}));
  assert.equal(result.kind,size===65536?'loaded':'invalid_response');assert.ok(cancelled<=1);
 }
 // Multi-byte valid UTF8 remains measured in bytes, including safe error text.
 const error={error:'é'.repeat(33000),error_id:'access_denied'};
 assert.equal((await audit(async()=>response(error,403))).kind,'invalid_response');
});

test('response metadata and redirects are checked before publishing any page',async()=>{
 for(const selected of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'},{'Content-Type':'application/json','Cache-Control':'no-store'},{'Content-Type':'application/json','Cache-Control':'private'},{...headers,'Cache-Control':'public, private, no-store'}])assert.deepEqual(await audit(async()=>new Response(JSON.stringify(page()),{headers:selected})),{kind:'invalid_response'});
 const redirected=response();Object.defineProperty(redirected,'redirected',{value:true});
 assert.equal((await audit(async()=>redirected)).kind,'invalid_response');
 assert.equal((await audit(async()=>new Response(null,{status:204,headers}))).kind,'invalid_response');
 assert.equal((await audit(async()=>new Response(JSON.stringify(page()),{headers:{'Content-Type':'Application/JSON; charset=utf-8','Cache-Control':'PRIVATE, NO-STORE'}}))).kind,'loaded');
});

for(const [status,error_id] of [[401,'authentication_required'],[403,'access_denied'],[404,'capture_unavailable'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'capture_read_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe generated error '+status+' '+error_id,async()=>{
 const result=await audit(async()=>response({error:'PRIVATE BODY',error_id,code:77},status));
 assert.deepEqual(result,{kind:'error',status,error_id});assert.ok(Object.isFrozen(result));
});
test('unknown statuses, mismatched identifiers and invalid error metadata do not expose raw errors',async()=>{
 for(const [status,value] of [[403,{error:'PRIVATE',error_id:'capture_unavailable'}],[418,{error:'PRIVATE',error_id:'internal_error'}],[503,{error:'PRIVATE',error_id:'unknown'}],[403,{error:'PRIVATE',error_id:'access_denied',extra:'PRIVATE'}],[403,{error:5,error_id:'access_denied'}],[403,{error:'PRIVATE',error_id:'access_denied',code:'5'}]])assert.deepEqual(await audit(async()=>response(value,status)),{kind:'invalid_response'});
 let calls=0;const result=await audit(async()=>{calls++;throw Error('PRIVATE TOKEN');});
 assert.deepEqual(result,{kind:'verification_unavailable'});assert.equal(calls,1);
});

test('account bearer scope limit and cursor are pinned before an ignored-abort await',async()=>{
 const held=deferred(),session={account_id:A,access_token:'synthetic'},work=pending({cursor:cursor('3')});let init;
 const result=audit(async(url,options)=>{init=options;assert.equal(new URL(url,'https://synthetic.invalid').searchParams.get('cursor'),cursor('3'));return held.promise;},{},work,session);
 Object.assign(session,{account_id:OWNER,access_token:'changed'});Object.assign(work,{account_id:OWNER,org_id:C,capture_id:O,limit:30,cursor:'bad'});
 held.resolve(response());assert.equal((await result).kind,'loaded');assert.equal(init.headers.Authorization,'Bearer synthetic');
});

test('cancelled and superseded fetches discard late bodies and never retry',async()=>{
 for(const mode of ['cancel','supersede']){
  const held=deferred(),controller=new AbortController();let current=true,calls=0,cancelled=0;
  const result=audit(()=>{calls++;return held.promise;},{signal:controller.signal,isCurrent:()=>current,timeoutMs:20});
  if(mode==='cancel')controller.abort();else current=false;
  assert.equal((await result).kind,mode==='cancel'?'cancelled':'superseded');
  const stream=new ReadableStream({cancel(){cancelled++;}});held.resolve(new Response(stream,{headers}));
  await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,1);assert.equal(calls,1);
 }
});

test('one original deadline bounds ignored fetch and stalled body with best-effort cancellation',async()=>{
 const held=deferred();let cancelled=0;
 const started=performance.now();assert.deepEqual(await audit(()=>held.promise,{timeoutMs:10}),{kind:'verification_unavailable'});assert.ok(performance.now()-started<500);
 held.resolve(new Response(new ReadableStream({cancel(){cancelled++;}}),{headers}));await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,1);
 let bodyCancelled=0;
 const stream=new ReadableStream({pull(){return new Promise(()=>{});},cancel(){bodyCancelled++;}});
 assert.equal((await audit(async()=>new Response(stream,{headers}),{timeoutMs:10})).kind,'verification_unavailable');assert.equal(bodyCancelled,1);
});

test('body cancellation, supersession and stream errors discard partial metadata',async()=>{
 for(const mode of ['cancel','supersede','error']){
  let current=true,control,cancelled=0;const controller=new AbortController(),started=deferred();
  const bytes=new TextEncoder().encode(JSON.stringify(page()));
  const stream=new ReadableStream({start(c){control=c;c.enqueue(bytes.subarray(0,100));},pull(){started.resolve();return new Promise(()=>{});},cancel(){cancelled++;}});
  const result=audit(async()=>new Response(stream,{headers}),{signal:controller.signal,isCurrent:()=>current,timeoutMs:20});await started.promise;
  if(mode==='cancel')controller.abort();else if(mode==='supersede')current=false;else control.error(Error('PRIVATE'));
  assert.deepEqual(await result,{kind:mode==='cancel'?'cancelled':mode==='supersede'?'superseded':'verification_unavailable'});
  if(mode!=='error')assert.equal(cancelled,1);
 }
});

test('immediately resolved empty chunks cannot starve the original deadline',async()=>{
 let cancelled=0;const stream=new ReadableStream({pull(c){c.enqueue(new Uint8Array());},cancel(){cancelled++;}});
 assert.deepEqual(await audit(async()=>new Response(stream,{headers}),{timeoutMs:5}),{kind:'verification_unavailable'});assert.equal(cancelled,1);
});

test('publication rechecks generation, abort, and the original deadline',async()=>{
 for(const mode of ['supersede','cancel','deadline','throw']){
  let calls=0;const controller=new AbortController();
  const result=await audit(async()=>response(),{signal:controller.signal,timeoutMs:25,isCurrent:()=>{
   if(++calls===6){if(mode==='supersede')return false;if(mode==='cancel')controller.abort();if(mode==='throw')throw Error('PRIVATE');if(mode==='deadline'){const end=performance.now()+30;while(performance.now()<end){}}}
   return true;
  }});
  assert.equal(calls,6);assert.deepEqual(result,{kind:mode==='cancel'?'cancelled':mode==='deadline'?'verification_unavailable':'superseded'});
 }
});

test('initial stale, cancelled and reentrant predicate executions do not dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 assert.equal((await audit(request,{isCurrent:()=>false})).kind,'superseded');
 assert.equal((await audit(request,{isCurrent:()=>{throw Error('PRIVATE');}})).kind,'superseded');
 const cancelled=new AbortController();cancelled.abort();assert.equal((await audit(request,{signal:cancelled.signal})).kind,'cancelled');
 const reentrant=new AbortController();assert.equal((await audit(request,{signal:reentrant.signal,isCurrent:()=>{reentrant.abort();return true;}})).kind,'cancelled');
 assert.equal(calls,0);
});
