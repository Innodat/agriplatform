import assert from 'node:assert/strict';
import {test} from 'node:test';
import {recoverOperation} from '../src/recovery.ts';
const A='11111111-1111-4111-8111-111111111111',O='22222222-2222-4222-8222-222222222222',
 OP='33333333-3333-4333-8333-333333333333',C='44444444-4444-4444-8444-444444444444',OTHER='55555555-5555-4555-8555-555555555555';
const session=()=>({account_id:A,access_token:'synthetic-token'});
const pending=(changes={})=>({account_id:A,org_id:O,operation_id:OP,command_type:'capture.create',...changes});
const receipt=(changes={})=>({operation_id:OP,command_type:'capture.create',command_version:1,status:'committed',result:{capture_id:C,revision:'9223372036854775807'},...changes});
const unresolved=()=>({operation_id:OP,command_type:'capture.create',status:'unresolved'});
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
const lease=()=>({signal:new AbortController().signal,isCurrent:()=>true});
const read=(request,options={},work=pending(),auth=session())=>recoverOperation(auth,work,{...lease(),request,timeoutMs:100,...options});
const tick=()=>new Promise(r=>setTimeout(r,0));
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};

test('one own read pins the original discriminator and returns an immutable original receipt',async()=>{
 let calls=0;
 const result=await read(async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/operations/'+OP+'?command_type=capture.create');
  assert.equal(init.method,'GET');assert.equal(init.headers.Authorization,'Bearer synthetic-token');
  for(const [key,value] of Object.entries({credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error'}))assert.equal(init[key],value);
  assert.equal(init.body,undefined);return response(receipt());
 });
 assert.equal(calls,1);assert.equal(result.kind,'committed');assert.equal(result.receipt.result.revision,'9223372036854775807');
 assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.receipt));assert.ok(Object.isFrozen(result.receipt.result));
});
test('verified unresolved remains separate from an error and allocates no new identity',async()=>{
 let calls=0;const original=pending();const result=await read(async()=>{calls++;return response(unresolved());},{},original);
 assert.equal(result.kind,'unresolved');assert.equal(result.outcome.operation_id,OP);assert.equal(calls,1);assert.deepEqual(original,pending());
});
test('edit accepts only its frozen capture target; create preserves first committed target',async()=>{
 const work=pending({command_type:'capture.edit',capture_id:C});
 const body=receipt({command_type:'capture.edit'});
 assert.equal((await read(async()=>response(body),{},work)).kind,'committed');
 assert.deepEqual(await read(async()=>response({...body,result:{capture_id:OTHER,revision:'1'}}),{},work),{kind:'invalid_response'});
 assert.equal((await read(async()=>response(receipt({result:{capture_id:OTHER,revision:'1'}})))).receipt.result.capture_id,OTHER);
});
for(const [name,change] of Object.entries({wrong_operation:{operation_id:OTHER},wrong_command:{command_type:'capture.edit'},version:{command_version:2},missing_status:{status:undefined},extra:{private:'canary'},numeric_revision:{result:{capture_id:C,revision:1}},overflow:{result:{capture_id:C,revision:'9223372036854775808'}},leading_zero:{result:{capture_id:C,revision:'01'}},trailing_newline:{result:{capture_id:C,revision:'1\n'}},nil_target:{result:{capture_id:'00000000-0000-0000-0000-000000000000',revision:'1'}},extra_result:{result:{capture_id:C,revision:'1',answers:'canary'}}}))test('rejects '+name,async()=>{
 assert.deepEqual(await read(async()=>response(receipt(change))),{kind:'invalid_response'});
});
for(const [status,id] of [[401,'authentication_required'],[403,'access_denied'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'operation_verification_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe status pair '+status+' '+id,async()=>{
 const result=await read(async()=>response({error:'SENSITIVE',error_id:id},status));
 assert.deepEqual(result,{kind:'error',status,error_id:id});assert.ok(!JSON.stringify(result).includes('SENSITIVE'));
});
test('wrong status families, extra error fields and legacy payloads never imply unresolved',async()=>{
 for(const [status,body] of [[403,{error:'x',error_id:'internal_error'}],[503,{error:'x',error_id:'raw_exception'}],[503,{error:'x',error_id:'execution_timeout',detail:'SENSITIVE'}],[401,{detail:{code:'authentication_required'}}],[201,unresolved()]])assert.deepEqual(await read(async()=>response(body,status)),{kind:'invalid_response'});
});
test('invalid account, selectors, command and lease fail before fetch',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 for(const work of [pending({account_id:OTHER}),pending({org_id:O+'\n'}),pending({command_type:'capture.delete'}),pending({command_type:'capture.edit'}),pending({operation_id:OP.toUpperCase()+'x'}),pending({target_id:C})])assert.deepEqual(await read(request,{},work),{kind:'invalid_request'});
 assert.deepEqual(await read(request,{isCurrent:undefined}),{kind:'invalid_request'});
 assert.deepEqual(await read(request,{},pending(),{account_id:A,access_token:'bad,token'}),{kind:'authentication_required'});
 assert.equal(calls,0);
});
test('stale generations and cancellation discard both success and denial',async()=>{
 for(const status of [200,403]){
  const gate=deferred();let current=true;const controller=new AbortController();
  const work=read(()=>gate.promise,{isCurrent:()=>current,signal:controller.signal});
  current=false;gate.resolve(response(status===200?receipt():{error:'private',error_id:'access_denied'},status));
  assert.deepEqual(await work,{kind:'superseded'});
 }
 const controller=new AbortController();const gate=deferred();const work=read(()=>gate.promise,{signal:controller.signal});
 controller.abort();assert.deepEqual(await work,{kind:'cancelled'});gate.resolve(response(receipt()));await tick();
});
test('one deadline bounds headers/body even when fetch or reader ignores abort',async()=>{
 assert.deepEqual(await read(()=>new Promise(()=>{}),{timeoutMs:10}),{kind:'verification_unavailable'});
 const stream=new ReadableStream({pull(){return new Promise(()=>{});}});
 assert.deepEqual(await read(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:10}),{kind:'verification_unavailable'});
});
test('malformed bytes, duplicate/escaped duplicate keys, size and body metadata are refused',async()=>{
 const raw=JSON.stringify(receipt());
 for(const body of [raw.replace('"operation_id":','"operation_id":"'+OTHER+'","operation_id":'),raw.replace('"operation_id":','"\\u006fperation_id":"'+OTHER+'","operation_id":'),raw.replace('"revision":','"revision":"1","revision":'),'{bad',' '.repeat(16385),new Uint8Array([255])]){
  assert.deepEqual(await read(async()=>new Response(body,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
 }
 for(const headers of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'}])assert.deepEqual(await read(async()=>new Response(raw,{headers})),{kind:'invalid_response'});
});

test('network failures do not expose exceptions or imply absence',async()=>{
 const result=await read(async()=>{throw new TypeError('SENSITIVE network token');});
 assert.deepEqual(result,{kind:'verification_unavailable'});
 assert.ok(!JSON.stringify(result).includes('SENSITIVE'));
});
test('rejected response metadata and late headers cancel their body',async()=>{
 let discarded=0;
 const body=()=>new ReadableStream({cancel(){discarded++;}});
 assert.deepEqual(await read(async()=>new Response(body(),{headers:{'Content-Type':'text/plain'}})),{kind:'invalid_response'});
 await tick();assert.equal(discarded,1);
 const gate=deferred();assert.deepEqual(await read(()=>gate.promise,{timeoutMs:5}),{kind:'verification_unavailable'});
 gate.resolve(new Response(body()));await tick();assert.equal(discarded,2);
});
test('pre-cancelled/stale/failed leases never send, including replacement generation',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 const controller=new AbortController();controller.abort();
 assert.deepEqual(await read(request,{signal:controller.signal}),{kind:'cancelled'});
 assert.deepEqual(await read(request,{isCurrent:()=>false}),{kind:'superseded'});
 assert.deepEqual(await read(request,{isCurrent:()=>{throw new Error('SENSITIVE');}}),{kind:'superseded'});
 assert.equal(calls,0);
 for(const event of ['account','org','token','A-B-A','dispose']){
  const gate=deferred();let generation=1;const observed=generation;
  const work=read(()=>gate.promise,{isCurrent:()=>generation===observed});
  generation++;gate.resolve(response(receipt()));assert.deepEqual(await work,{kind:'superseded'},event);
 }
});
test('duplicate scanning accepts ordinary escaped message text and refuses invalid Unicode/nonfinite values',async()=>{
 assert.deepEqual(await read(async()=>response({error:'{"quoted": "\\} ✓"}',error_id:'access_denied',code:null},403)),{kind:'error',status:403,error_id:'access_denied'});
 for(const body of ['{"error":"\\ud800","error_id":"access_denied"}','{"error":"\\u0000","error_id":"access_denied"}','{"error":"x","error_id":"access_denied","code":1e999}'])assert.deepEqual(await read(async()=>new Response(body,{status:403,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
});
test('safe error catalogue matches the candidate contract',async()=>{
 const {readFileSync}=await import('node:fs');
 const schema=JSON.parse(readFileSync(new URL('../../write-candidate/recovery-openapi.json',import.meta.url),'utf8'));
 const errors=schema.paths['/api/v1/operations/{operation_id}'].get.responses;
 for(const [status,definition] of Object.entries(errors)){
  if(status==='200')continue;
  const ref=definition.content['application/json'].schema.$ref.split('/').at(-1);
  for(const error_id of schema.components.schemas[ref].properties.error_id.enum){
   assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id},Number(status))),{kind:'error',status:Number(status),error_id});
  }
 }
});

test('empty microtask chunks cannot starve the total deadline or grow retained chunks',async t=>{
 let clock=0,pulled=0,cancelled=0;
 t.mock.method(performance,'now',()=>clock);
 const stream=new ReadableStream({pull(controller){pulled++;clock+=2;if(pulled<30)controller.enqueue(new Uint8Array());else controller.close();},cancel(){cancelled++;}});
 const result=await read(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:10});
 assert.deepEqual(result,{kind:'verification_unavailable'});assert.ok(pulled<30);assert.equal(cancelled,1);
});
test('pending/session/options mutation cannot retarget a request or edit acknowledgement',async()=>{
 for(const kind of ['capture.create','capture.edit']){
  const auth=session(),work=pending(kind==='capture.edit'?{command_type:kind,capture_id:C}:{}),gate=deferred();let call;
  const options={...lease(),timeoutMs:100,request:async(url,init)=>{call={url,init};return gate.promise;}};
  const result=recoverOperation(auth,work,options);
  auth.account_id=OTHER;auth.access_token='replacement';Object.assign(work,{account_id:OTHER,org_id:OTHER,operation_id:OTHER,command_type:'capture.delete',capture_id:OTHER});
  options.isCurrent=()=>false;options.timeoutMs=1;options.request=()=>{throw new Error('must use pinned transport');};
  gate.resolve(response(receipt({command_type:kind})));
  const returned=await result;assert.equal(returned.kind,'committed');assert.equal(returned.receipt.operation_id,OP);assert.equal(returned.receipt.result.capture_id,C);
  assert.equal(call.url,'/api/v1/operations/'+OP+'?command_type='+kind);assert.equal(call.init.headers.Authorization,'Bearer synthetic-token');
 }
});
test('body-phase cancellation/staleness/failed predicate cancels the acquired reader',async()=>{
 for(const mode of ['abort','stale','predicate_error']){
  const started=deferred();let controller,cancelled=0,current=true;const signal=new AbortController();
  const stream=new ReadableStream({start(c){controller=c;},pull(){started.resolve();},cancel(){cancelled++;}});
  const work=read(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{signal:signal.signal,isCurrent:()=>{if(current==='throw')throw new Error('SENSITIVE');return current;}});
  await started.promise;await tick();
  if(mode==='abort')signal.abort();else{current=mode==='stale'?false:'throw';controller.enqueue(new TextEncoder().encode(JSON.stringify(receipt())));}
  assert.deepEqual(await work,{kind:mode==='abort'?'cancelled':'superseded'});await tick();
  assert.equal(cancelled,1);
 }
});
test('unresolved refuses extra receipt fields and mismatched binding for create and edit',async()=>{
 for(const kind of ['capture.create','capture.edit']){
  const work=pending(kind==='capture.edit'?{command_type:kind,capture_id:C}:{}),body={...unresolved(),command_type:kind};
  assert.equal((await read(async()=>response(body),{},work)).kind,'unresolved');
  for(const change of [{command_version:1},{result:{capture_id:C,revision:'1'}},{extra:'SENSITIVE'},{operation_id:OTHER},{command_type:kind==='capture.create'?'capture.edit':'capture.create'}])assert.deepEqual(await read(async()=>response({...body,...change}),{},work),{kind:'invalid_response'});
 }
});
test('body limit counts cumulative UTF-8 bytes at 16384, including split multibyte sequences',async()=>{
 const encoder=new TextEncoder();
 const payload=(size,multi)=>{
  const fixed=encoder.encode(JSON.stringify({error:'',error_id:'access_denied'})).length,remaining=size-fixed;
  const value=JSON.stringify({error:multi?'é'.repeat(Math.floor(remaining/2))+'x'.repeat(remaining%2):'x'.repeat(remaining),error_id:'access_denied'});
  const bytes=encoder.encode(value);assert.equal(bytes.length,size);return bytes;
 };
 for(const multi of [false,true]){
  const valid=payload(16384,multi);let acceptedOffset=0;
  const accepted=multi?new ReadableStream({pull(c){if(acceptedOffset>=valid.length){c.close();return;}const next=Math.min(acceptedOffset+103,valid.length);c.enqueue(valid.subarray(acceptedOffset,next));acceptedOffset=next;}}):valid;
  assert.deepEqual(await read(async()=>new Response(accepted,{status:403,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'error',status:403,error_id:'access_denied'});
  const oversized=payload(16385,multi);let cancelled=0,index=0;
  const stream=new ReadableStream({pull(c){if(index<oversized.length){const next=Math.min(index+103,oversized.length);c.enqueue(oversized.subarray(index,next));index=next;}},cancel(){cancelled++;}});
  assert.deepEqual(await read(async()=>new Response(stream,{status:403,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
  await tick();assert.equal(cancelled,1);
 }
});
