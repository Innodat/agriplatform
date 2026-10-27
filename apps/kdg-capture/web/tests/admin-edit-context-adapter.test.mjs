import assert from 'node:assert/strict';
import {test} from 'node:test';
import {loadAdminEditContext} from '../../../../compiled/web/src/admin-edit-context.js';
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',O='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',C='cccccccc-cccc-4ccc-8ccc-cccccccccccc',OWNER='dddddddd-dddd-4ddd-8ddd-dddddddddddd',ACTOR='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',EXEC='ffffffff-ffff-4fff-8fff-ffffffffffff';
const Q='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',T='33333333-3333-4333-8333-333333333333';
const pending=(change={})=>({account_id:A,org_id:O,capture_id:C,...change});
const detail=(change={})=>({capture_id:C,org_id:O,owner_account_id:OWNER,owner_actor_id:ACTOR,child_id:Q,child_label:'Original child',questionnaire_id:B,questionnaire_version_id:T,questionnaire_version:'2',revision:'3',observation_date:'2026-10-26',answers:{[Q]:{value:3},[B]:{value:true,details:'Original details'},[T]:{value:'Original answer'}},definition:{schema_version:1,questions:[{id:Q,type:'rating',label:'Original rating',required:true,minimum:1,maximum:5,minimum_label:'Goed',maximum_label:'Nie goed nie'},{id:B,type:'boolean',label:'Original flag',required:true,default:false,details_enabled:true,details_label:'Original details'},{id:T,type:'text',label:'Original text',required:true}]},captured_at:'2026-10-26t10:00:00.123456789z',created_by:ACTOR,created_at:'2026-10-26T11:00:00Z',updated_by:EXEC,updated_at:'2026-10-26T08:00:00Z',...change});
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const context=(capture=detail())=>({capture,editable_fields:['observation_date','answers']});
const response=(value=context(),status=200)=>new Response(JSON.stringify(value),{status,headers});
const read=(request,options={},work=pending(),session={account_id:A,access_token:'synthetic'})=>loadAdminEditContext(session,work,{signal:new AbortController().signal,isCurrent:()=>true,request,timeoutMs:1000,...options});
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return{promise,resolve};};
const frozen=value=>{if(value&&typeof value==='object'){assert.ok(Object.isFrozen(value));for(const child of Object.values(value))frozen(child);}};
test('authorized cross-owner administrator edit context returns one complete immutable original snapshot',async()=>{
 let calls=0;const original=detail();const result=await read(async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/admin/captures/'+C+'/edit-context');
  assert.equal(init.method,'GET');assert.equal(init.body,undefined);assert.equal(init.headers.Authorization,'Bearer synthetic');
  assert.deepEqual(Object.keys(init.headers),['Authorization']);assert.equal(init.credentials,'same-origin');assert.equal(init.mode,'same-origin');assert.equal(init.cache,'no-store');assert.equal(init.redirect,'error');
  return response(context(original));
 });
 assert.equal(result.kind,'loaded');assert.equal(calls,1);assert.deepEqual(result.context.capture,original);frozen(result);
 assert.notEqual(result.context.capture.owner_account_id,A);assert.notEqual(result.context.capture.updated_by,result.context.capture.owner_actor_id);assert.equal(result.context.capture.created_by,ACTOR);
 assert.throws(()=>{result.context.capture.definition.questions[0].label='changed';},TypeError);assert.throws(()=>{result.context.capture.answers[Q].value=5;},TypeError);
 assert.equal(Object.isFrozen(original),false);assert.equal('account_id' in result.context.capture,false);assert.equal('observation' in result.context.capture,false);
});

test('own detail and bigint revision preserve existing DTO semantics and independent statement times',async()=>{
 for(const value of [detail({owner_account_id:A}),detail({revision:'9223372036854775807',questionnaire_version:'9223372036854775807'})]){
  const result=await read(async()=>response(context(value)));assert.equal(result.kind,'loaded');assert.deepEqual(result.context.capture,value);
 }
 const optional=detail();optional.definition.questions[2].required=false;delete optional.answers[T];
 assert.equal((await read(async()=>response(context(optional)))).kind,'loaded');
 const negative=detail();negative.answers[B]={value:false};assert.equal((await read(async()=>response(context(negative)))).kind,'loaded');
});

const malformed={
 foreign_org:{org_id:C},foreign_capture:{capture_id:O},unknown_reader:{account_id:A},unknown_authority:{editable:true},unknown_observation:{observation:{}},
 bad_owner:{owner_account_id:'bad'},bad_owner_actor:{owner_actor_id:'bad'},bad_creator:{created_by:EXEC},bad_executor:{updated_by:'bad'},
 missing_revision:{revision:undefined},revision_zero:{revision:'0'},revision_leading_zero:{revision:'03'},revision_number:{revision:3},revision_overflow:{revision:'9223372036854775808'},
 version_overflow:{questionnaire_version:'9223372036854775808'},bad_child:{child_id:'bad'},bad_questionnaire:{questionnaire_id:'bad'},bad_version_id:{questionnaire_version_id:'bad'},
 empty_child:{child_label:' '},long_child:{child_label:'x'.repeat(201)},bad_date:{observation_date:'2026-02-30'},bad_captured:{captured_at:'2026-10-26T10:00:00+02:00'},
 bad_created:{created_at:'0000-01-01T10:00:00Z'},bad_updated:{updated_at:'2026-10-26T10:60:00Z'},definition_null:{definition:null},answers_null:{answers:null}
};
for(const [name,change] of Object.entries(malformed))test('invalid complete detail '+name,async()=>assert.deepEqual(await read(async()=>response(context(detail(change)))),{kind:'invalid_response'}));

const contentCases={
 schema:d=>{d.definition.schema_version=2;},empty_questions:d=>{d.definition.questions=[];},unknown_definition:d=>{d.definition.extra=1;},
 duplicate_question:d=>{d.definition.questions.push(d.definition.questions[0]);},unknown_question:d=>{d.definition.questions[0].extra=1;},
 invalid_question_id:d=>{d.definition.questions[0].id='bad';},rating_bounds:d=>{d.definition.questions[0].maximum=6;},rating_label:d=>{d.definition.questions[0].minimum_label='Wrong';},
 boolean_default:d=>{d.definition.questions[1].default=true;},boolean_details_label:d=>{delete d.definition.questions[1].details_label;},boolean_disabled_label:d=>{d.definition.questions[1].details_enabled=false;},
 unknown_type:d=>{d.definition.questions[2].type='unknown';},blank_label:d=>{d.definition.questions[2].label=' ';},long_label:d=>{d.definition.questions[2].label='x'.repeat(501);},
 missing_required:d=>{delete d.answers[Q];},foreign_answer:d=>{d.answers[O]={value:3};},answer_extra:d=>{d.answers[Q].extra=1;},rating_fraction:d=>{d.answers[Q].value=1.5;},rating_range:d=>{d.answers[Q].value=6;},
 boolean_type:d=>{d.answers[B].value=1;},false_details:d=>{d.answers[B].value=false;},disabled_details:d=>{d.definition.questions[1].details_enabled=false;d.definition.questions[1].details_label=null;},
 long_details:d=>{d.answers[B].details='x'.repeat(5001);},text_type:d=>{d.answers[T].value=false;},blank_text:d=>{d.answers[T].value=' ';},long_text:d=>{d.answers[T].value='x'.repeat(5001);}
};
for(const [name,change] of Object.entries(contentCases))test('original questionnaire and answers reject '+name,async()=>{const d=detail();change(d);assert.deepEqual(await read(async()=>response(context(d))),{kind:'invalid_response'});});

test('invalid local caller, scope and selectors refuse without dispatch or fallback',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{account_id:OWNER},{account_id:'bad'},{org_id:'bad'},{capture_id:'bad'},{owner_account_id:OWNER},{permission:'kdg_capture.capture.read.all'},{query:{}},{cursor:'x'},{limit:1}])assert.equal((await read(request,{},pending(change))).kind,'invalid_request');
 for(const session of [null,{}, {account_id:'bad',access_token:'synthetic'},{account_id:A,access_token:'bad token'},{account_id:A,access_token:'bad,token'}])assert.equal((await read(request,{},pending(),session)).kind,'authentication_required');
 const bad=Object.defineProperty({},'org_id',{enumerable:true,get(){throw Error('PRIVATE');}});assert.equal((await read(request,{},bad)).kind,'invalid_request');
 assert.equal(calls,0);
});

test('closed options reject invalid values and throwing getters before dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{signal:null},{isCurrent:null},{request:null},{request:'bad'},{timeoutMs:null},{timeoutMs:0},{timeoutMs:-1},{timeoutMs:10001},{timeoutMs:NaN},{timeoutMs:Infinity},{owner_account_id:OWNER}])assert.equal((await read(request,change)).kind,'invalid_request');
 const opts=Object.defineProperty({signal:new AbortController().signal,isCurrent:()=>true},'timeoutMs',{enumerable:true,get(){throw Error('PRIVATE');}});
 assert.deepEqual(await loadAdminEditContext({account_id:A,access_token:'synthetic'},pending(),opts),{kind:'invalid_request'});assert.equal(calls,0);
});

test('strict duplicate-key grammar UTF8 and Unicode failures never yield a partial snapshot',async()=>{
 const raw=JSON.stringify(context());
 for(const body of ['{',raw+'x',raw.replace('"answers":','"\\u0061nswers":{},"answers":'),raw.replace('"value":3','"value":3,"value":3'),raw.replace('"value":3','"value":1e999'),raw.replace('Original child','\\ud800'),raw.replace('Original child','\\u0000'),new Uint8Array([255]),new Uint8Array([0xc3,0x28])])assert.deepEqual(await read(async()=>new Response(body,{headers})),{kind:'invalid_response'});
});

test('actual streamed byte ceiling accepts 544KiB and rejects one extra including error bodies',async()=>{
 for(const [status,value] of [[200,context()],[403,{error:'PRIVATE',error_id:'access_denied'}]])for(const size of [557056,557057]){
  const encoded=new TextEncoder().encode(JSON.stringify(value)),bytes=new Uint8Array(size);bytes.fill(32);bytes.set(encoded);
  const stream=new ReadableStream({start(c){c.enqueue(bytes.subarray(0,200));c.enqueue(bytes.subarray(200));c.close();}});
  const result=await read(async()=>new Response(stream,{status,headers:{...headers,'Content-Length':'1'}}));
  assert.equal(result.kind,size===557057?'invalid_response':status===200?'loaded':'error');
 }
 // Count actual UTF8 bytes rather than characters or a declared length.
 assert.equal((await read(async()=>response({error:'é'.repeat(278529),error_id:'access_denied'},403))).kind,'invalid_response');
});

test('response metadata and redirects are required before publication',async()=>{
 for(const selected of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'},{'Content-Type':'application/json','Cache-Control':'no-store'},{'Content-Type':'application/json','Cache-Control':'private'},{...headers,'Cache-Control':'public, private, no-store'}])assert.deepEqual(await read(async()=>new Response(JSON.stringify(context()),{headers:selected})),{kind:'invalid_response'});
 const redirected=response();Object.defineProperty(redirected,'redirected',{value:true});assert.equal((await read(async()=>redirected)).kind,'invalid_response');
 assert.equal((await read(async()=>new Response(null,{status:204,headers}))).kind,'invalid_response');
 assert.equal((await read(async()=>new Response(JSON.stringify(context()),{headers:{'Content-Type':'Application/JSON; charset=utf-8','Cache-Control':'PRIVATE, NO-STORE'}}))).kind,'loaded');
});

for(const [status,error_id] of [[401,'authentication_required'],[403,'access_denied'],[404,'capture_unavailable'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'capture_read_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe generated error '+status+' '+error_id,async()=>{
 const result=await read(async()=>response({error:'PRIVATE BODY',error_id,code:77},status));assert.deepEqual(result,{kind:'error',status,error_id});frozen(result);
});
test('unknown status identifiers and error metadata return only a safe failure without retries',async()=>{
 for(const [status,value] of [[403,{error:'PRIVATE',error_id:'capture_unavailable'}],[418,{error:'PRIVATE',error_id:'internal_error'}],[503,{error:'PRIVATE',error_id:'unknown'}],[403,{error:'PRIVATE',error_id:'access_denied',extra:'PRIVATE'}],[403,{error:5,error_id:'access_denied'}],[403,{error:'PRIVATE',error_id:'access_denied',code:'5'}]])assert.deepEqual(await read(async()=>response(value,status)),{kind:'invalid_response'});
 let calls=0;assert.deepEqual(await read(async()=>{calls++;throw Error('PRIVATE TOKEN');}),{kind:'verification_unavailable'});assert.equal(calls,1);
});

test('account bearer organization and capture are pinned before the first await',async()=>{
 const held=deferred(),session={account_id:A,access_token:'synthetic'},work=pending();let init;
 const result=read(async(url,options)=>{init=options;assert.equal(url,'/api/v1/admin/captures/'+C+'/edit-context');return held.promise;},{},work,session);
 Object.assign(session,{account_id:OWNER,access_token:'changed'});Object.assign(work,{account_id:OWNER,org_id:C,capture_id:O});
 held.resolve(response());assert.equal((await result).kind,'loaded');assert.equal(init.headers.Authorization,'Bearer synthetic');
});

test('cancelled and superseded fetches discard ignored-abort late bodies with cancellation',async()=>{
 for(const mode of ['cancel','supersede']){
  const held=deferred(),controller=new AbortController();let current=true,calls=0,cancelled=0;
  const result=read(()=>{calls++;return held.promise;},{signal:controller.signal,isCurrent:()=>current,timeoutMs:20});
  if(mode==='cancel')controller.abort();else current=false;
  assert.equal((await result).kind,mode==='cancel'?'cancelled':'superseded');
  held.resolve(new Response(new ReadableStream({cancel(){cancelled++;}}),{headers}));
  await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,1);assert.equal(calls,1);
 }
});

test('one original deadline bounds ignored fetch and stalled body and cancels owned streams',async()=>{
 const held=deferred();let cancelled=0;const started=performance.now();
 assert.deepEqual(await read(()=>held.promise,{timeoutMs:10}),{kind:'verification_unavailable'});assert.ok(performance.now()-started<500);
 held.resolve(new Response(new ReadableStream({cancel(){cancelled++;}}),{headers}));await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,1);
 let bodyCancelled=0;const stream=new ReadableStream({pull(){return new Promise(()=>{});},cancel(){bodyCancelled++;}});
 assert.equal((await read(async()=>new Response(stream,{headers}),{timeoutMs:10})).kind,'verification_unavailable');assert.equal(bodyCancelled,1);
});

test('partial body cancellation supersession and stream errors publish no snapshot',async()=>{
 for(const mode of ['cancel','supersede','error']){
  let current=true,control,cancelled=0;const controller=new AbortController(),started=deferred(),bytes=new TextEncoder().encode(JSON.stringify(context()));
  const stream=new ReadableStream({start(c){control=c;c.enqueue(bytes.subarray(0,100));},pull(){started.resolve();return new Promise(()=>{});},cancel(){cancelled++;}});
  const result=read(async()=>new Response(stream,{headers}),{signal:controller.signal,isCurrent:()=>current,timeoutMs:20});await started.promise;
  if(mode==='cancel')controller.abort();else if(mode==='supersede')current=false;else control.error(Error('PRIVATE'));
  assert.deepEqual(await result,{kind:mode==='cancel'?'cancelled':mode==='supersede'?'superseded':'verification_unavailable'});if(mode!=='error')assert.equal(cancelled,1);
 }
});

test('immediate empty chunks cannot starve the original deadline',async()=>{
 let cancelled=0;const stream=new ReadableStream({pull(c){c.enqueue(new Uint8Array());},cancel(){cancelled++;}});
 assert.deepEqual(await read(async()=>new Response(stream,{headers}),{timeoutMs:5}),{kind:'verification_unavailable'});assert.equal(cancelled,1);
});

test('publication rechecks current generation abort and the original deadline',async()=>{
 for(const mode of ['supersede','cancel','deadline','throw']){
  let calls=0;const controller=new AbortController();
  const result=await read(async()=>response(),{signal:controller.signal,timeoutMs:25,isCurrent:()=>{
   if(++calls===6){if(mode==='supersede')return false;if(mode==='cancel')controller.abort();if(mode==='throw')throw Error('PRIVATE');if(mode==='deadline'){const end=performance.now()+30;while(performance.now()<end){}}}return true;
  }});
  assert.equal(calls,6);assert.deepEqual(result,{kind:mode==='cancel'?'cancelled':mode==='deadline'?'verification_unavailable':'superseded'});
 }
});

test('initial stale cancelled and reentrant predicates refuse without dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 assert.equal((await read(request,{isCurrent:()=>false})).kind,'superseded');assert.equal((await read(request,{isCurrent:()=>{throw Error('PRIVATE');}})).kind,'superseded');
 const cancelled=new AbortController();cancelled.abort();assert.equal((await read(request,{signal:cancelled.signal})).kind,'cancelled');
 const reentrant=new AbortController();assert.equal((await read(request,{signal:reentrant.signal,isCurrent:()=>{reentrant.abort();return true;}})).kind,'cancelled');assert.equal(calls,0);
});

const wrapperCases={
 missing_capture:c=>{delete c.capture;},missing_fields:c=>{delete c.editable_fields;},
 null_capture:c=>{c.capture=null;},array_capture:c=>{c.capture=[];},
 extra_context:c=>{c.extra='PRIVATE';},own_read_observation:c=>{c.read_observation={};},own_edit_observation:c=>{c.edit_observation={};},
 actor_label:c=>{c.actor_label='PRIVATE';},offline_lease:c=>{c.expires_at='2026-10-27T00:00:00Z';},
 wrong_fields_order:c=>{c.editable_fields.reverse();},missing_field:c=>{c.editable_fields.pop();},
 extra_field:c=>{c.editable_fields.push('revision');},fields_object:c=>{c.editable_fields={0:'observation_date',1:'answers'};},
 fields_null:c=>{c.editable_fields=null;},duplicate_fields:c=>{c.editable_fields=['answers','answers'];},
 upper_case_field:c=>{c.editable_fields=['Observation_date','answers'];},impersonation:c=>{c.capture.created_by=EXEC;}
};
for(const [name,change] of Object.entries(wrapperCases))test('closed administrator context rejects '+name,async()=>{
 const c=context();change(c);assert.deepEqual(await read(async()=>response(c)),{kind:'invalid_response'});
});

test('semantic capture ceiling accepts exactly512KiB and rejects one extra beneath the544KiB wire ceiling',async()=>{
 const atSize=size=>{
  const capture=detail();capture.definition.questions=[];capture.answers={};
  for(let i=0;i<40;i++){
   const id=i.toString(16).padStart(8,'0')+'-1111-4111-8111-111111111111';
   capture.definition.questions.push({id,type:'text',label:'Original text',required:true});capture.answers[id]={value:'x'};
  }
  let remaining=size-new TextEncoder().encode(JSON.stringify(capture)).byteLength;
  for(const answer of Object.values(capture.answers)){
   const extra=Math.min(remaining,19999),bytes=extra+1;
   answer.value='😀'.repeat(Math.floor(bytes/4))+'x'.repeat(bytes%4);remaining-=extra;
  }
  assert.equal(remaining,0);assert.equal(new TextEncoder().encode(JSON.stringify(capture)).byteLength,size);return capture;
 };
 for(const size of [524288,524289]){
  const c=context(atSize(size));assert.ok(new TextEncoder().encode(JSON.stringify(c)).byteLength<557056);
  const result=await read(async()=>response(c));assert.equal(result.kind,size===524288?'loaded':'invalid_response');if(result.kind==='loaded')frozen(result);
 }
});

test('context and capture duplicate escaped keys are rejected before any publication',async()=>{
 const raw=JSON.stringify(context());
 for(const body of [raw.replace('"capture":','"\\u0063apture":{},"capture":'),raw.replace('"editable_fields":','"editable_fields":[],"editable_fields":'),raw.replace('"owner_account_id":','"owner_account_id":"'+OWNER+'","owner_account_id":')]){
  assert.deepEqual(await read(async()=>new Response(body,{headers})),{kind:'invalid_response'});
 }
});

test('successful context preserves exact editable order and freezes its wrapper and tuple',async()=>{
 const c=context(),result=await read(async()=>response(c));assert.equal(result.kind,'loaded');assert.deepEqual(result.context,c);frozen(result);
 assert.throws(()=>{result.context.editable_fields.reverse();},TypeError);assert.throws(()=>{result.context.capture={};},TypeError);
 assert.equal(Object.isFrozen(c),false);assert.equal(Object.isFrozen(c.capture),false);
});
