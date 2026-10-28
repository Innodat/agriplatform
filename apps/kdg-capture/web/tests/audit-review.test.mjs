import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createAuditReview} from '../../../../compiled/web/src/audit-review.js';
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',O='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',C='cccccccc-cccc-4ccc-8ccc-cccccccccccc',OWNER='dddddddd-dddd-4ddd-8ddd-dddddddddddd',AUTHOR='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',EDITOR='ffffffff-ffff-4fff-8fff-ffffffffffff';
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const value=(name='Original name',outage=false)=>({audit:{account_id:A,org_id:O,capture_id:C,owner_account_id:OWNER,owner_actor_id:AUTHOR,created_by:AUTHOR,created_at:'2026-10-26T10:00:00Z',updated_by:EDITOR,updated_at:'2026-10-26T10:00:00.000001Z',current_revision:'2',limit:2,events:[{revision:'2',command_type:'capture.edit',executor_actor_id:EDITOR,initiator_actor_id:null,recorded_at:'2026-10-26T10:00:00.000001Z'}],next_cursor:null},actor_display:outage?{status:'temporarily_unavailable'}:{status:'loaded',labels:[{actor_id:AUTHOR,status:'resolved',display_name:name},{actor_id:EDITOR,status:'resolved',display_name:'Actual editor'}]}});
const response=(name='Original name',outage=false)=>new Response(JSON.stringify(value(name,outage)),{headers});
const failure=(status=403,error_id='access_denied')=>new Response(JSON.stringify({error:'PRIVATE',error_id}),{status,headers});
const held=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return{promise,resolve};};
const options=(change={})=>({session:{account_id:A,access_token:'synthetic'},pending:{account_id:A,org_id:O,capture_id:C,limit:2},signal:new AbortController().signal,isCurrent:()=>true,request:async()=>response(),timeoutMs:100,...change});
const tick=()=>new Promise(r=>setTimeout(r,0));

test('loaded audit state clears immediately on invalidation and cannot revive',async()=>{
 const review=createAuditReview(options());assert.deepEqual(review.snapshot(),{kind:'idle'});
 const first=await review.load();assert.equal(first.kind,'loaded');assert.equal(first.model.original_capturer.display_name,'Original name');
 assert.equal(review.snapshot(),first);review.invalidate();assert.deepEqual(review.snapshot(),{kind:'locked'});
 assert.deepEqual(await review.load(),{kind:'locked'});assert.deepEqual(await review.retry(),{kind:'locked'});
});

test('explicit retry clears old page before a complete authorized aggregate GET',async()=>{
 let calls=0;const next=held();const review=createAuditReview(options({request:async(url,init)=>{
  calls++;assert.equal(url,'/api/v1/admin/captures/'+C+'/audit-details?limit=2');assert.equal(init.headers.Authorization,'Bearer synthetic');assert.equal(init.cache,'no-store');
  return calls===1?response('Ignored',true):next.promise;
 }}));
 assert.equal((await review.load()).model.names.status,'temporarily_unavailable');assert.equal(calls,1);
 const retry=review.retry();assert.deepEqual(review.snapshot(),{kind:'loading'});assert.equal(calls,2);
 next.resolve(response('Fresh retained name'));assert.equal((await retry).model.original_capturer.display_name,'Fresh retained name');assert.equal(calls,2);
});

test('overlapping loads discard delayed success and safe error from prior read',async()=>{
 for(const oldResponse of [()=>response('Obsolete'),()=>failure()]){
  const old=held(),next=held();let calls=0,oldSignal;
  const review=createAuditReview(options({request:(_url,init)=>{calls++;if(calls===1){oldSignal=init.signal;return old.promise;}return next.promise;}}));
  const first=review.load(),second=review.load();assert.equal(oldSignal.aborted,true);next.resolve(response('Current page'));
  const current=await second;assert.equal(current.kind,'loaded');assert.equal(current.model.original_capturer.display_name,'Current page');
  old.resolve(oldResponse());assert.deepEqual(await first,{kind:'superseded'});await tick();assert.equal(review.snapshot(),current);assert.equal(calls,2);
 }
});

test('external abort clears loaded data and aborts owned pending work',async()=>{
 for(const pending of [false,true]){
  const signal=new AbortController(),wait=held();let calls=0;
  const review=createAuditReview(options({signal:signal.signal,request:()=>{calls++;return pending?wait.promise:Promise.resolve(response());}}));
  const work=review.load();if(!pending)assert.equal((await work).kind,'loaded');signal.abort();
  assert.deepEqual(review.snapshot(),{kind:'locked'});if(pending){wait.resolve(response('Too late'));assert.deepEqual(await work,{kind:'superseded'});}
  assert.deepEqual(await review.retry(),{kind:'locked'});assert.equal(calls,1);
 }
});

for(const scope of ['account','org','capture','page','session','access'])test('changed '+scope+' generation clears already loaded state and fences later reads',async()=>{
 let generation=1,calls=0;const pinned=generation;
 const review=createAuditReview(options({isCurrent:()=>generation===pinned,request:async()=>{calls++;return response();}}));
 assert.equal((await review.load()).kind,'loaded');generation++;
 assert.deepEqual(review.snapshot(),{kind:'locked'});assert.deepEqual(await review.load(),{kind:'locked'});assert.equal(calls,1);
 generation=pinned;assert.deepEqual(await review.retry(),{kind:'locked'},'old generation cannot revive terminal instance');
});

test('changed caller generation during pending success or error exposes no data',async()=>{
 for(const reply of [()=>response(),()=>failure()]){
  const wait=held();let current=true;
  const review=createAuditReview(options({isCurrent:()=>current,request:()=>wait.promise}));const work=review.load();
  current=false;wait.resolve(reply());assert.deepEqual(await work,{kind:'locked'});assert.deepEqual(review.snapshot(),{kind:'locked'});
 }
});

test('close clears loaded data and makes a pending ignored-abort read harmless',async()=>{
 for(const pending of [false,true]){
  const wait=held();let calls=0;const review=createAuditReview(options({request:()=>{calls++;return pending?wait.promise:Promise.resolve(response());}}));
  const work=review.load();if(!pending)assert.equal((await work).kind,'loaded');review.close();review.close();review.invalidate();
  assert.deepEqual(review.snapshot(),{kind:'closed'});assert.deepEqual(await review.load(),{kind:'closed'});
  if(pending){wait.resolve(response('Late'));assert.deepEqual(await work,{kind:'superseded'});}
  assert.equal(calls,1);
 }
});

test('safe denied and unavailable refresh results never retain earlier names or become empty lists',async()=>{
 for(const [status,id] of [[401,'authentication_required'],[403,'access_denied'],[503,'authorization_unavailable'],[503,'capture_read_unavailable']]){
  let calls=0;const review=createAuditReview(options({request:async()=>++calls===1?response():failure(status,id)}));
  assert.equal((await review.load()).kind,'loaded');const result=await review.retry();assert.deepEqual(result,{kind:'error',status,error_id:id});assert.equal(review.snapshot(),result);assert.ok(!Object.hasOwn(result,'model'));assert.equal(calls,2);
 }
});

test('timeout is bounded and no retry occurs until explicitly requested',async()=>{
 const wait=held();let calls=0;const review=createAuditReview(options({timeoutMs:5,request:async()=>++calls===1?wait.promise:response('Retry')}));
 assert.deepEqual(await review.load(),{kind:'verification_unavailable'});assert.equal(calls,1);wait.resolve(response('Stale'));await tick();assert.deepEqual(review.snapshot(),{kind:'verification_unavailable'});
 assert.equal((await review.retry()).model.original_capturer.display_name,'Retry');assert.equal(calls,2);
});

test('construction pins session, scope, page and transport options without network effects',async()=>{
 const config=options();let calls=0;config.request=async(url,init)=>{calls++;assert.equal(url,'/api/v1/admin/captures/'+C+'/audit-details?limit=2');assert.equal(init.headers.Authorization,'Bearer synthetic');return response();};
 const review=createAuditReview(config);assert.equal(calls,0);
 config.session.account_id=OWNER;config.session.access_token='changed';config.pending.capture_id=O;config.pending.limit=30;config.pending.cursor='bad';config.isCurrent=()=>false;config.request=async()=>{throw Error('wrong transport');};
 const result=await review.load();assert.equal(result.kind,'loaded');assert.equal(calls,1);
 assert.ok(Object.isFrozen(review));assert.ok(Object.isFrozen(result));assert.ok(Object.isFrozen(result.model));
});

test('initial false, throwing, aborted and reentrant authority observations refuse locally',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const isCurrent of [()=>false,()=>{throw Error('PRIVATE');}]){const review=createAuditReview(options({request,isCurrent}));assert.deepEqual(await review.load(),{kind:'locked'});}
 const aborted=new AbortController();aborted.abort();assert.deepEqual(await createAuditReview(options({request,signal:aborted.signal})).load(),{kind:'locked'});
 let review;review=createAuditReview(options({request,isCurrent:()=>{review?.invalidate();return true;}}));assert.deepEqual(await review.load(),{kind:'locked'});assert.equal(calls,0);
});
