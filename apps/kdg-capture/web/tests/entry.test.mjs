import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createEntryBoundary} from '../src/entry.ts';
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222';
const ORG='33333333-3333-4333-8333-333333333333';
const session=account=>({account_id:account,access_token:'synthetic-'+account});
const body=account=>({account_id:account,actor_id:'44444444-4444-4444-8444-444444444444',
 membership_id:'9007199254740993',permission:'kdg_capture.capture.read.own',
 authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:account},
 decision_id:'55555555-5555-4555-8555-555555555555',checked_at:'2026-10-22T12:34:56.123456Z'});
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json','cache-control':'private, no-store'}});

test('entry clears on account change and only current authorized response is published',async()=>{
 let release;const events=[];let calls=0;
 const gate=createEntryBoundary(ORG,state=>events.push(state),async()=>{
  calls++;if(calls===1)return new Promise(resolve=>{release=resolve;});
  return response(body(B));
 });
 const old=gate.check(session(A));
 assert.equal(gate.state().kind,'checking');
 const current=await gate.check(session(B));
 assert.equal(current.kind,'authorized');
 assert.equal(current.context.account_id,B);
 release(response(body(A)));
 assert.equal((await old).kind,'superseded');
 assert.equal(gate.state().context.account_id,B);
 assert.ok(!JSON.stringify(events).includes('synthetic-'));
 gate.dispose();
});

const entry=await import('../src/entry.ts');
const read=(request,options={})=>entry.getCurrentContext(session(A),ORG,{request,timeoutMs:50,...options});

test('own request has no selectors and validates exact generated context',async()=>{
 const result=await read(async(url,init)=>{
  assert.equal(url,'/api/v1/context');assert.equal(init.method,'GET');
  assert.equal(init.credentials,'same-origin');assert.equal(init.mode,'same-origin');
  assert.equal(init.redirect,'error');assert.equal(init.cache,'no-store');
  assert.equal(init.headers.Authorization,session(A).access_token.startsWith('synthetic-')?'Bearer '+session(A).access_token:'wrong');
  assert.equal(init.body,undefined);return response(body(A));
 });
 assert.equal(result.kind,'authorized');assert.equal(result.context.membership_id,'9007199254740993');
 assert.ok(Object.isFrozen(result.context));assert.ok(Object.isFrozen(result.context.resource_scope));
});

for(const [status,error_id,kind] of [[401,'authentication_required','authentication_required'],[403,'access_denied','access_denied'],
 [409,'identity.actor_setup_required','actor_setup_required'],[503,'authorization_unavailable','authorization_unavailable'],
 [500,'internal_error','authorization_unavailable'],[422,'validation_failed','invalid_response']]){
 test('safe '+status+' '+error_id,async()=>{
  for(const envelope of [{error:'SENSITIVE',error_id,code:status},{detail:{code:error_id,message:'SENSITIVE'}}]){
   const result=await read(async()=>response(envelope,status));
   assert.deepEqual(result,{kind});assert.ok(!JSON.stringify(result).includes('SENSITIVE'));
  }
 });
}
for(const [key,value] of [['account_id',B],['actor_id','00000000-0000-0000-0000-000000000000'],
 ['membership_id','9223372036854775808'],['membership_id',9007199254740993],['membership_id','01'],['membership_id','1\n'],['actor_id',A+'\n'],
 ['permission','kdg_capture.capture.read.all'],['resource_scope',{kind:'own_account',account_id:B}],
 ['authorization_scope',{kind:'organization',org_id:B}],['checked_at','2026-02-30T12:34:56Z'],
 ['checked_at','2026-10-22T12Z'],['extra','SENSITIVE']]){
 test('invalid authority '+key+' '+String(value),async()=>{
  assert.deepEqual(await read(async()=>response({...body(A),[key]:value})),{kind:'invalid_response'});
 });
}
test('header and body stalls share a deadline even when transport ignores abort',async()=>{
 for(const phase of ['headers','body']){
  const start=performance.now();
  const result=await read(async()=>phase==='headers'?new Promise(()=>{}):
   new Response(new ReadableStream({start(controller){controller.enqueue(new TextEncoder().encode('{'));}}),
    {headers:{'content-type':'application/json'}}),{timeoutMs:25});
  assert.deepEqual(result,{kind:'authorization_unavailable'});
  assert.ok(performance.now()-start<500);
 }
});
test('logout and same-account recheck ignore late success or denial; dispose stays closed',async()=>{
 for(const status of [200,403]){
  let release;const states=[];
  const gate=createEntryBoundary(ORG,s=>states.push(s),()=>new Promise(resolve=>release=resolve));
  const pending=gate.check(session(A));gate.clear();assert.equal(gate.state().kind,'signed_out');
  release(response(status===200?body(A):{error_id:'access_denied'},status));
  assert.equal((await pending).kind,'superseded');assert.equal(gate.state().kind,'signed_out');
  gate.dispose();assert.equal((await gate.check(session(A))).kind,'superseded');
 }
 let releases=[];const gate=createEntryBoundary(ORG,()=>{},()=>new Promise(resolve=>releases.push(resolve)));
 const first=gate.check(session(A)),second=gate.check(session(A));
 releases[1](response(body(A)));await second;
 releases[0](response({error_id:'access_denied'},403));await first;
 assert.equal(gate.state().kind,'authorized');gate.dispose();
});
test('missing auth, external cancellation, malformed/oversized bodies and network errors stay safe',async()=>{
 let called=false;
 assert.deepEqual(await entry.getCurrentContext({...session(A),access_token:'bad\n'},ORG,{request:async()=>{called=true;}}),{kind:'authentication_required'});
 assert.equal(called,false);
 const controller=new AbortController();controller.abort();
 assert.deepEqual(await read(async()=>{throw new Error('unexpected');},{signal:controller.signal}),{kind:'cancelled'});
 for(const raw of ['<html>SENSITIVE</html>',' '.repeat(16385),'null']){
  assert.deepEqual(await read(async()=>new Response(raw)),{kind:'invalid_response'});
 }
 assert.deepEqual(await read(async()=>{throw new Error('SENSITIVE');}),{kind:'authorization_unavailable'});
});

test('closed context rejects year zero, nested extras, missing fields and malformed UTF-8',async()=>{
 const missing=body(A);delete missing.actor_id;
 for(const value of [{...body(A),checked_at:'0000-01-01T00:00:00Z'},
  {...body(A),authorization_scope:{...body(A).authorization_scope,extra:true}},
  {...body(A),resource_scope:{...body(A).resource_scope,extra:true}},missing]){
  assert.deepEqual(await read(async()=>response(value)),{kind:'invalid_response'});
 }
 assert.deepEqual(await read(async()=>new Response(new Uint8Array([0xff]))),{kind:'invalid_response'});
});
test('late headers after deadline cancel the body without reading it',async()=>{
 let release,cancelled=false;
 const pending=read(()=>new Promise(resolve=>release=resolve),{timeoutMs:10});
 assert.deepEqual(await pending,{kind:'authorization_unavailable'});
 release(new Response(new ReadableStream({cancel(){cancelled=true;}})));
 await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,true);
});
test('external cancellation during body consumption promptly cancels stream',async()=>{
 let cancelled=false,started;const ready=new Promise(resolve=>started=resolve);
 const controller=new AbortController();
 const pending=read(async()=>new Response(new ReadableStream({start(){started();},cancel(){cancelled=true;}})),{signal:controller.signal});
 await ready;controller.abort();assert.deepEqual(await pending,{kind:'cancelled'});
 await new Promise(resolve=>setTimeout(resolve,0));assert.equal(cancelled,true);
});
test('disposal aborts pending request and prevents later publication',async()=>{
 let release,signal;const states=[];
 const gate=createEntryBoundary(ORG,s=>states.push(s),async(_,init)=>{signal=init.signal;return new Promise(resolve=>release=resolve);});
 const pending=gate.check(session(A));gate.dispose();
 assert.equal(signal.aborted,true);assert.equal((await pending).kind,'superseded');
 release(response(body(A)));await new Promise(resolve=>setTimeout(resolve,0));
 assert.deepEqual(states.map(s=>s.kind),['checking']);assert.equal(gate.state().kind,'signed_out');
});
test('reentrant publication preserves replacement cancellation controller',async()=>{
 let replacement,signal;
 const gate=createEntryBoundary(ORG,s=>{if(s.kind==='authorized')replacement=gate.check(session(B));},async(_,init)=>{
  if(!signal){signal=init.signal;return response(body(A));}
  signal=init.signal;return new Promise(()=>{});
 });
 await gate.check(session(A));gate.clear();assert.equal(signal.aborted,true);
 assert.equal((await replacement).kind,'superseded');gate.dispose();
});
