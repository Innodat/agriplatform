import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createCapture} from '../../../../compiled/web/src/create.js';
const A='11111111-1111-4111-8111-111111111111',O='22222222-2222-4222-8222-222222222222',
 OP='33333333-3333-4333-8333-333333333333',C='44444444-4444-4444-8444-444444444444',OTHER='55555555-5555-4555-8555-555555555555';
const session=()=>({account_id:A,access_token:'synthetic-token'});
const command=(changes={})=>({operation_id:OP,command_version:1,capture_id:C,child_id:C,questionnaire_version_id:C,captured_at:'2026-10-26T10:00:00Z',child_eligibility_ref:'synthetic',observation_date:'2026-10-26',answers:{[C]:{value:'original ✓'}},...changes});
const pending=(changes={})=>({account_id:A,org_id:O,command:command(),...changes});
const receipt=(changes={})=>({operation_id:OP,command_type:'capture.create',command_version:1,status:'committed',result:{capture_id:C,revision:'9223372036854775807'},...changes});
const unresolved=()=>({operation_id:OP,command_type:'capture.create',status:'unresolved'});
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
const lease=()=>({signal:new AbortController().signal,isCurrent:()=>true});
const read=(request,options={},work=pending(),auth=session())=>createCapture(auth,work,{...lease(),request,timeoutMs:1000,...options});
const tick=()=>new Promise(r=>setTimeout(r,0));
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};

test('one create pins the original command and returns an immutable original receipt',async()=>{
 let calls=0;
 const result=await read(async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/captures');
  assert.equal(init.method,'POST');assert.equal(init.headers['Content-Type'],'application/json');assert.equal(init.headers.Authorization,'Bearer synthetic-token');
  for(const [key,value] of Object.entries({credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error'}))assert.equal(init[key],value);
  assert.deepEqual(JSON.parse(init.body),command());return response(receipt());
 });
 assert.equal(calls,1);assert.equal(result.kind,'committed');assert.equal(result.receipt.result.revision,'9223372036854775807');
 assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.receipt));assert.ok(Object.isFrozen(result.receipt.result));
});
for(const [name,change] of Object.entries({wrong_operation:{operation_id:OTHER},wrong_command:{command_type:'capture.edit'},version:{command_version:2},missing_status:{status:undefined},extra:{private:'canary'},numeric_revision:{result:{capture_id:C,revision:1}},overflow:{result:{capture_id:C,revision:'9223372036854775808'}},leading_zero:{result:{capture_id:C,revision:'01'}},trailing_newline:{result:{capture_id:C,revision:'1\n'}},nil_target:{result:{capture_id:'00000000-0000-0000-0000-000000000000',revision:'1'}},extra_result:{result:{capture_id:C,revision:'1',answers:'canary'}}}))test('rejects '+name,async()=>{
 assert.deepEqual(await read(async()=>response(receipt(change))),{kind:'invalid_response'});
});
for(const [status,id] of [[401,'authentication_required'],[403,'access_denied'],[403,'assignment_unavailable'],[409,'identity.actor_setup_required'],[409,'operation_busy'],[409,'questionnaire_version_unavailable'],[422,'unsupported_command_version'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'operation_verification_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe status pair '+status+' '+id,async()=>{
 const result=await read(async()=>response({error:'SENSITIVE',error_id:id},status));
 assert.deepEqual(result,{kind:'error',status,error_id:id});assert.ok(!JSON.stringify(result).includes('SENSITIVE'));
});
test('wrong status families, extra error fields and legacy payloads never imply absence',async()=>{
 for(const [status,body] of [[403,{error:'x',error_id:'internal_error'}],[503,{error:'x',error_id:'raw_exception'}],[503,{error:'x',error_id:'execution_timeout',detail:'SENSITIVE'}],[401,{detail:{code:'authentication_required'}}],[201,unresolved()]])assert.deepEqual(await read(async()=>response(body,status)),{kind:'invalid_response'});
});
test('invalid account, selectors, command and lease fail before fetch',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 for(const work of [pending({account_id:OTHER}),pending({org_id:O+'\n'}),pending({command:command({capture_id:C+'x'})}),pending({command:command({command_version:2})}),pending({command:command({operation_id:OP+'x'})}),pending({target_id:C})])assert.deepEqual(await read(request,{},work),{kind:'invalid_request'});
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
test('empty microtask chunks cannot starve the total deadline or grow retained chunks',async t=>{
 let clock=0,pulled=0,cancelled=0;
 t.mock.method(performance,'now',()=>clock);
 const stream=new ReadableStream({pull(controller){pulled++;clock+=2;if(pulled<30)controller.enqueue(new Uint8Array());else controller.close();},cancel(){cancelled++;}});
 const result=await read(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:10});
 assert.deepEqual(result,{kind:'verification_unavailable'});assert.ok(pulled<30);assert.equal(cancelled,1);
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

test('receipt target must match the original POST target and unresolved cannot acknowledge',async()=>{
 for(const body of [receipt({result:{capture_id:OTHER,revision:'1'}}),unresolved(),receipt({command_type:'capture.edit'}),receipt({command_version:'1'})])assert.deepEqual(await read(async()=>response(body)),{kind:'invalid_response'});
});
test('snapshot pins serialized nested answers, session, command, target and options before awaiting',async()=>{
 const auth=session(),work=pending(),original=structuredClone(work),gate=deferred();let call;
 const options={...lease(),request:async(url,init)=>{call={url,init};return gate.promise;},timeoutMs:1000};
 const result=createCapture(auth,work,options);
 auth.account_id=OTHER;auth.access_token='replacement';work.command.answers[C].value='changed';work.command.operation_id=OTHER;work.command.capture_id=OTHER;work.org_id=OTHER;
 options.request=()=>{throw Error('must not call');};options.isCurrent=()=>false;options.timeoutMs=1;
 gate.resolve(response(receipt()));assert.equal((await result).kind,'committed');
 assert.equal(call.url,'/api/v1/captures');assert.deepEqual(JSON.parse(call.init.body),original.command);assert.equal(call.init.headers.Authorization,'Bearer synthetic-token');
});
test('request byte ceiling uses serialized UTF-8 bytes, accepts exactly131072 and refuses131073',async()=>{
 for(const multi of [false,true])for(const size of [131072,131073]){
  const work=pending();work.command.answers[C].value='';const fixed=new TextEncoder().encode(JSON.stringify(work.command)).length,remaining=size-fixed;
  work.command.answers[C].value=multi?'é'.repeat(Math.floor(remaining/2))+'x'.repeat(remaining%2):'x'.repeat(remaining);
  const original=structuredClone(work);let calls=0;
  const result=await read(async(_url,init)=>{calls++;assert.equal(new TextEncoder().encode(init.body).length,size);return response(receipt());},{},work);
  assert.equal(result.kind,size===131072?'committed':'invalid_request');assert.equal(calls,size===131072?1:0);assert.deepEqual(work,original);
 }
});
test('invalid request identity/revision/options and unserializable input refuse before transport',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 for(const changes of [{org_id:'00000000-0000-0000-0000-000000000000'},{command:command({capture_id:'ABCDEFAB-1111-4111-8111-111111111111'})},{command:command({operation_id:'00000000-0000-0000-0000-000000000000'})},{command:command({extra:'canary'})}])assert.equal((await read(request,{},pending(changes))).kind,'invalid_request');
 for(const options of [{timeoutMs:0},{timeoutMs:10001},{timeoutMs:NaN},{signal:undefined},{request:42}])assert.equal((await read(request,options)).kind,'invalid_request');
 const cyclic=pending();cyclic.command.answers.loop=cyclic;assert.equal((await read(request,{},cyclic)).kind,'invalid_request');
 assert.equal(calls,0);
});
test('all failures preserve the caller command and make exactly one attempt',async()=>{
 for(const request of [async()=>response(receipt({operation_id:OTHER})),async()=>response({error:'SENSITIVE',error_id:'access_denied'},403),async()=>{throw Error('SENSITIVE');},()=>new Promise(()=>{})]){
  const work=pending(),original=structuredClone(work);let calls=0;
  await read((...args)=>{calls++;return request(...args);},{timeoutMs:5},work);assert.equal(calls,1);assert.deepEqual(work,original);
 }
});
test('all generated status/id variants are mapped without upstream messages',async()=>{
 const {readFileSync}=await import('node:fs');
 const schema=JSON.parse(readFileSync(new URL('../../write-candidate/create-openapi.json',import.meta.url),'utf8'));
 const deref=s=>s.$ref?schema.components.schemas[s.$ref.split('/').at(-1)]:s;
 for(const [status,definition] of Object.entries(schema.paths['/api/v1/captures'].post.responses)){
  if(status==='200')continue;
  const body=deref(definition.content['application/json'].schema);
  for(const variant of body.oneOf??[body]){
   const model=deref(variant);
   for(const error_id of model.properties.error_id.const?[model.properties.error_id.const]:model.properties.error_id.enum){
   const extra=error_id==='kdg_capture.capture_revision_conflict'?{current_revision:'3'}:{};
   assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id,...extra},Number(status))),{kind:'error',status:Number(status),error_id,...extra});
   }
  }
 }
});

test('stale and throwing fences suppress late network failures as well as responses',async()=>{
 for(const mode of ['stale','throw']){
  let current=true,reject;const gate=new Promise((_r,j)=>reject=j);
  const result=read(()=>gate,{isCurrent:()=>{if(current==='throw')throw Error('SENSITIVE');return current;}});
  current=mode==='throw'?'throw':false;reject(Error('SENSITIVE bearer'));assert.deepEqual(await result,{kind:'superseded'});
 }
});
test('redirects, missing bodies, extra/nested unsafe errors and duplicate conflict metadata are refused',async()=>{
 const redirected=response(receipt());Object.defineProperty(redirected,'redirected',{value:true});
 assert.deepEqual(await read(async()=>redirected),{kind:'invalid_response'});
 assert.deepEqual(await read(async()=>new Response(null,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
 for(const body of [{error:'x',error_id:'access_denied',answers:{}},{error:{message:'SENSITIVE'},error_id:'access_denied'},{error:'x',error_id:'access_denied',code:'SENSITIVE'}])assert.deepEqual(await read(async()=>response(body,403)),{kind:'invalid_response'});
 const conflict='{"error":"x","error_id":"kdg_capture.capture_revision_conflict","current_revision":"1","current_\\u0072evision":"2"}';
 assert.deepEqual(await read(async()=>new Response(conflict,{status:409,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
});
test('serialization uses the original deadline and cannot dispatch after it expires',async t=>{
 let now=0,calls=0;t.mock.method(performance,'now',()=>now);
 const work=pending();work.command.answers[C]={toJSON(){now=101;return {value:'synthetic'};}};
 assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{timeoutMs:100},work),{kind:'verification_unavailable'});
 assert.equal(calls,0);
});

test('a delegated predicate aborting synchronously blocks dispatch',async()=>{
 const owner=new AbortController();let calls=0;
 assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{signal:owner.signal,isCurrent:()=>{owner.abort();return true;}}),{kind:'cancelled'});
 assert.equal(calls,0);
});
test('a delegated predicate aborting synchronously blocks final publication',async()=>{
 for(const status of [200,403]){
  const owner=new AbortController();let arm=false;
  const res=response(status===200?receipt():{error:'private',error_id:'access_denied'},status);
  Object.defineProperty(res,'status',{get(){arm=true;return status;}});
  assert.deepEqual(await read(async()=>res,{signal:owner.signal,isCurrent:()=>{if(arm)owner.abort();return true;}}),{kind:'cancelled'});
 }
});
test('rejected initial leases do not traverse command getters or answer toJSON',async()=>{
 for(const mode of ['cancelled','stale','throw'])for(const payload of ['getter','toJSON']){
  const owner=new AbortController();if(mode==='cancelled')owner.abort();let traversals=0,calls=0;
  const work=pending();
  if(payload==='getter')Object.defineProperty(work,'command',{get(){traversals++;return command();}});
  else work.command.answers[C]={toJSON(){traversals++;return {value:'private'};}};
  assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{signal:owner.signal,isCurrent:()=>{if(mode==='throw')throw Error('private');return mode!=='stale';}},work),{kind:mode==='cancelled'?'cancelled':'superseded'});
  assert.equal(traversals,0);assert.equal(calls,0);
 }
});
test('undefined answer entries refuse without dropping input; omitted optional details remain valid',async()=>{
 const work=pending();work.command.answers[OTHER]=undefined;let calls=0;
 assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{},work),{kind:'invalid_request'});
 assert.equal(calls,0);assert.ok(Object.hasOwn(work.command.answers,OTHER));
 for(const answer of [{value:true},{value:true,details:undefined}]){
  const valid=pending();valid.command.answers[C]=answer;
  assert.equal((await read(async(_url,init)=>{assert.deepEqual(JSON.parse(init.body).answers[C],{value:true});return response(receipt());},{},valid)).kind,'committed');
  assert.strictEqual(valid.command.answers[C],answer);
 }
});
test('only HTTP 200 can acknowledge an otherwise valid matching receipt',async()=>{
 for(const status of [201,202])assert.deepEqual(await read(async()=>response(receipt(),status)),{kind:'invalid_response'});
});
test('concurrent operations keep independent cancellation, receipts and late-body disposal',async()=>{
 const first=deferred(),second=deferred(),owner=new AbortController(),seen=[];let discarded=0;
 const request=async(_url,init)=>{const body=JSON.parse(init.body);seen.push(body.operation_id);return body.operation_id===OP?first.promise:second.promise;};
 const a=read(request,{signal:owner.signal}),b=read(request,{},pending({command:command({operation_id:OTHER})}));
 assert.deepEqual(seen,[OP,OTHER]);owner.abort();assert.deepEqual(await a,{kind:'cancelled'});
 second.resolve(response(receipt({operation_id:OTHER})));assert.equal((await b).receipt.operation_id,OTHER);
 first.resolve(new Response(new ReadableStream({cancel(){discarded++;}}),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}));
 await tick();assert.equal(discarded,1);
});
