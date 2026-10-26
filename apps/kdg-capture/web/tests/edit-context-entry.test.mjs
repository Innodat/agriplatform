import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createEditContextEntry} from '../../../../compiled/web/src/edit-context-entry.js';
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333',OP='66666666-6666-4666-8666-666666666666',C='77777777-7777-4777-8777-777777777777';
const session=(id=A,token='synthetic-'+id)=>({user:{id},access_token:token});
const context=id=>({account_id:id,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:id},permission:'kdg_capture.capture.read.own',decision_id:'55555555-5555-4555-8555-555555555555',checked_at:'2026-10-23T10:00:00Z'});
const pending=(changes={})=>({account_id:A,org_id:ORG,capture_id:C,...changes});
const receipt=()=>({capture_id:C,org_id:ORG,owner_account_id:A,owner_actor_id:A,child_id:C,child_label:'Child',questionnaire_id:OP,questionnaire_version_id:OP,questionnaire_version:'1',revision:'2',observation_date:'2026-10-26',answers:{[OP]:{value:3}},definition:{schema_version:1,questions:[{id:OP,type:'rating',label:'Original',required:true,minimum:1,maximum:5,minimum_label:'Goed',maximum_label:'Nie goed nie'}]},captured_at:'2026-10-26T10:00:00Z',created_by:A,created_at:'2026-10-26T10:00:00Z',updated_by:A,updated_at:'2026-10-26T10:00:00Z'});
const observation=(permission)=>({...context(A),actor_id:A,permission,expires_at:'2026-10-30T10:00:00Z'});
const editContext=()=>({capture:receipt(),editable_fields:['observation_date','answers'],read_observation:observation('kdg_capture.capture.read.own'),edit_observation:observation('kdg_capture.capture.edit.own')});
const response=(value=editContext(),status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
const tick=()=>new Promise(r=>setTimeout(r,0));
function fixture(recover=async()=>response(),options={}){
 let cb,current=session(),sdk=0;const states=[],requests=[];
 const auth={getSession:async()=>{sdk++;return{data:{session:current},error:null};},refreshSession:async()=>{sdk++;return{data:{session:current},error:null};},signOut:async()=>{sdk++;return{error:null};},onAuthStateChange:callback=>{cb=callback;return{data:{subscription:{unsubscribe(){}}}};}};
 const gate=createEditContextEntry({org:ORG,auth,publish:s=>states.push(s),beginSignIn:async()=>{sdk++;},timeoutMs:1000,editContextTimeoutMs:1000,
 request:async(url,init)=>{if(url.startsWith('/api/v1/context'))return response(context(init.headers.Authorization.includes(B)?B:A));requests.push({url,init});return recover(url,init);},...options});
 return{gate,states,requests,sdk:()=>sdk,emit(event,s){current=s;cb(event,s);}};
}
test('current admitted entry recovers current capture with captured bearer and no Auth side effects',async()=>{
 const f=fixture();await f.gate.start();const before=f.sdk();const result=await f.gate.load(pending());
 assert.equal(result.kind,'loaded');assert.equal(f.requests.length,1);assert.equal(f.requests[0].init.headers.Authorization,'Bearer synthetic-'+A);assert.equal(f.sdk(),before);
 assert.equal(f.gate.acquireExecution,undefined);assert.ok(!JSON.stringify(f.states).includes('synthetic-'));assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('unadmitted and mismatched account or organization cannot request readback',async()=>{
 const f=fixture();assert.equal((await f.gate.load(pending())).kind,'superseded');await f.gate.start();
 for(const changes of [{account_id:B},{org_id:B}])assert.equal((await f.gate.load(pending(changes))).kind,'invalid_request');
 assert.equal(f.requests.length,0);f.gate.dispose();assert.equal((await f.gate.load(pending())).kind,'superseded');
});
for(const action of ['refresh','account','retry','signIn','signOut','recovery','dispose'])test('entry '+action+' aborts in-flight readback before late headers',async()=>{
 const held=deferred(),f=fixture(()=>held.promise);await f.gate.start();const old=f.gate.load(pending());await tick();const signal=f.requests[0].init.signal;
 if(action==='refresh')f.emit('TOKEN_REFRESHED',session(A,'fresh'));
 else if(action==='account')f.emit('SIGNED_IN',session(B));
 else if(action==='recovery')f.emit('PASSWORD_RECOVERY',session(A));
 else if(action==='dispose')f.gate.dispose();else void f.gate[action]();
 assert.equal(signal.aborted,true);assert.equal((await old).kind,'superseded');held.resolve(response());await tick();f.gate.dispose();
});
test('body-phase stale error cannot escape after A to B to A replacement',async()=>{
 let send;const f=fixture(async()=>new Response(new ReadableStream({start(c){send=()=>{c.enqueue(new TextEncoder().encode(JSON.stringify({error:'SENSITIVE',error_id:'access_denied'})));c.close();};}}),{status:403,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}));
 await f.gate.start();const old=f.gate.load(pending());await tick();f.emit('SIGNED_IN',session(B));await tick();f.emit('SIGNED_IN',session(A));await tick();
 assert.equal((await old).kind,'superseded');try{send();}catch{}assert.equal(f.gate.state().context.account_id,A);f.gate.dispose();
});
test('completion preserves other current work and deadline bounds ignored transport',async(t)=>{
 const held=deferred();let n=0;const f=fixture(()=>++n===1?held.promise:Promise.resolve(response()),{editContextTimeoutMs:20});await f.gate.start();
 // Control both clock and timer: another fast operation is not a host-latency assertion.
 let now=0;t.mock.method(performance,'now',()=>now);t.mock.timers.enable({apis:['setTimeout']});
 const first=f.gate.load(pending());await Promise.resolve();assert.equal((await f.gate.load(pending())).kind,'loaded');assert.equal(f.requests[0].init.signal.aborted,false);
 now=20;t.mock.timers.tick(20);
 assert.equal((await first).kind,'verification_unavailable');assert.equal(f.gate.state().kind,'authorized');held.resolve(response());f.gate.dispose();
});
for(const [value,status,kind] of [
 [{error:'SENSITIVE',error_id:'access_denied'},403,'error'],
 [{error:'SENSITIVE',error_id:'authentication_required'},401,'error'],
 [{error:'SENSITIVE',error_id:'authorization_unavailable'},503,'error'],
])test('current '+kind+' result stays safe and releases only its request',async()=>{
 const f=fixture(async()=>response(value,status));await f.gate.start();const before=f.sdk(),publications=f.states.length;const result=await f.gate.load(pending());assert.equal(result.kind,kind);
 assert.equal(f.requests[0].init.signal.aborted,true);assert.equal(f.gate.state().kind,'authorized');assert.ok(Object.isFrozen(result));assert.equal(f.sdk(),before);assert.equal(f.states.length,publications);assert.ok(!JSON.stringify(result).includes('SENSITIVE'));f.gate.dispose();
});
test('replacement admission uses refreshed bearer; disposed organization owner cannot recover',async()=>{
 const f=fixture();await f.gate.start();f.emit('TOKEN_REFRESHED',session(A,'fresh'));await tick();assert.equal((await f.gate.load(pending())).kind,'loaded');
 assert.equal(f.requests[0].init.headers.Authorization,'Bearer fresh');f.gate.dispose();const other=fixture(undefined,{org:B});await other.gate.start();
 assert.equal((await other.gate.load(pending())).kind,'superseded');assert.equal(other.requests.length,0);other.gate.dispose();
});

test('malformed runtime input fails safely before transport, including throwing accessors',async()=>{
 const f=fixture();await f.gate.start();
 for(const input of [null,undefined,17,{},Object.defineProperty({},'account_id',{enumerable:true,get(){throw Error('SENSITIVE');}})])assert.equal((await f.gate.load(input)).kind,'invalid_request');
 assert.equal(f.requests.length,0);f.gate.dispose();
});
test('admitted read binds original account org and capture identity',async()=>{
 const f=fixture(async()=>response({...editContext(),capture:{...receipt(),capture_id:B}}));await f.gate.start();
 assert.equal((await f.gate.load(pending())).kind,'invalid_response');assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('malformed current error is refused without changing admission',async()=>{
 const f=fixture(async()=>response({error_id:'access_denied'},403));await f.gate.start();assert.equal((await f.gate.load(pending())).kind,'invalid_response');assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});
for(const throwing of [false,true])test('accessor-triggered account replacement fences '+(throwing?'malformed':'mismatched')+' input before release',async()=>{
 const f=fixture();await f.gate.start();
 const input=Object.defineProperty({...pending()},'org_id',{enumerable:true,get(){f.emit('SIGNED_IN',session(B));if(throwing)throw Error('SENSITIVE');return B;}});
 assert.equal((await f.gate.load(input)).kind,'superseded');assert.equal(f.requests.length,0);f.gate.dispose();
});
