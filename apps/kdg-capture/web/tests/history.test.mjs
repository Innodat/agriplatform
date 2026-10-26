import assert from 'node:assert/strict';
import {test} from 'node:test';
import {historyCaptures} from '../../../../compiled/web/src/history.js';
import {A,O,C,Q,detail,pending,cursor,page,response} from './history-fixture.mjs';
const history=(request,options={},work=pending(),session={account_id:A,access_token:'synthetic'})=>historyCaptures(session,work,{signal:new AbortController().signal,isCurrent:()=>true,request,timeoutMs:1000,...options});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
test('one generated history GET returns deeply immutable original definitions and scope',async()=>{
 let calls=0;const result=await history(async(url,init)=>{calls++;assert.equal(url,'/api/v1/captures?from_date=2026-10-01&to_date=2026-10-26&limit=2');assert.equal(init.method,'GET');assert.equal(init.body,undefined);assert.equal(init.headers.Authorization,'Bearer synthetic');assert.equal(init.cache,'no-store');return response();});
 assert.equal(result.kind,'loaded');assert.deepEqual(result.page,page());assert.equal(calls,1);
 for(const item of [result,result.page,result.page.items,result.page.items[0],result.page.items[0].definition,result.page.items[0].answers])assert.ok(Object.isFrozen(item));
});
test('first middle final and empty pages use pinned dates and exact position',async()=>{
 const first=detail({created_at:'2026-10-26T10:00:00.000002Z',capture_id:A});
 const second=detail({created_at:'2026-10-26T10:00:00.000001Z',capture_id:Q});
 const a=await history(async()=>response(page({items:[first],next_cursor:cursor(first)})));
 assert.equal(a.kind,'loaded');
 const b=await history(async(url)=>{assert.equal(new URL(url,'https://kdg.invalid').searchParams.get('cursor'),cursor(first));return response(page({items:[second],next_cursor:null}));},{},pending({cursor:cursor(first)}));
 assert.equal(b.kind,'loaded');assert.equal(b.page.items[0].capture_id,Q);
 assert.equal((await history(async()=>response(page({items:[]})))).kind,'loaded');
 assert.equal((await history(async()=>response(page({limit:30})),{},pending({limit:undefined})) ).kind,'invalid_request');
 const defaultPending=pending();delete defaultPending.limit;
 assert.equal((await history(async()=>response(page({limit:30})),{},defaultPending)).page.limit,30);
});
for(const [name,changes] of Object.entries({wrong_owner:{account_id:Q},wrong_org:{org_id:Q},wrong_start:{from_date:'2026-09-01'},wrong_end:{to_date:'2026-10-25'},wrong_limit:{limit:30},unknown:{private:'SENSITIVE'},missing_items:{items:null},over_limit:{items:[detail(),detail(),detail()]},foreign_item:{items:[detail({owner_account_id:Q})]},foreign_org_item:{items:[detail({org_id:Q})]},invalid_item:{items:[detail({answers:{}})]},old_observation:{items:[detail({observation_date:'2026-09-30'})]},future_observation:{items:[detail({observation_date:'2026-10-27'})]},duplicate_item:{items:[detail(),detail()]},empty_continuation:{items:[],next_cursor:cursor()},wrong_position:{next_cursor:cursor(detail({capture_id:Q}))},wrong_cursor_owner:{next_cursor:cursor(detail(),{account_id:Q})},malformed_cursor:{next_cursor:'x'},wrong_cursor_limit:{next_cursor:cursor(detail(),{limit:30})},zero_year:{items:[detail({created_at:'0000-01-01T00:00:00Z'})]}}))test('refuses complete page '+name,async()=>assert.equal((await history(async()=>response(page(changes)))).kind,'invalid_response'));
test('empty page validates envelope owner and org',async()=>{
 for(const changes of [{account_id:Q},{org_id:Q}])assert.equal((await history(async()=>response(page({items:[],...changes})))).kind,'invalid_response');
});
test('microsecond order wins over inverse UUID order; tied timestamps use UUID',async()=>{
 const a=detail({capture_id:A,created_at:'2026-10-26T10:00:00.000002Z'}),b=detail({capture_id:Q,created_at:'2026-10-26T10:00:00.000001Z'});
 assert.equal((await history(async()=>response(page({items:[a,b]})))).kind,'loaded');
 assert.equal((await history(async()=>response(page({items:[b,a]})))).kind,'invalid_response');
 b.created_at=a.created_at;
 assert.equal((await history(async()=>response(page({items:[b,a]})))).kind,'loaded');
 assert.equal((await history(async()=>response(page({items:[a,b]})))).kind,'invalid_response');
});
test('every row is strictly after incoming continuation',async()=>{
 for(const item of [detail(),detail({capture_id:Q}),detail({created_at:'2026-10-27T00:00:00Z'})])assert.equal((await history(async()=>response(page({items:[item]})),{},pending({cursor:cursor()}))).kind,'invalid_response');
 assert.equal((await history(async()=>response(page({items:[detail({capture_id:A})]})),{},pending({cursor:cursor()}))).kind,'loaded');
});
test('malformed noncanonical duplicate-key and oversized cursors never dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 const value=JSON.parse(Buffer.from(cursor(),'base64url').toString());
 for(const raw of [Buffer.from(JSON.stringify(value).replace('\"v\":1','\"v\":1.0')).toString('base64url'),cursor(detail(),{from_date:'2026-10-27',to_date:'2026-10-26'}),cursor(detail(),{last_id:'00000000-0000-0000-0000-000000000000'}),cursor(detail(),{account_id:'00000000-0000-0000-0000-000000000000'}),cursor(detail(),{org_id:'00000000-0000-0000-0000-000000000000'}),'','x','x'.repeat(2049),cursor()+'=',Buffer.from(JSON.stringify(value,null,2)).toString('base64url'),Buffer.from('{"v":1,"v":1}').toString('base64url'),cursor(detail(),{v:true}),cursor(detail(),{last_created_at:'2026-10-26T10:00:00.000000Z'}),cursor(detail(),{org_id:Q}),cursor(detail(),{permission:'other'}),cursor(detail(),{private:'x'})])assert.equal((await history(request,{},pending({cursor:raw}))).kind,'invalid_request');
 assert.equal(calls,0);
});
test('query bearer and throwing caller getters never dispatch',async()=>{
 let calls=0;const request=async()=>{calls++;return response();};
 for(const change of [{account_id:Q},{org_id:'bad'},{from_date:'2026-02-30'},{from_date:'2026-10-27'},{to_date:'0000-01-01'},{limit:0},{limit:101},{limit:1.5},{operation_id:A},{cursor:undefined}])assert.equal((await history(request,{},pending(change))).kind,'invalid_request');
 const bad=Object.defineProperty({},'org_id',{enumerable:true,get(){throw Error('SENSITIVE');}});
 assert.equal((await history(request,{},bad)).kind,'invalid_request');
 assert.equal((await history(request,{},pending(),{account_id:A,access_token:'bad,token'})).kind,'authentication_required');assert.equal(calls,0);
});
test('malformed duplicate JSON UTF8 wrong metadata and complete page byte bounds',async()=>{
 const raw=JSON.stringify(page());
 for(const body of ['{',raw.replace('"items":','"\\u0069tems":[],"items":'),new Uint8Array([255]),' '.repeat(2097153)])assert.equal((await history(async()=>new Response(body,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}))).kind,'invalid_response');
 const exact=new Uint8Array(2097152);exact.fill(32);exact.set(new TextEncoder().encode(raw));
 assert.equal((await history(async()=>new Response(exact,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}))).kind,'loaded');
 for(const headers of [{'Content-Type':'text/plain','Cache-Control':'private, no-store'},{'Content-Type':'application/json'}])assert.equal((await history(async()=>new Response(raw,{headers}))).kind,'invalid_response');
});
test('individual detail512KiB is enforced inside a fitting page',async()=>{
 const ids=Array.from({length:27},(_,i)=>(i+1).toString(16).padStart(8,'0')+'-bbbb-4bbb-8bbb-'+(i+1).toString(16).padStart(12,'0'));
 const item=detail({definition:{schema_version:1,questions:ids.map(id=>({id,type:'text',label:'T',required:true}))},answers:Object.fromEntries(ids.map(id=>[id,{value:'😀'.repeat(5000)}]))});
 assert.equal((await history(async()=>response(page({items:[item]})))).kind,'invalid_response');
});
for(const [status,error_id] of [[401,'authentication_required'],[403,'access_denied'],[409,'identity.actor_setup_required'],[422,'validation_failed'],[500,'internal_error'],[503,'authorization_unavailable'],[503,'capture_read_unavailable'],[503,'execution_timeout']])test('current safe history error '+error_id,async()=>assert.deepEqual(await history(async()=>response({error:'SENSITIVE',error_id},status)),{kind:'error',status,error_id}));
test('late headers/body errors and ignored transport never publish stale pages or retry',async()=>{
 let current=true;const held=deferred(),controller=new AbortController();let calls=0;
 const old=history(()=>{calls++;return held.promise;},{isCurrent:()=>current,signal:controller.signal});current=false;held.resolve(response());assert.equal((await old).kind,'superseded');assert.equal(calls,1);
 const other=deferred(),cancelled=history(()=>other.promise,{signal:controller.signal});controller.abort();assert.equal((await cancelled).kind,'cancelled');other.resolve(response());
 assert.equal((await history(()=>new Promise(()=>{}),{timeoutMs:5})).kind,'verification_unavailable');
 const stream=new ReadableStream({pull(){return new Promise(()=>{});}});
 assert.equal((await history(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:5})).kind,'verification_unavailable');
});
test('captured dates/cursor survive caller mutation; reentrant predicate fences every result',async()=>{
 const held=deferred(),work=pending();const result=history(()=>held.promise,{},work);work.from_date='2026-01-01';held.resolve(response());assert.equal((await result).page.from_date,'2026-10-01');
 const controller=new AbortController();let calls=0;assert.equal((await history(async()=>{calls++;return response();},{signal:controller.signal,isCurrent:()=>{controller.abort();return true;}})).kind,'cancelled');assert.equal(calls,0);
});
test('individual compact UTF8 detail accepts exact512KiB and refuses one more byte',async()=>{
 const item=detail({captured_at:'2026-10-26T00:00:00.Z'});
 const remaining=524288-new TextEncoder().encode(JSON.stringify(item)).byteLength;
 item.captured_at='2026-10-26T00:00:00.'+'1'.repeat(remaining)+'Z';
 assert.equal(new TextEncoder().encode(JSON.stringify(item)).byteLength,524288);
 assert.equal((await history(async()=>response(page({items:[item]})))).kind,'loaded');
 item.captured_at=item.captured_at.replace('Z','1Z');
 assert.equal((await history(async()=>response(page({items:[item]})))).kind,'invalid_response');
});
test('non-ASCII malicious continuation and infinite empty chunks fail as whole response',async()=>{
 const value=JSON.parse(Buffer.from(cursor(),'base64url').toString());value.last_created_at='漢';
 const raw=Buffer.from(JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0)))).toString('base64url');
 assert.equal((await history(async()=>response(page({next_cursor:raw})))).kind,'invalid_response');
 const stream=new ReadableStream({pull(c){c.enqueue(new Uint8Array());}});
 assert.equal((await history(async()=>new Response(stream,{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:5})).kind,'verification_unavailable');
});
test('explicit null limit refuses before transport and null item refuses the whole page',async()=>{
 let calls=0;
 assert.equal((await history(async()=>{calls++;return response(page({limit:30}));},{},pending({limit:null}))).kind,'invalid_request');
 assert.equal(calls,0);
 for(const items of [[null],[detail(),null]])assert.deepEqual(await history(async()=>response(page({items}))),{kind:'invalid_response'});
});

for(const change of [null,{},{permission:'kdg_capture.capture.create.all'},{account_id:Q},{actor_id:'bad'},{membership_id:'0'},{decision_id:'bad'},{authorization_scope:{kind:'organization',org_id:Q}},{resource_scope:{kind:'own_account',account_id:Q}},{expires_at:'2026-11-03T10:00:00Z'},{expires_at:'2026-11-02T10:00:00.001Z'},{checked_at:'2026-02-30T10:00:00Z'},{extra:'private'}])test('closed exact own-read observation rejects '+JSON.stringify(change),async()=>{
 const valid=page();const invalid=change===null?null:Object.keys(change).length?{...valid.observation,...change}:{};
 assert.equal((await history(async()=>response({...valid,observation:invalid}))).kind,'invalid_response');
});
test('missing exact observation is refused while entry Context remains independent',async()=>{
 const value=page();delete value.observation;assert.equal((await history(async()=>response(value))).kind,'invalid_response');
});
