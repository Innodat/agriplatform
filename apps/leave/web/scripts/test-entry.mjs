// GENERATED consuming owner transition tests. Native/browser evidence remains separate.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createSelectionController} from '../src/leave-controller.ts';
import {createLeaveClient} from '../src/api/leave.ts';
const org='11111111-1111-4111-8111-111111111111',operation='22222222-2222-4222-8222-222222222222',event='33333333-3333-4333-8333-333333333333';
const receipt={operation_id:operation,status:'committed',result:{command:'select_organization',org_id:org,event_id:event}};
function fixture(client){let current=true;const controller=new AbortController(),states=[];const session={access_token:'private',account_id:'account'};const lease={session,context:{},signal:controller.signal,isCurrent:()=>current,release(){}};return{states,controller:createSelectionController({client,acquire:()=>lease,publish:s=>states.push(s),newId:()=>operation}),revoke(){current=false;controller.abort();}};}
test('Stay rejects a late committed selection',async()=>{let resolve;const f=fixture({select:()=>new Promise(r=>resolve=r)});const work=f.controller.select(org);f.controller.stay();resolve({ok:true,value:receipt});await work;assert.equal(f.states.at(-1).kind,'idle');});
test('account/token invalidation rejects late response',async()=>{let resolve;const f=fixture({select:()=>new Promise(r=>resolve=r)});const work=f.controller.select(org);f.revoke();resolve({ok:true,value:receipt});await work;assert.equal(f.states.at(-1).kind,'working');});
test('lost response recovers original operation and receipt',async()=>{const seen=[];const f=fixture({select:async(_t,_s,_o,op)=>{seen.push(op);return{ok:false,error_id:'api_unavailable'};},lookup:async(_t,_s,_o,op)=>{seen.push(op);return{ok:true,value:receipt};}});await f.controller.select(org);assert.equal(f.states.at(-1).kind,'unresolved');await f.controller.retry();assert.equal(f.states.at(-1).kind,'committed');assert.deepEqual(seen,[operation,operation]);});
test('current denial cannot disclose historical outcome',async()=>{const f=fixture({select:async()=>({ok:false,error_id:'access_denied'})});await f.controller.select(org);assert.equal(f.states.at(-1).kind,'denied');assert.equal(f.states.at(-1).receipt,undefined);});
test('independent tab controllers retain independent selection',async()=>{const one=fixture({select:async()=>({ok:true,value:receipt})}),two=fixture({select:async()=>({ok:true,value:receipt})});await one.controller.select(org);assert.equal(two.states.length,0);assert.equal(one.states.at(-1).kind,'committed');});
test('all discovery pages and empty listing use Leave API',async()=>{const second='44444444-4444-4444-8444-444444444444',requests=[];let count=0;const client=createLeaveClient(async(url)=>{requests.push(url);return Response.json(++count===1?{organizations:[{org_id:org,name:'For profit',membership_id:'19'}],next_cursor:btoa(org)}:{organizations:[{org_id:second,name:'Organization two',membership_id:'20'}],next_cursor:null});});const r=await client.organizations('private',new AbortController().signal);assert.equal(r.ok,true);assert.equal(r.value.organizations.length,2);assert.ok(requests.every(p=>p.startsWith('/api/v1/me/organizations')));const empty=await createLeaveClient(async()=>Response.json({organizations:[],next_cursor:null})).organizations('x',new AbortController().signal);assert.deepEqual(empty.value.organizations,[]);});
test('discovery outage cannot fabricate eligibility',async()=>{const r=await createLeaveClient(async()=>Response.json({error_id:'authorization_unavailable',error:'Unavailable',details:{}},{status:503})).organizations('x',new AbortController().signal);assert.deepEqual(r,{ok:false,error_id:'authorization_unavailable'});});
test('preference preserves operation revision and desired locale over English presentation',async()=>{const calls=[];const client=createLeaveClient(async(_url,options)=>{calls.push(JSON.parse(options.body));return Response.json({preferred_locale:'pt',revision:'9'});});const command={operation_id:operation,expected_revision:'8',preferred_locale:'pt'};const result=await client.setLanguage('x',new AbortController().signal,command);assert.deepEqual(calls,[command]);assert.deepEqual(result.value,{preferred_locale:'pt',revision:'9'});});
test('recovery deadline settles unresolved and releases its lease',async(t)=>{
 t.mock.timers.enable({apis:['setTimeout']});let released=0;const states=[];const signal=new AbortController().signal;
 const c=createSelectionController({newId:()=>operation,acquire:()=>({session:{access_token:'x'},signal,isCurrent:()=>true,release(){released++;}}),client:{select:async(_t,signal)=>new Promise(resolve=>signal.addEventListener('abort',()=>resolve({ok:false,error_id:'api_unavailable'})))},publish:s=>states.push(s)});
 const work=c.select(org);t.mock.timers.tick(15001);await work;assert.equal(states.at(-1).kind,'unresolved');assert.equal(released,1);
});
test('a definitive retry denial stops recovery before another lookup',async()=>{
 let lookups=0,selects=0;const f=fixture({select:async()=>++selects===1?{ok:false,error_id:'api_unavailable'}:{ok:false,error_id:'access_denied'},lookup:async()=>{lookups++;return{ok:true,value:{operation_id:operation,status:'unresolved'}};}});
 await f.controller.select(org);await f.controller.retry();assert.equal(f.states.at(-1).kind,'denied');assert.equal(lookups,1);
});

test('renewal reuses acknowledged tab context without another selection',async()=>{
 const {createEntryNavigation}=await import('../src/leave-controller.ts');const n=createEntryNavigation();const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',choices=[{org_id:org,name:'One',membership_id:'1'}],location={pathname:'/',search:'',hash:''};
 assert.deepEqual(await n.target(account,choices,location,async()=>null),{kind:'select',org});n.establish(account,org);
 assert.deepEqual(await n.target(account,choices,location,async()=>{throw Error('ordinary renewal must not restore');}),{kind:'established',org});
});
test('same-user return freshly observes account/scope and requests audited selection',async()=>{
 const {createEntryNavigation}=await import('../src/leave-controller.ts');const n=createEntryNavigation();const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',choices=[{org_id:org,name:'One',membership_id:'1'}];n.establish(account,org);n.suspend();let calls=0;
 assert.deepEqual(await n.target(account,choices,{pathname:'/',search:'',hash:''},async scope=>{calls++;return{account_id:account,scope_id:scope};}),{kind:'select',org});assert.equal(calls,1);
});
test('foreign-account return reveals no prior organization; validated deep links need selection',async()=>{
 const {createEntryNavigation}=await import('../src/leave-controller.ts');const n=createEntryNavigation();const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',other='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';n.establish(account,org);n.suspend();
 assert.deepEqual(await n.target(other,[],{pathname:'/',search:'',hash:''},async scope=>({account_id:other,scope_id:scope})),{kind:'none'});
 assert.deepEqual(await n.target(other,[{org_id:org,name:'Current',membership_id:'1'}],{pathname:'/organizations/'+org,search:'',hash:''},async()=>null),{kind:'select',org});
 assert.deepEqual(await n.target(other,[],{pathname:'//outside.example',search:'?secret=x',hash:''},async()=>null),{kind:'none'});
});
test('language revision conflict retains desired locale and retries with a new operation',async()=>{
 const {createLanguageController}=await import('../src/leave-controller.ts');const commands=[],states=[];let gets=0,ids=0;
 const c=createLanguageController({newId:()=>`operation-${++ids}`,acquire:()=>({session:{access_token:'x'},signal:new AbortController().signal,isCurrent:()=>true,release(){}}),publish:s=>states.push(s),client:{language:async()=>({ok:true,value:{preferred_locale:'en',revision:++gets===1?'0':'4'}}),setLanguage:async(_t,_s,command)=>{commands.push(command);return commands.length===1?{ok:false,error_id:'identity.preference_revision_conflict'}:{ok:true,value:{preferred_locale:command.preferred_locale,revision:'5'}};}}});
 await c.load();await c.change('pt');assert.equal(states.at(-1).desired,'pt');assert.equal(states.at(-1).language.preferred_locale,'en');await c.retry();assert.deepEqual(commands,[{operation_id:'operation-1',expected_revision:'0',preferred_locale:'pt'},{operation_id:'operation-2',expected_revision:'4',preferred_locale:'pt'}]);assert.equal(states.at(-1).language.preferred_locale,'pt');
});

for(const method of ['select','lookup'])for(const mismatch of ['operation','organization','unresolved-operation'])test(`${method} rejects otherwise-valid ${mismatch} response binding`,async()=>{
 const foreign='55555555-5555-4555-8555-555555555555';
 const value=mismatch==='unresolved-operation'?{operation_id:foreign,status:'unresolved'}:structuredClone(receipt);
 if(mismatch==='operation')value.operation_id=foreign;if(mismatch==='organization')value.result.org_id=foreign;
 const client=createLeaveClient(async()=>Response.json(value,{status:mismatch==='unresolved-operation'?202:200}));
 assert.deepEqual(await client[method]('private',new AbortController().signal,org,operation),{ok:false,error_id:'invalid_response'});
});
test('foreign receipt through real client cannot publish a committed transition',async()=>{
 const foreign={...receipt,operation_id:'55555555-5555-4555-8555-555555555555'};
 const f=fixture(createLeaveClient(async()=>Response.json(foreign)));
 await f.controller.select(org);await f.controller.retry();
 assert.equal(f.states.at(-1).kind,'unresolved');assert.equal(f.states.some(s=>s.kind==='committed'),false);assert.equal(f.states.at(-1).receipt,undefined);
});
test('document return intent is account-bound, consumed once and rechecks scope before selection',async()=>{
 const {createEntryNavigation}=await import('../src/leave-controller.ts');const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',other='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',choices=[{org_id:org,name:'One',membership_id:'1'}],location={pathname:'/',search:'',hash:''};
 const before=createEntryNavigation();before.establish(account,org);before.suspend();const serialized=JSON.stringify(before.returnIntent());
 const after=createEntryNavigation();after.resume(JSON.parse(serialized));let observed=0;
 assert.deepEqual(await after.target(account,choices,location,async scope=>{observed++;return{account_id:account,scope_id:scope};}),{kind:'select',org});assert.equal(observed,1);assert.equal(after.returnIntent(),null);
 after.resume(JSON.parse(serialized));assert.deepEqual(await after.target(other,choices,location,async scope=>({account_id:other,scope_id:scope})),{kind:'none'});
 after.resume(JSON.parse(serialized));assert.deepEqual(await after.target(account,[],location,async()=>null),{kind:'none'});
 assert.equal(after.resume({...JSON.parse(serialized),extra:'foreign'}),false);
});

test('cancelled and overlapping return observations preserve pending identity for the current lease',async()=>{
 const {createEntryNavigation}=await import('../src/leave-controller.ts');
 const account='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',other='55555555-5555-4555-8555-555555555555',choices=[{org_id:org,name:'One',membership_id:'1'},{org_id:other,name:'Two',membership_id:'2'}],location={pathname:'/',search:'',hash:''};
 const n=createEntryNavigation(),intent={account_id:account,scope_id:org};n.resume(intent);
 const first=new AbortController();let releaseFirst,startedFirst;const started=new Promise(resolve=>{startedFirst=resolve;});
 const abandoned=n.target(account,choices,location,()=>{startedFirst();return new Promise(resolve=>{releaseFirst=resolve;});},{signal:first.signal,isCurrent:()=>!first.signal.aborted});
 await started;first.abort();assert.deepEqual(await abandoned,{kind:'none'});assert.deepEqual(n.returnIntent(),intent);
 let releaseCurrent,startedCurrent;const observing=new Promise(resolve=>{startedCurrent=resolve;});
 const replacement=n.target(account,choices,location,()=>{startedCurrent();return new Promise(resolve=>{releaseCurrent=resolve;});});await observing;
 releaseFirst({account_id:account,scope_id:org});await Promise.resolve();assert.deepEqual(n.returnIntent(),intent);
 releaseCurrent({account_id:account,scope_id:org});assert.deepEqual(await replacement,{kind:'select',org});assert.equal(n.returnIntent(),null);
 assert.deepEqual(await n.target(account,choices,location,async()=>{throw Error('consumed return must not observe again');}),{kind:'none'});
 // A late older observation must not clear a newly captured return identity.
 n.resume(intent);let releaseOld,startedOld;const oldStarted=new Promise(resolve=>{startedOld=resolve;});
 const old=n.target(account,choices,location,()=>{startedOld();return new Promise(resolve=>{releaseOld=resolve;});});await oldStarted;
 const newer={account_id:account,scope_id:other};n.resume(newer);releaseOld(null);assert.deepEqual(await old,{kind:'none'});assert.deepEqual(n.returnIntent(),newer);
 assert.deepEqual(await n.target(account,choices,location,async scope=>({account_id:account,scope_id:scope})),{kind:'select',org:other});assert.equal(n.returnIntent(),null);
});
