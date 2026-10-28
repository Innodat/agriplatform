import assert from 'node:assert/strict';
import {test} from 'node:test';
import {A,O,C,OWNER,AUTHOR,EDITOR,Q,detail,history,aggregate,response,failure,authFixture,held,tick,historyCursor,auditCursor} from './admin-portal-fixture.mjs';
const {createAdminPortal}=await import('../../../../compiled/web/src/admin-portal.js').catch(()=>({}));
const config=(change={})=>({auth:authFixture().port,org_id:O,from_date:'2026-10-01',to_date:'2026-10-28',beginSignIn:async()=>{},request:async url=>response(String(url).includes('audit-details')?aggregate(detail(),Number(new URL(String(url),'http://local').searchParams.get('limit'))):String(url).includes('?')?history():detail()),timeoutMs:500,...change});

test('current all-read Auth admission renders complete cross-owner history through actual adapters',async()=>{
 assert.equal(typeof createAdminPortal,'function','administrator portal boundary/controller must exist');
 const calls=[],portal=createAdminPortal(config({request:async(url,init)=>{calls.push(String(url));assert.equal(init.headers.Authorization,'Bearer synthetic');assert.equal(init.cache,'no-store');return response(String(url).includes('audit-details')?aggregate():history());}}));
 await portal.start();const state=portal.snapshot();assert.equal(state.kind,'history');assert.equal(state.rows[0].capture.child_label,'Original child');assert.equal(state.rows[0].capturer.display_name,'<img src=x onerror=alert(1)> Capturer');assert.equal(state.rows[0].capture.owner_account_id,OWNER);assert.equal(calls.length,2);assert.ok(calls[0].endsWith('limit=5'));assert.ok(calls[1].endsWith('audit-details?limit=1'));assert.ok(!JSON.stringify(state).includes('synthetic'));portal.dispose();
});

test('history enrichment is bounded to five returned IDs and no partial rows publish',async()=>{
 const items=Array.from({length:5},(_,i)=>detail({capture_id:`cccccccc-cccc-4ccc-8ccc-ccccccccccc${i}`,created_at:`2026-10-26T10:00:0${5-i}Z`}));let calls=0;
 const portal=createAdminPortal(config({request:async url=>{calls++;const id=/captures\/([^/]+)\//.exec(String(url))?.[1];return response(id?aggregate(items.find(d=>d.capture_id===id)):history(items));}}));
 await portal.start();assert.equal(portal.snapshot().kind,'history');assert.equal(portal.snapshot().rows.length,5);assert.equal(calls,6);portal.dispose();
 for(const corrupt of ['foreign','partial','owner','creator']){
  const p=createAdminPortal(config({request:async url=>{if(!String(url).includes('audit-details'))return response(history());const v=aggregate();if(corrupt==='outage')v.actor_display={status:'temporarily_unavailable'};if(corrupt==='foreign')v.actor_display.labels[0].actor_id=Q;if(corrupt==='partial')v.actor_display.labels.pop();if(corrupt==='owner')v.audit.owner_account_id=A;if(corrupt==='creator'){v.audit.created_by=EDITOR;v.audit.owner_actor_id=EDITOR;v.actor_display.labels.shift();}return response(v);}}));
  await p.start();assert.equal(p.snapshot().kind,'unavailable',corrupt);assert.ok(!JSON.stringify(p.snapshot()).includes('Original child'));p.dispose();
 }
});

test('successful empty page needs no enrichment and unmapped capturer is a distinct safe label',async()=>{
 let calls=0;const empty=createAdminPortal(config({request:async()=>{calls++;return response(history([]));}}));await empty.start();assert.equal(empty.snapshot().kind,'history');assert.equal(empty.snapshot().rows.length,0);assert.equal(calls,1);empty.dispose();
 const p=createAdminPortal(config({request:async url=>{if(!String(url).includes('audit-details'))return response(history());const a=aggregate();a.actor_display.labels[0]={actor_id:AUTHOR,status:'unavailable'};return response(a);}}));await p.start();assert.equal(p.snapshot().rows[0].capturer.status,'unavailable');p.dispose();
});

test('valid temporary name outage renders distinct safe history fallback and retries the complete read',async()=>{
 let calls=0;const p=createAdminPortal(config({request:async url=>{calls++;return response(String(url).includes('audit-details')?aggregate(detail(),1,{}, {status:'temporarily_unavailable',labels:undefined}):history());}}));
 await p.start();assert.equal(p.snapshot().kind,'history');assert.equal(p.snapshot().rows[0].capturer.status,'temporarily_unavailable');await p.retry();assert.equal(calls,4);p.dispose();
});

test('detail composes fresh original answers with exact matching latest attribution; mismatches reject all',async()=>{
 for(const field of [null,'revision','updated_by','updated_at','owner_account_id','created_at']){
  let detailPhase=false;const p=createAdminPortal(config({request:async url=>{const audit=String(url).includes('audit-details');if(!detailPhase)return response(audit?aggregate():history());if(!audit)return response(detail());const value=aggregate(detail(),5);if(field==='revision')value.audit.current_revision='4',value.audit.events[0].revision='4';else if(field==='updated_by')value.audit.updated_by=AUTHOR,value.audit.events[0].executor_actor_id=AUTHOR;else if(field)value.audit[field]=field.includes('at')?'2026-10-26T11:02:00Z':A;if(field==='updated_by')value.actor_display.labels.pop();return response(value);}}));
  await p.start();detailPhase=true;await p.select(C);assert.equal(p.snapshot().kind,field?'unavailable':'detail',String(field));if(!field){assert.equal(p.snapshot().capture.answers[Q].value,3);assert.equal(p.snapshot().audit.current_revision,'3');}p.dispose();
 }
});

test('audit continuation replaces page and retains fresh matching header, opaque cursor and exact time',async()=>{
 let auditCalls=0;const p=createAdminPortal(config({request:async url=>{if(String(url).includes('audit-details')){auditCalls++;const limit=Number(new URL(String(url),'http://local').searchParams.get('limit'));if(auditCalls<3)return response(aggregate(detail(),limit,{events:limit===5?[3,2].map(r=>({revision:String(r),command_type:'capture.edit',executor_actor_id:EDITOR,initiator_actor_id:AUTHOR,recorded_at:detail().updated_at})):aggregate().audit.events}));return response(aggregate(detail(),5,{events:[{revision:'1',command_type:'capture.create',executor_actor_id:AUTHOR,initiator_actor_id:null,recorded_at:detail().created_at}]}));}return response(String(url).includes('?')?history():detail());}}));
 await p.start();await p.select(C);assert.equal(p.snapshot().audit.events.length,2);await p.auditPage(auditCursor(C,5,'2'));assert.equal(p.snapshot().kind,'detail');assert.equal(p.snapshot().audit.events.length,1);assert.equal(p.snapshot().audit.events[0].revision,'1');assert.equal(p.snapshot().audit.latest_modification.recorded_at,'2026-10-26T11:01:00.000001Z');p.dispose();
});

test('history Next and Back always read fresh bounded pages; return intent stays safe',async()=>{
 let seen=[];const p=createAdminPortal(config({request:async url=>{seen.push(String(url));if(String(url).includes('audit-details'))return response(aggregate(detail(),Number(new URL(String(url),'http://local').searchParams.get('limit'))));if(String(url).includes('?'))return response(history([detail()],{next_cursor:historyCursor()}));return response(detail());}}));
 await p.start();await p.select(C);await p.back();assert.equal(p.snapshot().kind,'history');assert.equal(p.snapshot().returnFocus,C);assert.equal(seen.filter(x=>x.startsWith('/api/v1/admin/captures?')).length,2);p.dispose();
});

for(const loss of ['refresh','offline','account','signout','org','dispose'])test(loss+' synchronously clears old data and fences ignored-abort late responses',async()=>{
 const auth=authFixture(),waiting=held();let delay=false;const p=createAdminPortal(config({auth:auth.port,request:async url=>delay?waiting.promise:response(String(url).includes('audit-details')?aggregate():history())}));
 await p.start();assert.equal(p.snapshot().kind,'history');delay=true;const work=p.select(C);assert.equal(p.snapshot().kind,'loading');
 if(loss==='refresh')void p.refresh();if(loss==='offline')p.online(false);if(loss==='account')auth.event('SIGNED_IN',OWNER);if(loss==='signout')void p.signOut();if(loss==='org')void p.replaceOrganization(Q);if(loss==='dispose')p.dispose();
 assert.ok(!JSON.stringify(p.snapshot()).includes('Original child'));waiting.resolve(response(detail()));await work;await tick();assert.ok(!JSON.stringify(p.snapshot()).includes('Original child'));p.dispose();assert.equal(auth.subscribed(),0);
});

test('loaded business state is synchronously removed on every Auth event and explicit fresh verification',async()=>{
 const auth=authFixture(),wait=held();let hold=false;const p=createAdminPortal(config({auth:auth.port,request:async url=>hold?wait.promise:response(String(url).includes('audit-details')?aggregate():history())}));await p.start();hold=true;auth.event();assert.equal(p.snapshot().kind,'checking');assert.ok(!JSON.stringify(p.snapshot()).includes('Original child'));p.dispose();wait.resolve(response(history()));
});

test('reconnect checks all-read and denial differs from service unavailability without own fallback',async()=>{
 for(const [status,id,kind] of [[403,'access_denied','denied'],[401,'authentication_required','signed_out'],[503,'authorization_unavailable','unavailable']]){
  let fail=false;const calls=[],p=createAdminPortal(config({request:async url=>{calls.push(String(url));return fail?failure(status,id):response(String(url).includes('audit-details')?aggregate():history());}}));await p.start();p.online(false);assert.equal(p.snapshot().kind,'offline');fail=true;await p.online(true);assert.equal(p.snapshot().kind,kind);assert.ok(calls.every(x=>x.startsWith('/api/v1/admin/captures')));p.dispose();
 }
});

test('one deadline bounds initial history and enrichment; Retry repeats complete reads only explicitly',async()=>{
 let calls=0,slow=true;const p=createAdminPortal(config({timeoutMs:40,request:async url=>{calls++;await new Promise(r=>setTimeout(r,slow?25:0));return response(String(url).includes('audit-details')?aggregate():history());}}));await p.start();assert.equal(p.snapshot().kind,'unavailable');const count=calls;await new Promise(r=>setTimeout(r,50));assert.equal(calls,count);slow=false;await p.retry();assert.equal(p.snapshot().kind,'history');assert.equal(calls,count+2);p.dispose();
});

for(const outcome of [null,{code:'synthetic_logout_failure'}])test('pending signout fence survives reconnect and owner replacement; late '+(outcome?'error':'success')+' cannot reopen',async()=>{
 const auth=authFixture(),logout=held();let calls=0;
 auth.port.signOut=()=>logout.promise;
 const p=createAdminPortal(config({auth:auth.port,request:async url=>{calls++;return response(String(url).includes('audit-details')?aggregate():history());}}));
 await p.start();const originalCalls=calls,work=p.signOut();assert.equal(p.snapshot().kind,'signed_out');
 await p.online(false);await p.online(true);await p.replaceOrganization(O);await p.refresh();auth.event();await tick();
 assert.equal(p.snapshot().kind,'signed_out');assert.equal(calls,originalCalls);
 logout.resolve({error:outcome});await work;await tick();assert.equal(p.snapshot().kind,'signed_out');assert.equal(calls,originalCalls);
 await p.retry();assert.equal(p.snapshot().kind,'history');assert.equal(calls,originalCalls+2);p.dispose();
});

for(const outcome of [null,{code:'synthetic_logout_failure'}])test('old logout '+(outcome?'error':'success')+' cannot clear a newer signout fence after deliberate reentry',async()=>{
 const auth=authFixture(),first=held(),second=held();let logouts=0,calls=0;
 auth.port.signOut=()=>++logouts===1?first.promise:second.promise;
 const p=createAdminPortal(config({auth:auth.port,request:async url=>{calls++;return response(String(url).includes('audit-details')?aggregate():history());}}));
 await p.start();const old=p.signOut();await tick();await p.signIn();assert.equal(p.snapshot().kind,'history');
 const latest=p.signOut();await tick();const before=calls;await p.online(false);await p.online(true);
 first.resolve({error:outcome});await old;assert.equal(p.snapshot().kind,'signed_out');assert.equal(calls,before);
 second.resolve({error:null});await latest;assert.equal(p.snapshot().kind,'signed_out');await p.retry();assert.equal(p.snapshot().kind,'history');p.dispose();
});
