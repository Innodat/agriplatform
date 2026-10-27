import assert from 'node:assert/strict';
import {test} from 'node:test';
import {recoverAdminEdit} from '../../../../compiled/web/src/admin-recovery.js';
const A='11111111-1111-4111-8111-111111111111',O='22222222-2222-4222-8222-222222222222',
 OP='33333333-3333-4333-8333-333333333333',C='44444444-4444-4444-8444-444444444444',OTHER='55555555-5555-4555-8555-555555555555';
const session=()=>({account_id:A,access_token:'synthetic-token'});
const pending=(changes={})=>({account_id:A,org_id:O,operation_id:OP,capture_id:C,command_type:'capture.edit',...changes});
const receipt=(changes={})=>({operation_id:OP,command_type:'capture.edit',command_version:1,status:'committed',result:{capture_id:C,revision:'9223372036854775807'},...changes});
const unresolved=(changes={})=>({operation_id:OP,command_type:'capture.edit',status:'unresolved',...changes});
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
const lease=()=>({signal:new AbortController().signal,isCurrent:()=>true});
const read=(request,options={},work=pending(),auth=session())=>recoverAdminEdit(auth,work,{...lease(),request,timeoutMs:1000,...options});
const tick=()=>new Promise(r=>setTimeout(r,0));
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};

// Synthetic request/stream cases exercise only this inert request boundary.
// Current read.all, executor privacy and stored-target authority stay server-owned.

test('administrator explicit GET returns matching immutable original edit receipt',async()=>{
 let calls=0;
 const result=await read(async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/admin/operations/'+OP+'?command_type=capture.edit');
  assert.equal(init.method,'GET');assert.equal(init.headers.Authorization,'Bearer synthetic-token');
  for(const [key,value] of Object.entries({credentials:'same-origin',mode:'same-origin',cache:'no-store',redirect:'error'}))assert.equal(init[key],value);
  assert.deepEqual(Object.keys(init.headers),['Authorization']);assert.equal(init.body,undefined);return response(receipt());
 });
 assert.equal(result.kind,'committed');assert.equal(calls,1);assert.deepEqual(result.receipt,receipt());
 assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.receipt));assert.ok(Object.isFrozen(result.receipt.result));
});

test('wrong status families, extra error fields and legacy payloads never imply absence',async()=>{
 for(const [status,body] of [[403,{error:'x',error_id:'internal_error'}],[503,{error:'x',error_id:'raw_exception'}],[503,{error:'x',error_id:'execution_timeout',detail:'SENSITIVE'}],[401,{detail:{code:'authentication_required'}}],[201,unresolved()]])assert.deepEqual(await read(async()=>response(body,status)),{kind:'invalid_response'});
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
test('all generated status/id variants are mapped without upstream messages',async()=>{
 const {readFileSync}=await import('node:fs');
 const schema=JSON.parse(readFileSync(new URL('../../write-candidate/admin-edit-openapi.json',import.meta.url),'utf8'));
 const deref=s=>s.$ref?schema.components.schemas[s.$ref.split('/').at(-1)]:s;
 for(const [status,definition] of Object.entries(schema.paths['/api/v1/admin/operations/{operation_id}'].get.responses)){
  if(status==='200')continue;
  const body=deref(definition.content['application/json'].schema);
  for(const variant of body.oneOf??[body]){
   const model=deref(variant);
   for(const error_id of model.properties.error_id.const?[model.properties.error_id.const]:model.properties.error_id.enum){
   const extra={};
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
test('only HTTP 200 can acknowledge an otherwise valid matching receipt',async()=>{
 for(const status of [201,202])assert.deepEqual(await read(async()=>response(receipt(),status)),{kind:'invalid_response'});
});
test('closed options reject selectors and invalid explicit values before dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 for(const option of [{owner_account_id:OTHER},{org_id:O},{permission:'kdg_capture.capture.edit.all'},{timeoutMs:null},{request:null},{isCurrent:()=>1}]){
  const result=await read(request,option);assert.equal(result.kind,Object.hasOwn(option,'isCurrent')?'superseded':'invalid_request');
 }
 assert.equal(calls,0);
});
test('exact generated integer code and cache requirements cover success and errors',async()=>{
 for(const code of [1.5,'1',{},true])assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id:'access_denied',code},403)),{kind:'invalid_response'});
 for(const code of [null,0,-1])assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id:'access_denied',code},403)),{kind:'error',status:403,error_id:'access_denied'});
 for(const status of [200,403])for(const cache of ['public, private, no-store','private','no-store']){
  const value=status===200?receipt():{error:'SENSITIVE',error_id:'access_denied'};
  assert.deepEqual(await read(async()=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':cache}})),{kind:'invalid_response'});
 }
});
test('preflight option access and final validation share the original total deadline',async t=>{
 let now=0,calls=0;t.mock.method(performance,'now',()=>now);
 const options={...lease(),request:async()=>{calls++;return response(receipt());}};
 Object.defineProperty(options,'timeoutMs',{get(){now=11;return 10;},enumerable:true});
 assert.deepEqual(await recoverAdminEdit(session(),pending(),options),{kind:'verification_unavailable'});assert.equal(calls,0);
 now=0;const res=response(receipt());Object.defineProperty(res,'status',{get(){now=11;return 200;}});
 assert.deepEqual(await read(async()=>res,{timeoutMs:10}),{kind:'verification_unavailable'});
});
test('best-effort cancellation cannot replace a safe result when transport cancellation throws',async()=>{
 const res=response(receipt());Object.defineProperty(res,'body',{value:{cancel(){throw Error('SENSITIVE');}}});
 assert.deepEqual(await read(async()=>res),{kind:'verification_unavailable'});
 const late=deferred();assert.deepEqual(await read(()=>late.promise,{timeoutMs:5}),{kind:'verification_unavailable'});
 late.resolve(res);await tick();
});

for(const [name,change] of Object.entries({wrong_operation:{operation_id:OTHER},wrong_command:{command_type:'capture.create'},wrong_status:{status:'saved'},version:{command_version:2},string_version:{command_version:'1'},missing_status:{status:undefined},missing_result:{result:undefined},extra:{private:'canary'},numeric_revision:{result:{capture_id:C,revision:1}},zero:{result:{capture_id:C,revision:'0'}},negative:{result:{capture_id:C,revision:'-1'}},overflow:{result:{capture_id:C,revision:'9223372036854775808'}},leading_zero:{result:{capture_id:C,revision:'01'}},trailing_newline:{result:{capture_id:C,revision:'1\n'}},wrong_target:{result:{capture_id:OTHER,revision:'1'}},nil_target:{result:{capture_id:'00000000-0000-0000-0000-000000000000',revision:'1'}},extra_result:{result:{capture_id:C,revision:'1',answers:'canary'}}}))test('receipt refuses '+name,async()=>{
 assert.deepEqual(await read(async()=>response(receipt(change))),{kind:'invalid_response'});
});
for(const [status,id] of [[401,'authentication_required'],[403,'access_denied'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'operation_verification_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe generated recovery status pair '+status+' '+id,async()=>{
 const result=await read(async()=>response({error:'SENSITIVE bearer',error_id:id},status));
 assert.deepEqual(result,{kind:'error',status,error_id:id});assert.ok(Object.isFrozen(result));assert.ok(!JSON.stringify(result).includes('SENSITIVE'));
});
test('unresolved preserves exact immutable identity and ambiguous outcome with one GET',async()=>{
 const work=pending(),before=structuredClone(work);let calls=0;
 const result=await read(async(url,init)=>{calls++;assert.equal(url,'/api/v1/admin/operations/'+OP+'?command_type=capture.edit');assert.equal(init.method,'GET');assert.equal(init.body,undefined);return response(unresolved());},{},work);
 assert.deepEqual(result,{kind:'unresolved',outcome:unresolved()});assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.outcome));
 assert.equal(calls,1);assert.deepEqual(work,before);assert.equal(Object.isFrozen(work),false);
 assert.deepEqual(Object.keys(result.outcome).sort(),['command_type','operation_id','status']);
});
test('unresolved refuses missing, mismatched, receipt, snapshot and authority/provenance fields',async()=>{
 for(const change of [{operation_id:OTHER},{command_type:'capture.create'},{status:undefined},{command_version:1},{result:{capture_id:C,revision:'1'}},{capture_id:C},{capture:{}},{proposal:{}},{owner_account_id:OTHER},{surface:'admin'},{actor_label:'SENSITIVE'},{absent:true}]){
  assert.deepEqual(await read(async()=>response(unresolved(change))),{kind:'invalid_response'});
 }
 for(const body of [null,[],{},'unresolved',1])assert.deepEqual(await read(async()=>response(body)),{kind:'invalid_response'});
});
test('read-only recovery needs no local edit grant, owner or proposal and never falls back to own',async()=>{
 for(const reply of [receipt(),unresolved(),{error:'edit grant removed',error_id:'access_denied'}]){
  let calls=0;const work=pending(),before=structuredClone(work);
  const result=await read(async(url,init)=>{calls++;assert.equal(url,'/api/v1/admin/operations/'+OP+'?command_type=capture.edit');assert.equal(init.method,'GET');assert.equal(init.body,undefined);return response(reply,reply.error_id?403:200);},{},work);
  assert.equal(calls,1);assert.deepEqual(work,before);assert.ok(['committed','unresolved','error'].includes(result.kind));
 }
});
test('recovery errors refuse write/read-only families, wrong status, raw fields and conflict metadata',async()=>{
 for(const [status,error_id] of [[404,'capture_unavailable'],[409,'operation_busy'],[409,'questionnaire_version_unavailable'],[409,'kdg_capture.capture_revision_conflict'],[422,'unsupported_command_version'],[503,'capture_read_unavailable'],[403,'authentication_required'],[500,'operation_verification_unavailable']])assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id},status)),{kind:'invalid_response'});
 for(const extra of [{current_revision:'1'},{receipt:receipt()},{body:'SENSITIVE'},{exception:'SENSITIVE'},{bearer:'SENSITIVE'},{owner_account_id:OTHER}])assert.deepEqual(await read(async()=>response({error:'SENSITIVE',error_id:'access_denied',...extra},403)),{kind:'invalid_response'});
});
test('invalid closed pending identity/type/selectors and options refuse before any dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response(receipt());};
 for(const work of [null,undefined,[],{},pending({account_id:OTHER}),pending({command_type:'capture.create'}),pending({command_type:undefined}),pending({capture_id:undefined}),pending({operation_id:undefined}),pending({target_id:C}),pending({owner_account_id:OTHER}),pending({permission:'kdg_capture.capture.read.all'}),pending({query:{command_type:'capture.edit'}}),pending({body:{}})]){
  // Explicit undefined here intentionally bypasses read()'s default argument.
  const result=await recoverAdminEdit(session(),work,{...lease(),request});assert.deepEqual(result,{kind:'invalid_request'});
 }
 for(const key of ['org_id','operation_id','capture_id'])for(const value of ['00000000-0000-0000-0000-000000000000','ABCDEFAB-1111-4111-8111-111111111111',C+'\n',C+'x','',1])assert.deepEqual(await read(request,{},pending({[key]:value})),{kind:'invalid_request'});
 for(const options of [{timeoutMs:0},{timeoutMs:-1},{timeoutMs:10001},{timeoutMs:NaN},{timeoutMs:Infinity},{signal:undefined},{request:42},{isCurrent:undefined},{capture_id:C},{operation_id:OP},{command_type:'capture.edit'}])assert.deepEqual(await read(request,options),{kind:'invalid_request'});
 for(const auth of [null,{},sessionWith({account_id:OTHER+'x'}),sessionWith({access_token:''}),sessionWith({access_token:'bad,token'}),sessionWith({access_token:'white space'})])assert.deepEqual(await read(request,{},pending(),auth),{kind:'authentication_required'});
 assert.equal(calls,0);
});
function sessionWith(change){return {...session(),...change};}
test('pinned caller/bearer/org/operation/capture/type and options survive caller mutation',async()=>{
 for(const outcome of ['committed','unresolved']){
  const auth=session(),work=pending(),gate=deferred();let call;
  const options={...lease(),timeoutMs:1000,request:async(url,init)=>{call={url,init};return gate.promise;}};
  const result=recoverAdminEdit(auth,work,options);
  Object.assign(auth,{account_id:OTHER,access_token:'replacement'});Object.assign(work,{account_id:OTHER,org_id:OTHER,operation_id:OTHER,capture_id:OTHER,command_type:'capture.create'});
  options.request=()=>{throw Error('must use original transport');};options.isCurrent=()=>false;options.timeoutMs=1;options.signal=new AbortController().signal;
  gate.resolve(response(outcome==='committed'?receipt():unresolved()));const value=await result;assert.equal(value.kind,outcome);
  assert.equal((value.receipt??value.outcome).operation_id,OP);assert.equal(call.url,'/api/v1/admin/operations/'+OP+'?command_type=capture.edit');assert.equal(call.init.headers.Authorization,'Bearer synthetic-token');assert.equal(call.init.body,undefined);
 }
});
test('concurrent original lookups preserve independent cancellation, receipts and unresolved outcomes',async()=>{
 const first=deferred(),second=deferred(),owner=new AbortController(),seen=[];let discarded=0;
 const request=async(url,init)=>{seen.push({url,signal:init.signal});return url.includes(OP)?first.promise:second.promise;};
 const a=read(request,{signal:owner.signal}),b=read(request,{},pending({operation_id:OTHER,capture_id:OTHER}));
 assert.equal(seen.length,2);assert.notEqual(seen[0].signal,seen[1].signal);owner.abort();assert.deepEqual(await a,{kind:'cancelled'});
 second.resolve(response(receipt({operation_id:OTHER,result:{capture_id:OTHER,revision:'1'}})));assert.equal((await b).receipt.operation_id,OTHER);
 first.resolve(new Response(new ReadableStream({cancel(){discarded++;}}),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}));
 await tick();assert.equal(discarded,1);
 const [one,two]=await Promise.all([read(async()=>response(unresolved())),read(async()=>response(unresolved({operation_id:OTHER})),{},pending({operation_id:OTHER}))]);
 assert.equal(one.outcome.operation_id,OP);assert.equal(two.outcome.operation_id,OTHER);
});
test('old and no-op original receipt revisions acknowledge without guessing current state',async()=>{
 for(const revision of ['1','2','7','9223372036854775807']){
  const work=pending(),before=structuredClone(work);let calls=0;
  const result=await read(async(_url,init)=>{calls++;assert.equal(init.method,'GET');assert.equal(init.body,undefined);return response(receipt({result:{capture_id:C,revision}}));},{},work);
  assert.deepEqual(result,{kind:'committed',receipt:receipt({result:{capture_id:C,revision}})});assert.equal(calls,1);assert.deepEqual(work,before);
 }
});
test('all safe outcomes preserve pending input and never retry or invent operation identity',async()=>{
 for(const request of [async()=>response(unresolved()),async()=>response(receipt({operation_id:OTHER})),async()=>response({error:'SENSITIVE',error_id:'access_denied'},403),async()=>{throw Error('SENSITIVE');},()=>new Promise(()=>{})]){
  const work=pending(),before=structuredClone(work);let calls=0;
  const result=await read((...args)=>{calls++;return request(...args);},{timeoutMs:5},work);
  assert.equal(calls,1);assert.deepEqual(work,before);assert.equal(Object.isFrozen(work),false);
  assert.ok(!JSON.stringify(result).includes('SENSITIVE'));assert.equal(Object.hasOwn(result,'synced'),false);assert.equal(Object.hasOwn(result,'rolled_back'),false);
 }
});
test('pre-cancelled/stale/throwing leases refuse before traversing any pending getter',async()=>{
 for(const mode of ['cancelled','stale','throw']){
  const owner=new AbortController();if(mode==='cancelled')owner.abort();let traversals=0,calls=0;const work=pending();
  Object.defineProperty(work,'operation_id',{get(){traversals++;return OP;},enumerable:true});
  assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{signal:owner.signal,isCurrent:()=>{if(mode==='throw')throw Error('SENSITIVE');return mode!=='stale';}},work),{kind:mode==='cancelled'?'cancelled':'superseded'});
  assert.equal(traversals,0);assert.equal(calls,0);
 }
});
test('all success variants share exact status, duplicate-key, UTF8 and streamed byte boundaries',async()=>{
 const encoder=new TextEncoder();
 for(const value of [receipt(),unresolved()]){
  for(const status of [201,202,206])assert.deepEqual(await read(async()=>response(value,status)),{kind:'invalid_response'});
  const raw=JSON.stringify(value);
  for(const size of [16384,16385]){
   const padded=raw+' '.repeat(size-encoder.encode(raw).length);assert.equal(encoder.encode(padded).length,size);
   const result=await read(async()=>new Response(padded,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store','Content-Length':'1'}}));
   assert.equal(result.kind,size===16384?value.status:'invalid_response');
  }
  const dup=raw.replace('"command_type":','"command_\\u0074ype":"capture.create","command_type":');
  assert.deepEqual(await read(async()=>new Response(dup,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})),{kind:'invalid_response'});
 }
});
test('late unresolved or denial cannot publish after abort, deadline or stale generation',async()=>{
 for(const reply of [unresolved(),{error:'SENSITIVE',error_id:'access_denied'}])for(const mode of ['abort','deadline','stale','throw']){
  let current=true,cancelled=0;const gate=deferred(),owner=new AbortController();
  const work=read(()=>gate.promise,{timeoutMs:mode==='deadline'?5:1000,signal:owner.signal,isCurrent:()=>{if(current==='throw')throw Error('SENSITIVE');return current;}});
  if(mode==='abort')owner.abort();else if(mode==='stale')current=false;else if(mode==='throw')current='throw';
  if(mode==='deadline'){assert.deepEqual(await work,{kind:'verification_unavailable'});gate.resolve(new Response(new ReadableStream({cancel(){cancelled++;}})));await tick();assert.equal(cancelled,1);}
  else {gate.resolve(response(reply,reply.error_id?403:200));assert.deepEqual(await work,{kind:mode==='abort'?'cancelled':'superseded'});}
 }
});
test('pinning and publication both enforce the original deadline even for unresolved',async t=>{
 let now=0,calls=0;t.mock.method(performance,'now',()=>now);
 const work=pending();Object.defineProperty(work,'operation_id',{get(){now=11;return OP;},enumerable:true});
 assert.deepEqual(await read(async()=>{calls++;return response(receipt());},{timeoutMs:10},work),{kind:'verification_unavailable'});assert.equal(calls,0);
 now=0;const res=response(unresolved());Object.defineProperty(res,'status',{get(){now=11;return 200;}});
 assert.deepEqual(await read(async()=>res,{timeoutMs:10}),{kind:'verification_unavailable'});
});
test('default fetch and exact ten-second ceiling preserve the same total publication deadline',async t=>{
 let now=0,calls=0,completedAt=9999;t.mock.method(performance,'now',()=>now);
 t.mock.method(globalThis,'fetch',async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/admin/operations/'+OP+'?command_type=capture.edit');assert.equal(init.method,'GET');assert.equal(init.body,undefined);
  const res=response(unresolved());Object.defineProperty(res,'status',{get(){now=completedAt;return 200;}});return res;
 });
 assert.equal((await recoverAdminEdit(session(),pending(),lease())).kind,'unresolved');
 now=0;completedAt=10000;
 assert.deepEqual(await recoverAdminEdit(session(),pending(),{...lease(),timeoutMs:10000}),{kind:'verification_unavailable'});
 assert.equal(calls,2);
});
