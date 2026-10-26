import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readCapture} from '../../../../compiled/web/src/read.js';
import {A,O,C,Q,detail,pending,response} from './read-fixture.mjs';
const read=(request,options={},work=pending(),session={account_id:A,access_token:'synthetic'})=>readCapture(session,work,{signal:new AbortController().signal,isCurrent:()=>true,request,timeoutMs:1000,...options});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
test('one generated own-detail GET returns deeply immutable original definition and current detail',async()=>{
 let calls=0;const result=await read(async(url,init)=>{calls++;assert.equal(url,'/api/v1/captures/'+C);assert.equal(init.method,'GET');assert.equal(init.body,undefined);assert.equal(init.headers.Authorization,'Bearer synthetic');assert.equal(init.cache,'no-store');return response();});
 assert.equal(result.kind,'loaded');assert.deepEqual(result.snapshot,detail());assert.equal(calls,1);
 for(const value of [result,result.snapshot,result.snapshot.answers,result.snapshot.answers[Q],result.snapshot.definition,result.snapshot.definition.questions,result.snapshot.definition.questions[0]])assert.ok(Object.isFrozen(value));
});
for(const [name,changes] of Object.entries({wrong_owner:{owner_account_id:Q},wrong_org:{org_id:Q},wrong_capture:{capture_id:Q},bad_actor:{owner_actor_id:null},wrong_creator:{created_by:Q},bad_revision:{revision:'01'},overflow:{revision:'9223372036854775808'},version:{questionnaire_version:'0'},numeric_version:{questionnaire_version:1},future_schema:{definition:{schema_version:2,questions:detail().definition.questions}},foreign_answer:{answers:{[A]:{value:3}}},missing_answer:{answers:{}},boolean_rating:{answers:{[Q]:{value:true}}},bad_day:{observation_date:'2026-02-30'},bad_timestamp:{created_at:'2026-10-26T25:00:00Z'},unknown:{private:'SENSITIVE'},missing_label:{child_label:''},too_long_label:{child_label:'x'.repeat(201)}}))test('refuses '+name,async()=>assert.deepEqual(await read(async()=>response(detail(changes))),{kind:'invalid_response'}));
test('rating boolean and text use original types, details configuration and unique question ids',async()=>{
 const boolean={id:Q,type:'boolean',label:'Boolean',required:true,default:false,details_enabled:true,details_label:'Details'};
 const value=detail({definition:{schema_version:1,questions:[boolean]},answers:{[Q]:{value:true,details:'ok'}}});
 assert.equal((await read(async()=>response(value))).kind,'loaded');
 for(const bad of [detail({definition:{schema_version:1,questions:[boolean,boolean]}}),{...value,answers:{[Q]:{value:false,details:'hidden'}}},{...value,answers:{[Q]:{value:true,details:null}}},{...value,definition:{schema_version:1,questions:[{...boolean,details_enabled:false}]}}])assert.equal((await read(async()=>response(bad))).kind,'invalid_response');
 const text={id:Q,type:'text',label:'Text',required:true};
 assert.equal((await read(async()=>response(detail({definition:{schema_version:1,questions:[text]},answers:{[Q]:{value:'ok'}}})))).kind,'loaded');
 assert.equal((await read(async()=>response(detail({definition:{schema_version:1,questions:[text]},answers:{[Q]:{value:' '}}})))).kind,'invalid_response');
});
for(const [status,error_id] of [[401,'authentication_required'],[403,'access_denied'],[404,'capture_unavailable'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'capture_read_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe error '+status+' '+error_id,async()=>assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id},status)),{kind:'error',status,error_id}));
test('malformed JSON UTF8 duplicate escaped keys oversized bodies and wrong metadata refuse',async()=>{
 const raw=JSON.stringify(detail());
 for(const body of ['{',raw.replace('"revision":','"\\u0072evision":"2","revision":'),' '.repeat(524289),new Uint8Array([255]),raw.replace('Child','\\ud800')])assert.equal((await read(async()=>new Response(body,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}))).kind,'invalid_response');
 for(const headers of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'}])assert.equal((await read(async()=>new Response(raw,{headers}))).kind,'invalid_response');
 for(const [status,body] of [[201,detail()],[404,{error:'x',error_id:'access_denied'}],[503,{error:'x',error_id:'capture_read_unavailable',private:'x'}]])assert.equal((await read(async()=>response(body,status))).kind,'invalid_response');
});
test('invalid identity query selectors bearer and leases never dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const work of [pending({account_id:Q}),pending({org_id:'invalid'}),pending({capture_id:'invalid'}),pending({operation_id:A})])assert.equal((await read(request,{},work)).kind,'invalid_request');
 assert.equal((await read(request,{isCurrent:undefined})).kind,'invalid_request');
 assert.equal((await read(request,{},pending(),{account_id:A,access_token:'bad,token'})).kind,'authentication_required');assert.equal(calls,0);
});
test('cancellation stale generation and deadline discard late snapshots without retry',async()=>{
 let current=true;const held=deferred(),controller=new AbortController();
 const work=read(()=>held.promise,{isCurrent:()=>current,signal:controller.signal});current=false;held.resolve(response());assert.equal((await work).kind,'superseded');
 const other=deferred(),cancelled=read(()=>other.promise,{signal:controller.signal});controller.abort();assert.equal((await cancelled).kind,'cancelled');other.resolve(response());
 assert.equal((await read(()=>new Promise(()=>{}),{timeoutMs:5})).kind,'verification_unavailable');
 const body=new ReadableStream({pull(){return new Promise(()=>{});}});
 assert.equal((await read(async()=>new Response(body,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:5})).kind,'verification_unavailable');
});
test('input mutation and reentrant owner cancellation cannot retarget or publish',async()=>{
 const held=deferred(),work=pending();const result=read(()=>held.promise,{},work);work.capture_id=Q;held.resolve(response());assert.equal((await result).snapshot.capture_id,C);
 const controller=new AbortController();let calls=0;assert.equal((await read(async()=>{calls++;return response();},{signal:controller.signal,isCurrent:()=>{controller.abort();return true;}})).kind,'cancelled');assert.equal(calls,0);
});
for(const [field,value] of [['revision','1\n'],['questionnaire_version','2\n'],['created_at','2026-10-26T10:00:00Z\n'],['updated_at','2026-10-26T10:00:00Z\r\n'],['captured_at','2026-10-26T10:00:00Z\n'],['observation_date','0000-01-01'],['captured_at','0000-01-01T00:00:00Z']])test('strict canonical '+field+' '+JSON.stringify(value),async()=>assert.equal((await read(async()=>response(detail({[field]:value})))).kind,'invalid_response'));
test('512KiB UTF8 ceiling accepts exact bytes split through a codepoint and rejects one extra',async()=>{
 const raw=JSON.stringify(detail({child_label:'Kind 😀'})),encoded=new TextEncoder().encode(raw);
 const bytes=new Uint8Array(524288);bytes.fill(32);bytes.set(encoded);
 const marker=encoded.findIndex(x=>x===0xf0)+2;
 const send=body=>new Response(new ReadableStream({start(c){c.enqueue(body.subarray(0,marker));c.enqueue(body.subarray(marker));c.close();}}),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
 assert.equal((await read(async()=>send(bytes))).kind,'loaded');
 const oversized=new Uint8Array(524289);oversized.fill(32);oversized.set(bytes);
 assert.equal((await read(async()=>send(oversized))).kind,'invalid_response');
});
test('endless immediate empty chunks cannot starve the original deadline',async()=>{
 const stream=new ReadableStream({pull(c){c.enqueue(new Uint8Array());}});
 assert.equal((await read(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:5})).kind,'verification_unavailable');
});
for(const [value,expected] of [['',false],[' ',false],['\ufeff',true],['\u0085',false],['\u001c',false],['\u0085\u001c ',false],['\ufeff\u0085',true]])test('Python nonblank label and text parity '+JSON.stringify(value),async()=>{
 const base=detail({child_label:value,definition:{schema_version:1,questions:[{id:Q,type:'text',label:value,required:true}]},answers:{[Q]:{value}}});
 assert.equal((await read(async()=>response(base))).kind,expected?'loaded':'invalid_response');
 base.child_label='Child';base.definition.questions[0].label='Question';
 assert.equal((await read(async()=>response(base))).kind,expected?'loaded':'invalid_response');
});
test('fractional optional error code violates the generated integer contract',async()=>assert.equal((await read(async()=>response({error:'safe',error_id:'capture_unavailable',code:1.5},404))).kind,'invalid_response'));
