// GENERATED E1-CONTEXT client/lease acceptance; actual rendered proof is separate.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createLeaveClient} from '../src/api/leave.ts';
import {createContextController} from '../src/context-controller.ts';
const org='11111111-1111-4111-8111-111111111111',other='22222222-2222-4222-8222-222222222222',employment='33333333-3333-4333-8333-333333333333';
const ready={status:'ready',org_id:org,employment_id:employment,editability:{status:'editable'},setup_notices:[]};
test('context read uses protected Leave API and validates scoped closed response',async()=>{
 const calls=[];const c=createLeaveClient(async(url,options)=>{calls.push([url,options]);return Response.json(ready);});
 assert.deepEqual(await c.context('private',new AbortController().signal,org),{ok:true,value:ready});
 assert.equal(calls[0][0],'/api/v1/organizations/'+org+'/me/draft-context');assert.equal(calls[0][1].cache,'no-store');
 for(const value of [{...ready,org_id:other},{...ready,active_draft:null},{...ready,scope_generation:'0'},{...ready,editability:{status:'read_only'}},{...ready,setup_notices:[{code:'unknown'}]}])assert.deepEqual(await createLeaveClient(async()=>Response.json(value)).context('x',new AbortController().signal,org),{ok:false,error_id:'invalid_response'});
});
test('typed setup, read-only, notice, unavailable and denial remain distinct',async()=>{
 for(const value of [{status:'setup_required',org_id:org,reason:'employment_missing'},{...ready,editability:{status:'read_only',reason:'permission_missing'}},{...ready,setup_notices:[{code:'work_timezone_missing'}]}])assert.equal((await createLeaveClient(async()=>Response.json(value)).context('x',new AbortController().signal,org)).ok,true);
 for(const [status,error_id] of [[403,'access_denied'],[503,'dependency_unavailable']])assert.deepEqual(await createLeaveClient(async()=>Response.json({error_id,error:'safe',details:{}},{status})).context('x',new AbortController().signal,org),{ok:false,error_id});
});
test('context enums reject arrays without publishing an editable observation',async()=>{
 for(const value of [
  {status:'setup_required',org_id:org,reason:['employment_missing']},
  {...ready,editability:{status:'read_only',reason:['employment_ended']}},
  {...ready,editability:{status:'read_only',reason:[['employment_ended']]}},
  {...ready,setup_notices:[{code:['work_timezone_invalid']}]},
 ]){
  const client=createLeaveClient(async()=>Response.json(value));
  assert.deepEqual(await client.context('x',new AbortController().signal,org),{ok:false,error_id:'invalid_response'});
  const f=fixture(client);await f.controller.load(org);assert.equal(f.states.at(-1).kind,'unavailable');
 }
});
function fixture(client){let current=true;const abort=new AbortController(),states=[];let released=0;const controller=createContextController({client,acquire:()=>({session:{access_token:'private'},signal:abort.signal,isCurrent:()=>current,release(){released++;}}),publish:s=>states.push(s)});return{controller,states,released:()=>released,revoke(){current=false;abort.abort();}};}
test('organization replacement drops old result and clears old protected state',async()=>{
 let finish;const f=fixture({context:async(_t,_s,o)=>o===org?new Promise(r=>finish=r):{ok:true,value:{...ready,org_id:other}}});
 const first=f.controller.load(org);await f.controller.load(other);finish({ok:true,value:ready});await first;
 assert.equal(f.states.at(-1).value.org_id,other);assert.deepEqual(f.states.filter(s=>s.kind==='loading'),[{kind:'loading'},{kind:'loading'}]);assert.equal(f.released(),2);
});
test('account invalidation and disposal prevent delayed disclosure',async()=>{
 for(const end of ['revoke','dispose']){let finish;const f=fixture({context:()=>new Promise(r=>finish=r)});const work=f.controller.load(org);if(end==='revoke')f.revoke();else f.controller.dispose();finish({ok:true,value:ready});await work;assert.equal(f.states.some(s=>s.kind==='resolved'),false);assert.equal(f.released(),1);}
});
test('retry is a fresh read; outage never becomes setup or permission restriction',async()=>{
 let calls=0;const f=fixture({context:async()=>++calls===1?{ok:false,error_id:'dependency_unavailable'}:{ok:true,value:ready}});await f.controller.load(org);assert.equal(f.states.at(-1).kind,'unavailable');await f.controller.load(org);assert.equal(f.states.at(-1).kind,'resolved');assert.equal(calls,2);
});
