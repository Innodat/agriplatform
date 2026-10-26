import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createProvisionEntry} from '../../../../compiled/web/src/provision-entry.js';
import {A,O,C,actor,provision,response,pending,observation} from './provision-fixture.mjs';
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
function fixture(request=async()=>response(),settings={}){
 let callback,current={user:{id:A},access_token:'synthetic-token'};const calls=[];
 const auth={getSession:async()=>({data:{session:current},error:null}),refreshSession:async()=>({data:{session:current},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return{data:{subscription:{unsubscribe(){}}}};}};
 const entry=createProvisionEntry({org:O,auth,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{if(url==='/api/v1/context'){const value=observation('kdg_capture.capture.read.own');delete value.expires_at;return response(value);}calls.push([url,init]);return request(url,init);},...settings});
 return {entry,calls,replace(account=A){current={user:{id:account},access_token:'replacement'};callback('TOKEN_REFRESHED',current);}};
}
test('explicit admitted setup consumes one lease without exposing acquisition',async()=>{
 const f=fixture();try{assert.equal((await f.entry.load(pending())).kind,'superseded');await f.entry.start();const value=await f.entry.load(pending());assert.equal(value.kind,'loaded');assert.equal(f.calls.length,1);assert.equal(f.calls[0][1].signal.aborted,true);assert.equal(f.entry.acquireExecution,undefined);}finally{f.entry.dispose();}
});
test('mismatched selection never contacts setup',async()=>{
 const f=fixture();try{await f.entry.start();for(const value of [{account_id:C,org_id:O},{account_id:A,org_id:C},null,17,{}])assert.equal((await f.entry.load(value)).kind,'invalid_request');assert.equal(f.calls.length,0);}finally{f.entry.dispose();}
});
for(const phase of ['headers','body'])for(const action of ['replace','account','dispose'])test('entry '+action+' fences late '+phase,async()=>{
 const reached=deferred(),held=deferred();const f=fixture(async()=>{if(phase==='headers'){reached.resolve();await held.promise;return response();}return new Response(new ReadableStream({async pull(c){reached.resolve();await held.promise;try{c.enqueue(new TextEncoder().encode(JSON.stringify(provision())));c.close();}catch{}}}),{headers:{'content-type':'application/json','cache-control':'private,no-store'}});});
 try{await f.entry.start();const work=f.entry.load(pending());await reached.promise;if(action==='dispose')f.entry.dispose();else f.replace(action==='account'?C:A);assert.equal((await work).kind,'superseded');held.resolve();}finally{held.resolve();f.entry.dispose();}
});
for(const id of ['access_denied','provision_unavailable'])test('safe error releases lease '+id,async()=>{
 const f=fixture(async()=>response({error:'SENSITIVE',error_id:id},id==='access_denied'?403:503));try{await f.entry.start();const value=await f.entry.load(pending());assert.equal(value.kind,'error');assert.equal(f.calls[0][1].signal.aborted,true);assert.ok(!JSON.stringify(value).includes('SENSITIVE'));}finally{f.entry.dispose();}
});
test('throwing release returns a safe unavailable result',async()=>{
 let leaseSignal;const f=fixture(async(_url,init)=>{leaseSignal=init.signal;return response();});await f.entry.start();
 // The transport signal is a child; capture the lease via its abort registration.
 const add=AbortSignal.prototype.addEventListener,abort=AbortController.prototype.abort;let parent;
 AbortSignal.prototype.addEventListener=function(name,...args){if(name==='abort'&&parent===undefined)parent=this;return add.call(this,name,...args);};
 AbortController.prototype.abort=function(...args){if(this.signal===parent)throw Error('SENSITIVE');return abort.apply(this,args);};
 try{const value=await f.entry.load(pending());assert.equal(value.kind,'verification_unavailable');assert.ok(!JSON.stringify(value).includes('SENSITIVE'));}finally{AbortSignal.prototype.addEventListener=add;AbortController.prototype.abort=abort;f.entry.dispose();}
});
