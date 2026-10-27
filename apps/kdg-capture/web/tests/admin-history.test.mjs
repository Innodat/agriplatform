import assert from 'node:assert/strict';
import {test} from 'node:test';
import {adminHistoryCaptures} from '../../../../compiled/web/src/admin-history.js';
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',O='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',C='cccccccc-cccc-4ccc-8ccc-cccccccccccc',OWNER='dddddddd-dddd-4ddd-8ddd-dddddddddddd',ACTOR='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',EXEC='ffffffff-ffff-4fff-8fff-ffffffffffff';
const Q='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',T='33333333-3333-4333-8333-333333333333';
const pending=(change={})=>({account_id:A,org_id:O,from_date:'2026-10-01',to_date:'2026-10-27',...change});
const detail=(change={})=>({capture_id:C,org_id:O,owner_account_id:OWNER,owner_actor_id:ACTOR,child_id:Q,child_label:'Original child',questionnaire_id:B,questionnaire_version_id:T,questionnaire_version:'2',revision:'3',observation_date:'2026-10-26',answers:{[Q]:{value:3},[B]:{value:true,details:'Original details'},[T]:{value:'Original answer'}},definition:{schema_version:1,questions:[{id:Q,type:'rating',label:'Original rating',required:true,minimum:1,maximum:5,minimum_label:'Goed',maximum_label:'Nie goed nie'},{id:B,type:'boolean',label:'Original flag',required:true,default:false,details_enabled:true,details_label:'Original details'},{id:T,type:'text',label:'Original text',required:true}]},captured_at:'2026-10-26t10:00:00.123456789z',created_by:ACTOR,created_at:'2026-10-26T11:00:00Z',updated_by:EXEC,updated_at:'2026-10-26T08:00:00Z',...change});
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const page=(items=[detail()],change={})=>({account_id:A,org_id:O,from_date:'2026-10-01',to_date:'2026-10-27',limit:30,items,next_cursor:null,...change});
const response=(value=page(),status=200)=>new Response(JSON.stringify(value),{status,headers});
const read=(request,options={},work=pending(),session={account_id:A,access_token:'synthetic'})=>adminHistoryCaptures(session,work,{signal:new AbortController().signal,isCurrent:()=>true,request,timeoutMs:1000,...options});
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return{promise,resolve};};
const frozen=value=>{if(value&&typeof value==='object'){assert.ok(Object.isFrozen(value));for(const child of Object.values(value))frozen(child);}};
const encode=value=>Buffer.from(JSON.stringify(Object.fromEntries(Object.keys(value).sort().map(key=>[key,value[key]])))).toString('base64url');
const cursor=(last=detail(),change={})=>encode({v:1,account_id:A,org_id:O,permission:'kdg_capture.capture.read.all',from_date:'2026-10-01',to_date:'2026-10-27',limit:30,last_created_at:last.created_at,last_id:last.capture_id,...change});
test('authorized cross-owner administrator pagination returns complete immutable original pages',async()=>{
 const first=detail({capture_id:EXEC,observation_date:'2026-10-27'}),second=detail({owner_account_id:A,owner_actor_id:Q,created_by:Q,observation_date:'2026-10-01'}),third=detail({capture_id:B,created_at:'2026-10-26T10:59:59.999999Z'});
 const pages=[page([first,second],{next_cursor:cursor(second)}),page([third])];let calls=0;
 for(const [index,value] of pages.entries()){
  const work=pending(index?{cursor:pages[0].next_cursor}:{});
  const result=await read(async(url,init)=>{
   calls++;const query=new URLSearchParams({from_date:work.from_date,to_date:work.to_date,limit:'30',...(index?{cursor:work.cursor}:{})});
   assert.equal(url,'/api/v1/admin/captures?'+query);assert.equal(init.method,'GET');assert.equal(init.body,undefined);
   assert.deepEqual(init.headers,{Authorization:'Bearer synthetic'});assert.equal(init.credentials,'same-origin');assert.equal(init.mode,'same-origin');assert.equal(init.cache,'no-store');assert.equal(init.redirect,'error');
   return response(value);
  },{},work);
  assert.equal(result.kind,'loaded');assert.deepEqual(result.page,value);frozen(result);
  assert.equal('observation' in result.page,false);assert.equal('editable' in result.page,false);assert.equal(Object.isFrozen(value),false);
  assert.throws(()=>{result.page.items[0].answers[Q].value=5;},TypeError);
 }
 assert.equal(calls,2);assert.notEqual(pages[0].items[0].owner_account_id,A);assert.notEqual(pages[0].items[0].updated_by,pages[0].items[0].owner_actor_id);
});

const malformed={
 foreign_org:{org_id:C},bad_capture:{capture_id:'bad'},unknown_reader:{account_id:A},unknown_authority:{editable:true},unknown_observation:{observation:{}},
 bad_owner:{owner_account_id:'bad'},bad_owner_actor:{owner_actor_id:'bad'},bad_creator:{created_by:EXEC},bad_executor:{updated_by:'bad'},
 missing_revision:{revision:undefined},revision_zero:{revision:'0'},revision_leading_zero:{revision:'03'},revision_number:{revision:3},revision_overflow:{revision:'9223372036854775808'},
 version_overflow:{questionnaire_version:'9223372036854775808'},bad_child:{child_id:'bad'},bad_questionnaire:{questionnaire_id:'bad'},bad_version_id:{questionnaire_version_id:'bad'},
 empty_child:{child_label:' '},long_child:{child_label:'x'.repeat(201)},bad_date:{observation_date:'2026-02-30'},bad_captured:{captured_at:'2026-10-26T10:00:00+02:00'},
 bad_created:{created_at:'0000-01-01T10:00:00Z'},bad_updated:{updated_at:'2026-10-26T10:60:00Z'},definition_null:{definition:null},answers_null:{answers:null}
};
for(const [name,change] of Object.entries(malformed))test('invalid complete detail '+name,async()=>assert.deepEqual(await read(async()=>response(page([detail(change)]))),{kind:'invalid_response'}));

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
for(const [name,change] of Object.entries(contentCases))test('original questionnaire and answers reject '+name,async()=>{const d=detail();change(d);assert.deepEqual(await read(async()=>response(page([d]))),{kind:'invalid_response'});});

test('invalid local caller, scope and selectors refuse without dispatch or fallback',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{account_id:OWNER},{account_id:'bad'},{org_id:'bad'},{from_date:'bad'},{owner_account_id:OWNER},{permission:'kdg_capture.capture.read.all'},{query:{}},{cursor:'x'},{limit:0},{capture_id:C}])assert.equal((await read(request,{},pending(change))).kind,'invalid_request');
 for(const session of [null,{}, {account_id:'bad',access_token:'synthetic'},{account_id:A,access_token:'bad token'},{account_id:A,access_token:'bad,token'}])assert.equal((await read(request,{},pending(),session)).kind,'authentication_required');
 const bad=Object.defineProperty({},'org_id',{enumerable:true,get(){throw Error('PRIVATE');}});assert.equal((await read(request,{},bad)).kind,'invalid_request');
 assert.equal(calls,0);
});

test('closed options reject invalid values and throwing getters before dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{signal:null},{isCurrent:null},{request:null},{request:'bad'},{timeoutMs:null},{timeoutMs:0},{timeoutMs:-1},{timeoutMs:10001},{timeoutMs:NaN},{timeoutMs:Infinity},{owner_account_id:OWNER}])assert.equal((await read(request,change)).kind,'invalid_request');
 const opts=Object.defineProperty({signal:new AbortController().signal,isCurrent:()=>true},'timeoutMs',{enumerable:true,get(){throw Error('PRIVATE');}});
 assert.deepEqual(await adminHistoryCaptures({account_id:A,access_token:'synthetic'},pending(),opts),{kind:'invalid_request'});assert.equal(calls,0);
});

test('strict duplicate-key grammar UTF8 and Unicode failures never yield a partial snapshot',async()=>{
 const raw=JSON.stringify(page());
 for(const body of ['{',raw+'x',raw.replace('"answers":','"\\u0061nswers":{},"answers":'),raw.replace('"value":3','"value":3,"value":3'),raw.replace('"value":3','"value":1e999'),raw.replace('Original child','\\ud800'),raw.replace('Original child','\\u0000'),new Uint8Array([255]),new Uint8Array([0xc3,0x28])])assert.deepEqual(await read(async()=>new Response(body,{headers})),{kind:'invalid_response'});
});

test('actual streamed page ceiling accepts 2MiB and rejects one extra including error bodies',async()=>{
 for(const [status,value] of [[200,page()],[403,{error:'PRIVATE',error_id:'access_denied'}]])for(const size of [2097152,2097153]){
  const encoded=new TextEncoder().encode(JSON.stringify(value)),bytes=new Uint8Array(size);bytes.fill(32);bytes.set(encoded);
  const stream=new ReadableStream({start(c){c.enqueue(bytes.subarray(0,200));c.enqueue(bytes.subarray(200));c.close();}});
  const result=await read(async()=>new Response(stream,{status,headers:{...headers,'Content-Length':'1'}}));
  assert.equal(result.kind,size===2097153?'invalid_response':status===200?'loaded':'error');
 }
 // Count actual UTF8 bytes rather than characters or a declared length.
 assert.equal((await read(async()=>response({error:'é'.repeat(1048577),error_id:'access_denied'},403))).kind,'invalid_response');
});

test('response metadata and redirects are required before publication',async()=>{
 for(const selected of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'},{'Content-Type':'application/json','Cache-Control':'no-store'},{'Content-Type':'application/json','Cache-Control':'private'},{...headers,'Cache-Control':'public, private, no-store'}])assert.deepEqual(await read(async()=>new Response(JSON.stringify(page()),{headers:selected})),{kind:'invalid_response'});
 const redirected=response();Object.defineProperty(redirected,'redirected',{value:true});assert.equal((await read(async()=>redirected)).kind,'invalid_response');
 assert.equal((await read(async()=>new Response(null,{status:204,headers}))).kind,'invalid_response');
 assert.equal((await read(async()=>new Response(JSON.stringify(page()),{headers:{'Content-Type':'Application/JSON; charset=utf-8','Cache-Control':'PRIVATE, NO-STORE'}}))).kind,'loaded');
});

for(const [status,error_id] of [[401,'authentication_required'],[403,'access_denied'],[404,'capture_unavailable'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[500,'invalid_write_context'],[503,'authorization_unavailable'],[503,'capture_read_unavailable'],[503,'authorization_observation_expired'],[503,'execution_timeout']])test('safe generated error '+status+' '+error_id,async()=>{
 const result=await read(async()=>response({error:'PRIVATE BODY',error_id,code:77},status));assert.deepEqual(result,{kind:'error',status,error_id});frozen(result);
});
test('unknown status identifiers and error metadata return only a safe failure without retries',async()=>{
 for(const [status,value] of [[403,{error:'PRIVATE',error_id:'capture_unavailable'}],[418,{error:'PRIVATE',error_id:'internal_error'}],[503,{error:'PRIVATE',error_id:'unknown'}],[403,{error:'PRIVATE',error_id:'access_denied',extra:'PRIVATE'}],[403,{error:5,error_id:'access_denied'}],[403,{error:'PRIVATE',error_id:'access_denied',code:'5'}]])assert.deepEqual(await read(async()=>response(value,status)),{kind:'invalid_response'});
 let calls=0;assert.deepEqual(await read(async()=>{calls++;throw Error('PRIVATE TOKEN');}),{kind:'verification_unavailable'});assert.equal(calls,1);
});

test('account bearer organization dates limit and cursor are pinned before the first await',async()=>{
 const held=deferred(),session={account_id:A,access_token:'synthetic'},work=pending({limit:1,cursor:cursor(detail({capture_id:EXEC}),{limit:1})});let init;
 const result=read(async(url,options)=>{init=options;const query=new URL(url,'http://localhost').searchParams;assert.equal(query.get('cursor'),work.cursor);assert.equal(query.get('limit'),'1');return held.promise;},{},work,session);
 Object.assign(session,{account_id:OWNER,access_token:'changed'});Object.assign(work,{account_id:OWNER,org_id:C,from_date:'2026-01-01',to_date:'2026-01-02',limit:100,cursor:'changed'});
 held.resolve(response(page([detail()],{limit:1})));assert.equal((await result).kind,'loaded');assert.equal(init.headers.Authorization,'Bearer synthetic');
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
  let current=true,control,cancelled=0;const controller=new AbortController(),started=deferred(),bytes=new TextEncoder().encode(JSON.stringify(page()));
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

test('terminal empty pages and optional content preserve owner semantics',async()=>{
 for(const work of [pending(),pending({cursor:cursor()})]){
  const result=await read(async()=>response(page([])),{},work);assert.deepEqual(result,{kind:'loaded',page:page([])});frozen(result);
 }
 for(const value of [detail({owner_account_id:A}),detail({revision:'9223372036854775807',questionnaire_version:'9223372036854775807'})]){
  const result=await read(async()=>response(page([value])));assert.equal(result.kind,'loaded');assert.deepEqual(result.page.items[0],value);
 }
 const optional=detail();optional.definition.questions[2].required=false;delete optional.answers[T];optional.answers[B]={value:false};
 assert.equal((await read(async()=>response(page([optional])))).kind,'loaded');
});

for(const [name,change] of Object.entries({foreign_reader:{account_id:OWNER},foreign_org:{org_id:C},foreign_from:{from_date:'2026-09-01'},foreign_to:{to_date:'2026-11-01'},foreign_limit:{limit:1},bad_items:{items:{}},extra_observation:{observation:{}},missing_next:{next_cursor:undefined},bad_next:{next_cursor:7},extra_permission:{permission:'kdg_capture.capture.read.all'}}))test('closed page echo '+name,async()=>assert.deepEqual(await read(async()=>response(page([detail()],change))),{kind:'invalid_response'}));

test('page item uniqueness ordering inclusive bounds and request position are enforced atomically',async()=>{
 const value=detail(),earlier=detail({capture_id:B,created_at:'2026-10-26T10:59:59.999999Z'}),later=detail({capture_id:EXEC});
 for(const items of [[value,value],[value,detail({created_at:'2026-10-26T10:59:59Z'})],[value,later],[earlier,value],[detail({observation_date:'2026-09-30'})],[detail({observation_date:'2026-10-28'})],[null],[[]]])assert.deepEqual(await read(async()=>response(page(items))),{kind:'invalid_response'});
 assert.equal((await read(async()=>response(page([value])),{},pending({cursor:cursor()}))).kind,'invalid_response');
 assert.equal((await read(async()=>response(page([later])),{},pending({cursor:cursor()}))).kind,'invalid_response');
 assert.equal((await read(async()=>response(page([earlier])),{},pending({cursor:cursor()}))).kind,'loaded');
 assert.equal((await read(async()=>response(page([value,earlier],{limit:1})),{},pending({limit:1}))).kind,'invalid_response');
});

test('microsecond order retains precision and canonical UTC position spelling',async()=>{
 const first=detail({capture_id:B,created_at:'2026-10-26T11:00:00.000002Z'}),second=detail({capture_id:EXEC,created_at:'2026-10-26T11:00:00.000001Z'}),third=detail({capture_id:C});
 assert.equal((await read(async()=>response(page([first,second,third],{next_cursor:cursor(third)})))).kind,'loaded');
 assert.equal((await read(async()=>response(page([second,first])))).kind,'invalid_response');
 for(const created_at of ['2026-10-26T11:00:00.000000Z','2026-10-26T11:00:00.001Z','2026-10-26t11:00:00z','2026-10-26T11:00:00+00:00','2026-10-26T11:00:00.1234567Z','2026-10-26T11:00:00Z\n'])assert.equal((await read(async()=>response(page([detail({created_at})])))).kind,'invalid_response');
});

test('continuation is the last included row even for a short byte-limited page',async()=>{
 const value=detail(),next=cursor(value);
 assert.equal((await read(async()=>response(page([value],{next_cursor:next})))).kind,'loaded');
 for(const selected of [cursor(detail({capture_id:B})),cursor(detail({created_at:'2026-10-26T11:00:00.000001Z'})),cursor(value,{permission:'kdg_capture.capture.read.own'}),cursor(value,{account_id:OWNER}),cursor(value,{limit:1}),cursor(value,{extra:true})])assert.deepEqual(await read(async()=>response(page([value],{next_cursor:selected}))),{kind:'invalid_response'});
 assert.equal((await read(async()=>response(page([],{next_cursor:next})))).kind,'invalid_response');
});

const badCursors={
 own:cursor(detail(),{permission:'kdg_capture.capture.read.own'}),reader:cursor(detail(),{account_id:OWNER}),org:cursor(detail(),{org_id:C}),from:cursor(detail(),{from_date:'2026-09-01'}),to:cursor(detail(),{to_date:'2026-11-01'}),limit:cursor(detail(),{limit:1}),
 version:cursor(detail(),{v:2}),bool_version:cursor(detail(),{v:true}),extra:cursor(detail(),{extra:1}),bad_id:cursor(detail(),{last_id:'bad'}),missing_position:cursor(detail(),{last_id:undefined}),
 fraction:cursor(detail(),{last_created_at:'2026-10-26T11:00:00.001Z'}),zero_fraction:cursor(detail(),{last_created_at:'2026-10-26T11:00:00.000000Z'}),offset:cursor(detail(),{last_created_at:'2026-10-26T11:00:00+00:00'}),
 bad_day:cursor(detail(),{last_created_at:'2026-02-30T11:00:00Z'}),bad_hour:cursor(detail(),{last_created_at:'2026-10-26T24:00:00Z'}),bad_second:cursor(detail(),{last_created_at:'2026-10-26T11:00:60Z'}),padding:cursor()+'=',empty:'',overlong:'x'.repeat(2049),invalid_base64:'a',not_json:'eA',null: null,undefined:undefined
};
const cursorText=Buffer.from(cursor(),'base64url').toString();
badCursors.duplicate=Buffer.from(cursorText.replace('"v":1','"v":1,"v":1')).toString('base64url');
badCursors.whitespace=Buffer.from(' '+cursorText).toString('base64url');
badCursors.key_order=Buffer.from(JSON.stringify({v:1,...JSON.parse(cursorText)})).toString('base64url');
badCursors.escaped_key=Buffer.from(cursorText.replace('"v"','"\\u0076"')).toString('base64url');
for(const [name,selected] of Object.entries(badCursors))test('local cursor refuses '+name+' before dispatch',async()=>{
 let calls=0;assert.deepEqual(await read(async()=>{calls++;return response();},{},pending({cursor:selected})),{kind:'invalid_request'});assert.equal(calls,0);
});

test('local dates and page limits are explicit closed valid bounds',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{from_date:'2026-02-30'},{from_date:'0000-01-01'},{from_date:'2026-10-28'},{to_date:'2026-09-30'},{from_date:undefined},{to_date:undefined},{limit:undefined},{limit:null},{limit:0},{limit:101},{limit:1.5},{limit:'30'},{limit:NaN}])assert.deepEqual(await read(request,{},pending(change)),{kind:'invalid_request'});
 assert.equal(calls,0);
 for(const limit of [1,100])assert.equal((await read(async()=>response(page([],{limit})),{},pending({limit}))).kind,'loaded');
 assert.equal((await read(async()=>response(page([],{from_date:'2026-10-27',to_date:'2026-10-27'})),{},pending({from_date:'2026-10-27',to_date:'2026-10-27'}))).kind,'loaded');
});

function sizedDetail(size){
 const value=detail({definition:{schema_version:1,questions:[]},answers:{}});
 for(let n=1;n<=50;n++){
  const q='12345678-1234-4234-8234-'+String(n).padStart(12,'0');
  value.definition.questions.push({id:q,type:'text',label:'Original text',required:true});value.answers[q]={value:'x'};
 }
 let remaining=size-new TextEncoder().encode(JSON.stringify(value)).byteLength;
 for(const answer of Object.values(value.answers)){
  // Replace a one-byte x by Unicode content while staying below 5,000 code points.
  const increase=Math.min(remaining,19996),bytes=increase+1,emoji=Math.floor(bytes/4),ascii=bytes%4;
  answer.value='🙂'.repeat(emoji)+'x'.repeat(ascii);remaining-=increase;if(!remaining)break;
 }
 assert.equal(remaining,0);assert.equal(new TextEncoder().encode(JSON.stringify(value)).byteLength,size);return value;
}
test('semantic per-detail 512KiB limit remains independent of the 2MiB page ceiling',async()=>{
 for(const size of [524288,524289]){
  const value=sizedDetail(size);assert.ok(new TextEncoder().encode(JSON.stringify(page([value]))).byteLength<2097152);
  assert.equal((await read(async()=>response(page([value])))).kind,size===524288?'loaded':'invalid_response');
 }
});
