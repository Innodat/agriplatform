import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createEditEntry} from '../../../../compiled/web/src/edit-entry.js';
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333',OP='66666666-6666-4666-8666-666666666666',C='77777777-7777-4777-8777-777777777777';
const session=(id=A,token='synthetic-'+id)=>({user:{id},access_token:token});
const context=(id,org=ORG)=>({account_id:id,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',authorization_scope:{kind:'organization',org_id:org},resource_scope:{kind:'own_account',account_id:id},permission:'kdg_capture.capture.read.own',decision_id:'55555555-5555-4555-8555-555555555555',checked_at:'2026-10-23T10:00:00Z'});
const pending=(changes={})=>({account_id:A,org_id:ORG,capture_id:C,command:{operation_id:OP,command_version:1,expected_revision:'1',observation_date:'2026-10-26',answers:{[C]:{value:'original'}}},...changes});
const receipt=()=>({operation_id:OP,command_type:'capture.edit',command_version:1,status:'committed',result:{capture_id:C,revision:'1'}});
const response=(value=receipt(),status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
const tick=()=>new Promise(r=>setTimeout(r,0));
function fixture(recover=async()=>response(),options={},admit){
 let cb,current=session(),sdk=0;const states=[],requests=[];
 const auth={getSession:async()=>{sdk++;return{data:{session:current},error:null};},refreshSession:async()=>{sdk++;return{data:{session:current},error:null};},signOut:async()=>{sdk++;return{error:null};},onAuthStateChange:callback=>{cb=callback;return{data:{subscription:{unsubscribe(){}}}};}};
 const gate=createEditEntry({org:ORG,auth,publish:s=>states.push(s),beginSignIn:async()=>{sdk++;},timeoutMs:100,editTimeoutMs:100,
 request:async(url,init)=>{if(url.startsWith('/api/v1/context'))return admit?admit(url,init):response(context(init.headers.Authorization.includes(B)?B:A,options.org??ORG));requests.push({url,init});return recover(url,init);},...options});
 return{gate,states,requests,sdk:()=>sdk,emit(event,s){current=s;cb(event,s);}};
}
test('current admitted entry edits original operation with captured bearer and no Auth side effects',async()=>{
 const f=fixture();await f.gate.start();const before=f.sdk();const result=await f.gate.edit(pending());
 assert.equal(result.kind,'committed');assert.equal(f.requests.length,1);assert.equal(f.requests[0].url,'/api/v1/captures/'+C);assert.equal(f.requests[0].init.method,'PUT');assert.deepEqual(JSON.parse(f.requests[0].init.body),pending().command);assert.equal(f.requests[0].init.headers.Authorization,'Bearer synthetic-'+A);assert.equal(f.sdk(),before);
 assert.equal(f.gate.acquireExecution,undefined);assert.ok(!JSON.stringify(f.states).includes('synthetic-'));assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('unadmitted and mismatched account or organization cannot request edit',async()=>{
 const f=fixture();assert.equal((await f.gate.edit(pending())).kind,'superseded');await f.gate.start();
 for(const changes of [{account_id:B},{org_id:B}])assert.equal((await f.gate.edit(pending(changes))).kind,'invalid_request');
 assert.equal(f.requests.length,0);f.gate.dispose();assert.equal((await f.gate.edit(pending())).kind,'superseded');
});
for(const action of ['refresh','account','retry','signIn','signOut','recovery','dispose'])test('entry '+action+' aborts in-flight edit before late headers',async()=>{
 const held=deferred(),f=fixture(()=>held.promise);await f.gate.start();const old=f.gate.edit(pending());await tick();const signal=f.requests[0].init.signal;
 if(action==='refresh')f.emit('TOKEN_REFRESHED',session(A,'fresh'));
 else if(action==='account')f.emit('SIGNED_IN',session(B));
 else if(action==='recovery')f.emit('PASSWORD_RECOVERY',session(A));
 else if(action==='dispose')f.gate.dispose();else void f.gate[action]();
 assert.equal(signal.aborted,true);assert.equal((await old).kind,'superseded');held.resolve(response());await tick();f.gate.dispose();
});
test('body-phase stale error cannot escape after A to B to A replacement',async()=>{
 let send;const f=fixture(async()=>new Response(new ReadableStream({start(c){send=()=>{c.enqueue(new TextEncoder().encode(JSON.stringify({error:'SENSITIVE',error_id:'access_denied'})));c.close();};}}),{status:403,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}));
 await f.gate.start();const old=f.gate.edit(pending());await tick();f.emit('SIGNED_IN',session(B));await tick();f.emit('SIGNED_IN',session(A));await tick();
 assert.equal((await old).kind,'superseded');try{send();}catch{}assert.equal(f.gate.state().context.account_id,A);f.gate.dispose();
});
test('completion preserves other current work and deadline bounds ignored transport',async()=>{
 const held=deferred();let n=0;const f=fixture(()=>++n===1?held.promise:Promise.resolve(response()),{editTimeoutMs:20});await f.gate.start();
 const first=f.gate.edit(pending());await tick();assert.equal((await f.gate.edit(pending())).kind,'committed');assert.equal(f.requests[0].init.signal.aborted,false);
 assert.equal((await first).kind,'verification_unavailable');assert.equal(f.gate.state().kind,'authorized');held.resolve(response());f.gate.dispose();
});
for(const [value,status,kind] of [
 [{error:'SENSITIVE',error_id:'kdg_capture.capture_revision_conflict',current_revision:'9223372036854775807'},409,'error'],
 [{error:'SENSITIVE',error_id:'access_denied'},403,'error'],
 [{error:'SENSITIVE',error_id:'authentication_required'},401,'error'],
 [{error:'SENSITIVE',error_id:'authorization_unavailable'},503,'error'],
])test('current '+kind+' result stays safe and releases only its request',async()=>{
 const f=fixture(async()=>response(value,status));await f.gate.start();const before=f.sdk(),publications=f.states.length;const result=await f.gate.edit(pending());assert.equal(result.kind,kind);
 assert.equal(f.requests[0].init.signal.aborted,true);assert.equal(f.gate.state().kind,'authorized');assert.ok(Object.isFrozen(result));assert.equal(f.sdk(),before);assert.equal(f.states.length,publications);assert.ok(!JSON.stringify(result).includes('SENSITIVE'));f.gate.dispose();
});
test('replacement admission uses refreshed bearer; disposed organization owner cannot edit',async()=>{
 const f=fixture();await f.gate.start();f.emit('TOKEN_REFRESHED',session(A,'fresh'));await tick();assert.equal((await f.gate.edit(pending())).kind,'committed');
 assert.equal(f.requests[0].init.headers.Authorization,'Bearer fresh');f.gate.dispose();const other=fixture(undefined,{org:B});await other.gate.start();
 assert.equal(other.gate.state().kind,'authorized');assert.equal(other.gate.state().context.authorization_scope.org_id,B);
 assert.equal((await other.gate.edit(pending({org_id:B}))).kind,'committed');assert.equal(other.requests.length,1);assert.deepEqual(JSON.parse(other.requests[0].init.body),pending().command);
 assert.equal((await f.gate.edit(pending())).kind,'superseded');assert.equal(f.requests.length,1);other.gate.dispose();
});

test('malformed runtime input fails safely before transport, including throwing accessors',async()=>{
 const f=fixture();await f.gate.start();
 for(const input of [null,undefined,17,{},Object.defineProperty({},'account_id',{enumerable:true,get(){throw Error('SENSITIVE');}})])assert.equal((await f.gate.edit(input)).kind,'invalid_request');
 assert.equal(f.requests.length,0);f.gate.dispose();
});
test('admitted edit rejects a mismatched original capture receipt',async()=>{
 const f=fixture(async()=>response({...receipt(),result:{capture_id:B,revision:'2'}}));await f.gate.start();
 assert.equal((await f.gate.edit(pending())).kind,'invalid_response');f.gate.dispose();
});
test('malformed current error is refused without changing admission',async()=>{
 const f=fixture(async()=>response({error_id:'access_denied'},403));await f.gate.start();assert.equal((await f.gate.edit(pending())).kind,'invalid_response');assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('configuration and nested caller mutation cannot retarget an executing original edit',async()=>{
 const held=deferred(),configuration={};const f=fixture(()=>held.promise,configuration);await f.gate.start();
 const input=pending(),original=JSON.stringify(input),work=f.gate.edit(input);
 input.account_id=B;input.org_id=B;input.capture_id=B;input.command.operation_id=B;input.command.answers[C].value='changed';configuration.org=B;configuration.request=()=>{throw Error('SENSITIVE');};
 assert.deepEqual(JSON.parse(f.requests[0].init.body),JSON.parse(original).command);held.resolve(response());assert.equal((await work).kind,'committed');f.gate.dispose();
});
test('factory pins actual supplied configuration before caller mutation',async()=>{
 let callback;const states=[];const requests=[];const configuration={org:ORG,publish:s=>states.push(s),beginSignIn:async()=>{},auth:{getSession:async()=>({data:{session:session()},error:null}),refreshSession:async()=>({data:{session:session()},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return{data:{subscription:{unsubscribe(){}}}};}},request:async(url,init)=>{requests.push({url,init});return response(url.startsWith('/api/v1/context')?context(A):receipt());}};
 const gate=createEditEntry(configuration);configuration.org=B;configuration.editTimeoutMs=-1;configuration.request=async()=>{throw Error('SENSITIVE');};await gate.start();assert.equal((await gate.edit(pending())).kind,'committed');assert.equal(requests.length,2);assert.ok(callback);gate.dispose();
});
for(const phase of ['scope','nested','throwing'])test('reentrant '+phase+' input invalidation is superseded without dispatch',async()=>{
 const f=fixture();await f.gate.start();const input=pending();
 if(phase==='scope'||phase==='throwing')Object.defineProperty(input,'account_id',{enumerable:true,get(){f.gate.dispose();if(phase==='throwing')throw Error('SENSITIVE');return A;}});
 else Object.defineProperty(input.command.answers[C],'value',{enumerable:true,get(){f.gate.dispose();return 'original';}});
 assert.equal((await f.gate.edit(input)).kind,'superseded');assert.equal(f.requests.length,0);f.gate.dispose();
});
test('offline replacement aborts held old edit and refuses new work after late response',async()=>{
 const held=deferred(),f=fixture(()=>held.promise);await f.gate.start();const old=f.gate.edit(pending());await tick();const signal=f.requests[0].init.signal;
 f.gate.dispose();const offline=fixture(undefined,{online:false});await offline.gate.start();assert.equal(signal.aborted,true);
 assert.equal((await offline.gate.edit(pending())).kind,'superseded');assert.equal(offline.requests.length,0);
 held.resolve(response());assert.equal((await old).kind,'superseded');await tick();
 assert.equal((await f.gate.edit(pending())).kind,'superseded');assert.equal((await offline.gate.edit(pending())).kind,'superseded');assert.equal(offline.requests.length,0);assert.equal(f.requests.length,1);offline.gate.dispose();
});
for(const kind of ['success','error'])test('replacement during ready '+kind+' response cleanup suppresses adapter result',async()=>{
 let f;f=fixture(async()=>{const value=kind==='success'?receipt():{error:'SENSITIVE',error_id:'access_denied'};const r=response(value,kind==='success'?200:403);const get=r.body.getReader.bind(r.body);r.body.getReader=()=>{const reader=get();const cancel=reader.cancel.bind(reader);reader.cancel=(...args)=>{f.gate.dispose();return cancel(...args);};return reader;};return r;});
 await f.gate.start();assert.equal((await f.gate.edit(pending())).kind,'superseded');f.gate.dispose();
});
test('network error preserves input and current admission without retries',async()=>{
 const f=fixture(async()=>{throw Error('SENSITIVE');});await f.gate.start();const input=pending(),snapshot=JSON.stringify(input),before=f.sdk(),publications=f.states.length;
 assert.deepEqual(await f.gate.edit(input),{kind:'verification_unavailable'});assert.equal(JSON.stringify(input),snapshot);assert.equal(f.sdk(),before);assert.equal(f.states.length,publications);assert.equal(f.requests.length,1);assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('invalid input leaves a current sibling execution usable',async()=>{
 const held=deferred(),f=fixture(()=>held.promise);await f.gate.start();const first=f.gate.edit(pending());
 assert.equal((await f.gate.edit(pending({account_id:B}))).kind,'invalid_request');assert.equal(f.requests[0].init.signal.aborted,false);held.resolve(response());assert.equal((await first).kind,'committed');f.gate.dispose();
});
test('typed conflict preserves exact revision and original caller input',async()=>{
 const f=fixture(async()=>response({error:'SENSITIVE',error_id:'kdg_capture.capture_revision_conflict',current_revision:'9223372036854775807'},409));await f.gate.start();const input=pending(),before=JSON.stringify(input);
 assert.deepEqual(await f.gate.edit(input),{kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'9223372036854775807'});assert.equal(JSON.stringify(input),before);f.gate.dispose();
});

test('pending current-context admission cannot PUT',async()=>{
 const held=deferred(),f=fixture(undefined,{},()=>held.promise);const started=f.gate.start();await tick();
 assert.equal((await f.gate.edit(pending())).kind,'superseded');assert.equal(f.requests.length,0);
 held.resolve(response(context(A)));await started;assert.equal(f.gate.state().kind,'authorized');assert.equal(f.requests.length,0);f.gate.dispose();
});
for(const [status,error_id] of [[403,'access_denied'],[503,'authorization_unavailable']])test('context '+status+' cannot admit a PUT',async()=>{
 const f=fixture(undefined,{},()=>response({error:'SENSITIVE',error_id},status));await f.gate.start();
 assert.notEqual(f.gate.state().kind,'authorized');assert.equal((await f.gate.edit(pending())).kind,'superseded');assert.equal(f.requests.length,0);f.gate.dispose();
});
for(const editTimeoutMs of [0,-1,NaN,Infinity,10001])test('invalid editTimeoutMs '+editTimeoutMs+' preserves admission and independent valid execution',async()=>{
 const held=deferred(),valid=fixture(()=>held.promise),f=fixture(undefined,{editTimeoutMs});await valid.gate.start();await f.gate.start();const work=valid.gate.edit(pending());
 const state=f.gate.state(),publications=f.states.length,before=f.sdk();assert.deepEqual(await f.gate.edit(pending()),{kind:'invalid_request'});
 assert.equal(f.requests.length,0);assert.equal(f.gate.state(),state);assert.equal(f.states.length,publications);assert.equal(f.sdk(),before);assert.equal(valid.requests[0].init.signal.aborted,false);
 held.resolve(response());assert.equal((await work).kind,'committed');f.gate.dispose();valid.gate.dispose();
});
