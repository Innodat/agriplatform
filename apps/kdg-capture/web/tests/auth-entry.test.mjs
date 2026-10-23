import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createAuthEntry,createEntryReturn,createEntryOAuth} from '../../../../compiled/web/src/auth-entry.js';
import {createKdgEmailAuth} from '../../../../compiled/web/src/email-auth.js';
import {createEmailCodeController} from '../../../../compiled/web/src/auth/lifecycle.js';
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';
const session=(id=A,token='synthetic-'+id)=>({user:{id},access_token:token});
const context=id=>({account_id:id,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:id},permission:'kdg_capture.capture.read.own',decision_id:'55555555-5555-4555-8555-555555555555',checked_at:'2026-10-23T10:00:00Z'});
const reply=id=>new Response(JSON.stringify(context(id)));
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
const tick=()=>new Promise(r=>setTimeout(r,0));
function fixture(overrides={},options={}){
 let cb,current=session(),unsubscribed=0;const states=[],calls=[];
 const auth={getSession:async()=>({data:{session:current},error:null}),refreshSession:async()=>({data:{session:current},error:null}),signOut:async(options)=>{calls.push(options);current=null;cb('SIGNED_OUT',null);return{error:null};},onAuthStateChange:callback=>{cb=callback;return{data:{subscription:{unsubscribe(){unsubscribed++;}}}};},...overrides};
 const gate=createAuthEntry({org:ORG,auth,publish:s=>states.push(s),beginSignIn:async()=>{calls.push('interactive');},request:async(_url,init)=>reply(init.headers.Authorization.includes(B)?B:A),timeoutMs:50,...options});
 return{gate,auth,states,calls,emit(event,s){current=s;cb(event,s);},unsubscribed:()=>unsubscribed};
}
test('current SDK session admits only through the KDG context boundary',async()=>{
 const f=fixture();await f.gate.start();assert.equal(f.gate.state().kind,'authorized');assert.equal(f.gate.state().context.account_id,A);f.gate.dispose();
});

test('subscribe before lookup; newer account beats an old bootstrap result',async()=>{
 const pending=deferred(),f=fixture({getSession:()=>pending.promise});const old=f.gate.start();
 f.emit('SIGNED_IN',session(B));assert.notEqual(f.gate.state().kind,'authorized');await old;await tick();
 assert.equal(f.gate.state().context.account_id,B);pending.resolve({data:{session:session(A)},error:null});await tick();
 assert.equal(f.gate.state().context.account_id,B);f.gate.dispose();
});
test('late INITIAL_SESSION cannot replace a live sign-in',async()=>{
 const f=fixture();await f.gate.start();f.emit('SIGNED_IN',session(B));await tick();f.emit('INITIAL_SESSION',session(A));await tick();
 assert.equal(f.gate.state().context.account_id,B);f.gate.dispose();
});
test('token refresh clears admission synchronously and uses the new bearer',async()=>{
 const tokens=[],f=fixture({}, {request:async(_,init)=>{tokens.push(init.headers.Authorization);return reply(A);}});
 await f.gate.start();f.emit('TOKEN_REFRESHED',session(A,'fresh-token'));assert.notEqual(f.gate.state().kind,'authorized');await tick();
 assert.equal(f.gate.state().kind,'authorized');assert.equal(tokens.at(-1),'Bearer fresh-token');f.gate.dispose();
});
test('local sign-out clears immediately, stays latched against late sessions and unsubscribes',async()=>{
 const f=fixture();await f.gate.start();const out=f.gate.signOut();assert.equal(f.gate.state().kind,'signed_out');await out;
 assert.deepEqual(f.calls,[{scope:'local'}]);f.emit('TOKEN_REFRESHED',session(A));await tick();assert.equal(f.gate.state().kind,'signed_out');
 f.gate.dispose();assert.equal(f.unsubscribed(),1);
});
test('timeout resolves ignored SDK work and latches out its late result/event',async()=>{
 const pending=deferred(),f=fixture({getSession:()=>pending.promise},{timeoutMs:10});await f.gate.start();
 assert.equal(f.gate.state().kind,'authorization_unavailable');pending.resolve({data:{session:session(A)},error:null});f.emit('SIGNED_IN',session(A));await tick();
 assert.equal(f.gate.state().kind,'authorization_unavailable');f.gate.dispose();
});
test('disposal settles ignored work, unsubscribes and forbids late publication',async()=>{
 const pending=deferred(),f=fixture({getSession:()=>pending.promise});const start=f.gate.start();f.gate.dispose();await start;
 const count=f.states.length;pending.resolve({data:{session:session(A)},error:null});f.emit('SIGNED_IN',session(B));await tick();
 assert.equal(f.states.length,count);assert.equal(f.unsubscribed(),1);assert.equal(f.gate.state().kind,'signed_out');
});
test('explicit sign-in refreshes once; a refresh event supersedes its return',async()=>{
 let f;f=fixture({refreshSession:async()=>{f.emit('TOKEN_REFRESHED',session(A,'refreshed'));return{data:{session:session(A,'older')},error:null};}});
 await f.gate.start();await f.gate.signIn();await tick();assert.equal(f.gate.state().kind,'authorized');assert.ok(!f.calls.includes('interactive'));f.gate.dispose();
});
test('interactive launch completion alone never establishes admission',async()=>{
 const f=fixture({getSession:async()=>({data:{session:null},error:null})});await f.gate.start();await f.gate.signIn();
 assert.deepEqual(f.calls,['interactive']);assert.equal(f.gate.state().kind,'authentication_required');f.gate.dispose();
});
test('refresh failure launches interactive owner action once without leaking raw errors',async()=>{
 const f=fixture({refreshSession:async()=>({data:{session:null},error:{message:'SENSITIVE'}})});await f.gate.start();await f.gate.signIn();
 assert.deepEqual(f.calls,['interactive']);assert.equal(f.gate.state().kind,'authentication_required');assert.ok(!JSON.stringify(f.states).includes('SENSITIVE'));f.gate.dispose();
});
test('sign-out failure is unavailable and never restores prior admission',async()=>{
 const f=fixture({signOut:async()=>({error:{message:'SENSITIVE'}})});await f.gate.start();await f.gate.signOut();
 assert.equal(f.gate.state().kind,'authorization_unavailable');f.emit('SIGNED_IN',session(B));await tick();assert.equal(f.gate.state().kind,'authorization_unavailable');f.gate.dispose();
});
test('offline bridge performs no context request',async()=>{
 let requests=0;const f=fixture({}, {online:false,request:async()=>{requests++;return reply(A);}});await f.gate.start();f.emit('SIGNED_IN',session(A));await tick();await f.gate.retry();await f.gate.signIn();
 assert.equal(requests,0);assert.notEqual(f.gate.state().kind,'authorized');f.gate.dispose();
});
test('SDK session error and synchronous subscription exception fail safely',async()=>{
 for(const overrides of [{getSession:async()=>({data:{session:null},error:{message:'SENSITIVE'}})}, {onAuthStateChange:()=>{throw new Error('SENSITIVE');}}]){
  const f=fixture(overrides);await f.gate.start();assert.equal(f.gate.state().kind,'authorization_unavailable');assert.ok(!JSON.stringify(f.states).includes('SENSITIVE'));f.gate.dispose();
 }
});
test('synchronous subscription event is not overwritten by bootstrap',async()=>{
 let reads=0;const f=fixture({getSession:async()=>{reads++;return{data:{session:session(A)},error:null};},onAuthStateChange:callback=>{callback('SIGNED_IN',session(B));return{data:{subscription:{unsubscribe(){}}}};}});
 await f.gate.start();await tick();assert.equal(reads,0);assert.equal(f.gate.state().context.account_id,B);f.gate.dispose();
});
test('password recovery cannot establish ordinary app admission',async()=>{
 const f=fixture();await f.gate.start();f.emit('PASSWORD_RECOVERY',session(A));await tick();assert.equal(f.gate.state().kind,'authentication_required');f.gate.dispose();
});

test('actual SDK2.117.3 refresh and local logout use only injected synthetic Auth fetch',async()=>{
 const {createClient}=await import('@supabase/supabase-js');
 const values=new Map(),calls=[],now=Math.floor(Date.now()/1000);
 const token=counter=>Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:A,exp:now+3600,iat:now,aud:'authenticated',counter})).toString('base64url')+'.c3ludGhldGlj';
 const sdkSession=counter=>({access_token:token(counter),refresh_token:'synthetic-refresh',expires_at:now+3600,expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',role:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}});
 values.set('kdg-synthetic-auth',JSON.stringify(sdkSession(1)));
 const client=createClient('https://synthetic-auth.invalid','synthetic-public-key',{
  auth:{storageKey:'kdg-synthetic-auth',storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},autoRefreshToken:false,detectSessionInUrl:false,debug:false},
  global:{fetch:async(input,init)=>{const path=new URL(String(input)).pathname;calls.push({path,method:init.method});
   if(path==='/auth/v1/token')return new Response(JSON.stringify(sdkSession(2)),{headers:{'content-type':'application/json'}});
   if(path==='/auth/v1/logout')return new Response(null,{status:204});throw new Error('unexpected synthetic request');
  }},
 });
 const published=[];const gate=createAuthEntry({org:ORG,auth:client.auth,publish:s=>published.push(s.kind),beginSignIn:async()=>{},request:async()=>reply(A),timeoutMs:1000});
 await gate.start();await tick();assert.equal(gate.state().kind,'authorized');
 await client.auth.refreshSession();await tick();assert.equal(gate.state().kind,'authorized');
 await gate.signOut();assert.equal(gate.state().kind,'signed_out');assert.equal((await client.auth.getSession()).data.session,null);
 assert.deepEqual(calls,[{path:'/auth/v1/token',method:'POST'},{path:'/auth/v1/logout',method:'POST'}]);
 assert.equal(values.size,0);gate.dispose();client.auth.stopAutoRefresh();
 assert.ok(published.includes('authorized'));
});

test('a refreshed session still rejected as unauthenticated launches owner sign-in once',async()=>{
 let f;f=fixture({refreshSession:async()=>{f.emit('TOKEN_REFRESHED',session(A,'fresh'));return{data:{session:session(A,'fresh')},error:null};}},
  {request:async()=>new Response(JSON.stringify({error_id:'authentication_required'}),{status:401})});
 await f.gate.start();await f.gate.signIn();await tick();assert.deepEqual(f.calls,['interactive']);assert.equal(f.gate.state().kind,'authentication_required');f.gate.dispose();
});
test('SIGNED_OUT during failed refresh requires another explicit sign-in action',async()=>{
 let f;f=fixture({refreshSession:async()=>{f.emit('SIGNED_OUT',null);return{data:{session:null},error:{message:'SENSITIVE'}};}});
 await f.gate.start();await f.gate.signIn();await tick();assert.deepEqual(f.calls,[]);assert.equal(f.gate.state().kind,'signed_out');await f.gate.signIn();assert.deepEqual(f.calls,['interactive']);f.gate.dispose();
});
test('late refresh for a previous account cannot replace a new sign-in',async()=>{
 const f=fixture();await f.gate.start();f.emit('SIGNED_IN',session(B));f.emit('TOKEN_REFRESHED',session(A));await tick();
 assert.notEqual(f.gate.state().kind,'authorized');f.gate.dispose();
});

test('interactive fallback remains checking and suppresses duplicate sign-in while pending',async()=>{
 const launch=deferred();let launches=0;
 const f=fixture({refreshSession:async()=>({data:{session:session(A)},error:null})},{
  request:async()=>new Response(JSON.stringify({error_id:'authentication_required'}),{status:401}),
  beginSignIn:()=>{launches++;return launch.promise;},
 });
 await f.gate.start();const pending=f.gate.signIn();await tick();assert.equal(f.gate.state().kind,'checking');
 const duplicate=f.gate.signIn();await tick();assert.equal(launches,1);launch.resolve();await pending;await duplicate;f.gate.dispose();
});

test('synchronous subscription callback disposal detaches the returned subscription',async()=>{
 let f,unsubscribed=0;f=fixture({onAuthStateChange:callback=>{callback('SIGNED_IN',session(A));return{data:{subscription:{unsubscribe(){unsubscribed++;}}}};}}, {publish:()=>f.gate.dispose()});
 await f.gate.start();assert.equal(unsubscribed,1);assert.equal(f.gate.state().kind,'signed_out');
});
test('concurrent logout during refresh cancels recovery without an interactive launch',async()=>{
 const pending=deferred(),f=fixture({refreshSession:()=>pending.promise});await f.gate.start();const recovery=f.gate.signIn();await tick();
 f.emit('SIGNED_OUT',null);await tick();assert.equal(f.gate.state().kind,'signed_out');assert.deepEqual(f.calls,[]);
 pending.resolve({data:{session:session(A)},error:null});await recovery;await tick();assert.equal(f.gate.state().kind,'signed_out');f.gate.dispose();
});


test('mismatched refresh result latches closed against subsequent events until explicit retry',async()=>{
 const f=fixture({refreshSession:async()=>({data:{session:session(B)},error:null})});await f.gate.start();await f.gate.signIn();
 assert.equal(f.gate.state().kind,'authentication_required');f.emit('TOKEN_REFRESHED',session(B));await tick();assert.equal(f.gate.state().kind,'authentication_required');
 await f.gate.retry();assert.equal(f.gate.state().context.account_id,B);f.gate.dispose();
});
for(const phase of ['refresh','interactive','signOut'])test('deadline bounds '+phase+' and rejects late completions/events',async()=>{
 const pending=deferred();let f,observed=null;
 const overrides=phase==='refresh'?{refreshSession:()=>pending.promise}:phase==='signOut'?{signOut:()=>pending.promise}:{getSession:async()=>({data:{session:observed},error:null})};
 f=fixture(overrides,{timeoutMs:10,...(phase==='interactive'?{beginSignIn:()=>pending.promise}:{})});await f.gate.start();
 await (phase==='signOut'?f.gate.signOut():f.gate.signIn());assert.equal(f.gate.state().kind,'authorization_unavailable');
 pending.resolve({data:{session:session(A)},error:null});f.emit('TOKEN_REFRESHED',session(A));await tick();assert.equal(f.gate.state().kind,'authorization_unavailable');
 observed=session(A);await f.gate.retry();assert.equal(f.gate.state().kind,'authorized');f.gate.dispose();
});

for(const expired of [false,true])test('actual SDK rejected refresh; expired='+expired,async()=>{
 const {createClient}=await import('@supabase/supabase-js');const values=new Map(),now=Math.floor(Date.now()/1000);let launches=0;
 values.set('kdg-rejected-auth',JSON.stringify({access_token:'synthetic',refresh_token:'synthetic-refresh',expires_at:now+3600,expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}));
 const client=createClient('https://synthetic-auth.invalid','synthetic-public-key',{auth:{storageKey:'kdg-rejected-auth',storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},autoRefreshToken:false,detectSessionInUrl:false,debug:false},
  global:{fetch:async()=>new Response(JSON.stringify({code:'refresh_token_not_found',msg:'SENSITIVE'}),{status:400,headers:{'content-type':'application/json','x-supabase-api-version':'2024-01-01'}})}});
 const events=[];const listener=client.auth.onAuthStateChange(event=>{events.push(event);}).data.subscription;
 const gate=createAuthEntry({org:ORG,auth:client.auth,publish:()=>{},beginSignIn:async()=>{launches++;},request:async()=>reply(A),timeoutMs:1000});
 await gate.start();await tick();
 if(expired){const stored=JSON.parse(values.get('kdg-rejected-auth'));stored.expires_at=now-1;values.set('kdg-rejected-auth',JSON.stringify(stored));}
 await gate.signIn();await tick();
 if(expired){assert.equal(gate.state().kind,'signed_out');assert.ok(events.includes('SIGNED_OUT'));assert.equal(launches,0);await gate.signIn();assert.equal(launches,1);}
 else{assert.equal(gate.state().kind,'authentication_required');assert.ok(!events.includes('SIGNED_OUT'));assert.equal(launches,1);}
 assert.equal(gate.state().kind,'authentication_required');gate.dispose();listener.unsubscribe();client.auth.stopAutoRefresh();
});

test('KDG return selection rechecks the current private context before restoring entry',async()=>{
 const calls=[],guard=createEntryReturn({org:ORG,request:async(path,init)=>{calls.push({path,init});return reply(A);}});
 assert.equal(guard.capture('/',context(A)),true);
 assert.deepEqual(await guard.restore({account_id:A,access_token:'synthetic-current'}),{kind:'restored',path:'/'});
 assert.equal(calls.length,1);assert.equal(calls[0].path,'/api/v1/context');assert.equal(calls[0].init.headers.Authorization,'Bearer synthetic-current');
 assert.equal(calls[0].init.cache,'no-store');assert.equal(calls[0].init.redirect,'error');guard.dispose();
});

test('KDG return target is limited to entry; invalid capture clears earlier intent without HTTP',async()=>{
 let requests=0;const guard=createEntryReturn({org:ORG,request:async()=>{requests++;return reply(A);}});
 for(const path of ['/captures','/auth/callback','/?account='+B,'https://evil.invalid/','//evil.invalid','/%2f','/#PRIVATE']){
  guard.capture('/',context(A));assert.equal(guard.capture(path,context(A)),false);assert.deepEqual(await guard.restore({account_id:A,access_token:'synthetic'}),{kind:'safe',path:'/'});
 }
 assert.equal(requests,0);guard.dispose();
});
test('KDG return selection protects changed account, organization, revoked access, outage and malformed evidence',async()=>{
 for(const [account,response] of [[B,()=>reply(B)],[A,()=>new Response(JSON.stringify(context(A)),{status:403})],[A,()=>new Response('PRIVATE',{status:503})],[A,()=>new Response('{}')],[A,()=>new Response(JSON.stringify({...context(A),authorization_scope:{kind:'organization',org_id:B}}))]]){
  const guard=createEntryReturn({org:ORG,request:async()=>response()});guard.capture('/',context(A));
  assert.deepEqual(await guard.restore({account_id:account,access_token:'synthetic'}),{kind:'safe',path:'/'});guard.dispose();
 }
 const guard=createEntryReturn({org:ORG,request:async()=>{throw new Error('must not call');}});
 assert.equal(guard.capture('/',{...context(A),authorization_scope:{kind:'organization',org_id:B}}),false);
 guard.capture('/',context(A));assert.deepEqual(await guard.restore(null),{kind:'safe',path:'/'});guard.dispose();
});
test('KDG return cancellation aborts in-flight current-context work and prevents late restoration',async()=>{
 const pending=deferred();let signal;const guard=createEntryReturn({org:ORG,request:async(_path,init)=>{signal=init.signal;return pending.promise;}});
 guard.capture('/',context(A));const result=guard.restore({account_id:A,access_token:'synthetic'});await tick();guard.clear();
 assert.deepEqual(await result,{kind:'safe',path:'/'});assert.equal(signal.aborted,true);pending.resolve(reply(A));await tick();guard.dispose();
});

test('KDG return pins the supplied account and bearer before deferred verification',async()=>{
 const tokens=[],guard=createEntryReturn({org:ORG,request:async(_path,init)=>{tokens.push(init.headers.Authorization);return reply(init.headers.Authorization.includes(B)?B:A);}});
 guard.capture('/',context(A));const current={account_id:A,access_token:'synthetic-'+A};const result=guard.restore(current);
 current.account_id=B;current.access_token='synthetic-'+B;
 assert.deepEqual(await result,{kind:'restored',path:'/'});assert.deepEqual(tokens,['Bearer synthetic-'+A]);guard.dispose();
});
for(const stage of ['headers','body'])test(`KDG return deadline aborts stalled ${stage} and late success cannot restore`,async()=>{
 const pending=deferred();let signal,cancelled=0;
 const response=new Response(new ReadableStream({cancel(){cancelled++;}}));
 const guard=createEntryReturn({org:ORG,timeoutMs:5,request:async(_path,init)=>{signal=init.signal;return stage==='headers'?pending.promise:response;}});
 guard.capture('/',context(A));const result=await guard.restore({account_id:A,access_token:'synthetic'});
 assert.deepEqual(result,{kind:'safe',path:'/'});assert.equal(signal.aborted,true);
 if(stage==='headers')pending.resolve(response);await tick();assert.equal(cancelled,1);
 assert.deepEqual(await guard.restore({account_id:A,access_token:'synthetic'}),{kind:'safe',path:'/'});guard.dispose();
});

test('KDG OAuth callback consumes explicit SDK flow and requires current private context',async()=>{
 let stored=null;const calls=[],callbackUrl='https://app.invalid/auth/callback',authorizeUrl='https://auth.invalid/auth/v1/authorize';
 const flow=createEntryOAuth({org:ORG,authorizeUrl,callbackUrl,provider:'azure',scopes:'email',store:{read:()=>stored,write:value=>{stored=value;},take:()=>{const old=stored;stored=null;return old;}},pause:()=>calls.push('pause'),navigate:()=>calls.push('navigate'),scrub:()=>calls.push('scrub'),
 auth:{signInWithOAuth:async input=>{calls.push(input);return{data:{url:authorizeUrl+'?'+new URLSearchParams({provider:'azure',redirect_to:callbackUrl,scopes:'email',code_challenge:'a'.repeat(43),code_challenge_method:'s256'}),flowId:'syntheticFlow123'},error:null};},exchangeCodeForSession:async(code,options)=>{calls.push([code,options]);return{data:{session:session()},error:null};}},request:async()=>{calls.push('context');return reply(A);}});
 assert.deepEqual(await flow.launch(),{kind:'launched'});assert.equal((await flow.callback(callbackUrl+'?code=synthetic-code')).kind,'authorized');
 assert.ok(calls.includes('context'));assert.deepEqual(calls[1],{provider:'azure',options:{redirectTo:callbackUrl,scopes:'email',skipBrowserRedirect:true}});flow.dispose();
});

async function sdkOAuthFixture({failure=false,denied=false,delay}={}){
 const {createClient}=await import('@supabase/supabase-js');const {randomUUID}=await import('node:crypto');
 const values=new Map(),calls=[],key='synthetic-pkce-'+randomUUID(),now=Math.floor(Date.now()/1000);
 const access=Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:A,exp:now+3600,aud:'authenticated'})).toString('base64url')+'.c3ludGhldGlj';
 const client=createClient('https://synthetic-auth.invalid','synthetic-public-key',{
  auth:{flowType:'pkce',detectSessionInUrl:false,autoRefreshToken:false,debug:false,storageKey:key,storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}}},
  global:{fetch:async(input,init)=>{
   const url=new URL(String(input));assert.equal(url.origin,'https://synthetic-auth.invalid');assert.equal(url.pathname,'/auth/v1/token');assert.equal(url.searchParams.get('grant_type'),'pkce');
   const body=JSON.parse(init.body);assert.deepEqual(Object.keys(body).sort(),['auth_code','code_verifier']);calls.push({kind:'exchange',body});if(delay)await delay;
   if(failure)return new Response(JSON.stringify({error_code:'bad_code',message:'PRIVATE'}),{status:400,headers:{'content-type':'application/json'}});
   return new Response(JSON.stringify({access_token:access,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',role:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}),{headers:{'content-type':'application/json'}});
  }},
 });
 let stored=null;const options={org:ORG,auth:client.auth,authorizeUrl:'https://synthetic-auth.invalid/auth/v1/authorize',callbackUrl:'https://app.invalid/auth/callback',provider:'azure',scopes:'email',
  store:{read:()=>stored,write:value=>{stored=value;},take:()=>{const prior=stored;stored=null;return prior;}},pause:()=>calls.push({kind:'pause'}),navigate:url=>calls.push({kind:'navigate',url}),scrub:url=>calls.push({kind:'scrub',url}),
  request:async(_path,init)=>{calls.push({kind:'context'});assert.equal(init.headers.Authorization,'Bearer '+access);return denied?new Response(JSON.stringify({error_id:'access_denied'}),{status:403}):reply(A);}};
 return{client,values,calls,key,options,flow:createEntryOAuth(options),stored:()=>stored};
}
test('actual SDK PKCE launch/exchange binds its stored verifier, scrubs callback and rechecks KDG authority',async()=>{
 const f=await sdkOAuthFixture();assert.equal((await f.flow.launch()).kind,'launched');const record=f.stored(),slot=f.key+'-flow-'+record.flow_id+'-code-verifier';
 const verifier=JSON.parse(f.values.get(slot));const {createHash}=await import('node:crypto');
 const launched=f.calls.find(c=>c.kind==='navigate');assert.equal(new URL(launched.url).searchParams.get('code_challenge'),createHash('sha256').update(verifier).digest('base64url'));
 f.flow.dispose();const callback=createEntryOAuth(f.options);const result=await callback.callback(f.options.callbackUrl+'?code=synthetic-code');
 assert.equal(result.kind,'authorized');assert.equal(result.context.account_id,A);assert.equal(f.calls.find(c=>c.kind==='exchange').body.code_verifier,verifier);
 assert.ok(f.calls.findIndex(c=>c.kind==='scrub')<f.calls.findIndex(c=>c.kind==='exchange'));assert.equal(f.values.has(slot),false);assert.equal(f.calls.filter(c=>c.kind==='context').length,1);
 assert.equal((await callback.callback(f.options.callbackUrl+'?code=synthetic-code')).kind,'invalid_callback');assert.equal(f.calls.filter(c=>c.kind==='exchange').length,1);callback.dispose();f.client.auth.stopAutoRefresh();
});
for(const mode of ['failure','denied'])test('actual SDK callback '+mode+' cannot grant KDG admission or replay code',async()=>{
 const f=await sdkOAuthFixture({[mode]:true});await f.flow.launch();const result=await f.flow.callback(f.options.callbackUrl+'?code=synthetic-code');
 assert.equal(result.kind,mode==='failure'?'authentication_required':'access_denied');assert.ok(!JSON.stringify(result).includes('PRIVATE'));
 await f.flow.callback(f.options.callbackUrl+'?code=synthetic-code');assert.equal(f.calls.filter(c=>c.kind==='exchange').length,1);f.flow.dispose();f.client.auth.stopAutoRefresh();
});
test('actual SDK callback with absent explicit flow slot never borrows the latest verifier',async()=>{
 const f=await sdkOAuthFixture();await f.flow.launch();const record=f.stored();f.options.store.write({...record,flow_id:'absentFlow123'});
 assert.equal((await f.flow.callback(f.options.callbackUrl+'?code=synthetic-code')).kind,'authentication_required');assert.equal(f.calls.filter(c=>c.kind==='exchange').length,0);
 assert.equal(f.values.has(f.key+'-flow-'+record.flow_id+'-code-verifier'),true);f.flow.dispose();f.client.auth.stopAutoRefresh();
});

for(const action of ['timeout','dispose'])test('actual SDK late session write after callback '+action+' never invokes owner admission',async()=>{
 const pending=deferred(),f=await sdkOAuthFixture({delay:pending.promise});await f.flow.launch();f.flow.dispose();
 const callback=createEntryOAuth({...f.options,timeoutMs:action==='timeout'?5:50});const work=callback.callback(f.options.callbackUrl+'?code=synthetic-late');await tick();
 assert.equal(f.calls.filter(c=>c.kind==='exchange').length,1);if(action==='dispose')callback.dispose();
 assert.equal((await work).kind,action==='timeout'?'authorization_unavailable':'cancelled');pending.resolve();await tick();await tick();
 const current=await f.client.auth.getSession();assert.equal(current.data.session.user.id,A);assert.equal(f.values.has(f.key),true);assert.equal(f.calls.filter(c=>c.kind==='context').length,0);
 assert.notEqual((await work).kind,'authorized');callback.dispose();f.client.auth.stopAutoRefresh();
});

test('KDG OAuth pins owner configuration before asynchronous launch/callback work',async()=>{
 const f=await sdkOAuthFixture(),options={...f.options},flow=createEntryOAuth(options);await flow.launch();options.org=B;
 assert.equal((await flow.callback(f.options.callbackUrl+'?code=synthetic-config')).kind,'authorized');flow.dispose();f.flow.dispose();f.client.auth.stopAutoRefresh();
});

test('actual SDK email-code flow disables account creation and verifies email before current KDG admission',async()=>{
 const values=new Map(),calls=[],now=Math.floor(Date.now()/1000),token=Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:A,exp:now+3600,aud:'authenticated'})).toString('base64url')+'.c3ludGhldGlj';
 const auth=createKdgEmailAuth({url:'https://synthetic-auth.invalid',publicKey:'sb_publishable_synthetic_public_123456',storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},request:async(input,init)=>{
  const path=new URL(String(input)).pathname,body=JSON.parse(init.body);calls.push({path,body});
  if(path==='/auth/v1/otp')return new Response('{}',{headers:{'content-type':'application/json'}});
  assert.equal(path,'/auth/v1/verify');return new Response(JSON.stringify({access_token:token,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}),{headers:{'content-type':'application/json'}});
 }});
 const controller=createEmailCodeController({auth,publish:()=>{}});await controller.send('facilitator@example.invalid');assert.equal(controller.state().kind,'code');
 assert.equal(calls[0].body.create_user,false);await controller.verify('123456');assert.equal(controller.state().kind,'verified');
 assert.equal(calls[1].body.type,'email');assert.equal(calls[1].body.token,'123456');assert.ok(values.has('kdg-capture-auth'));
 controller.dispose();auth.stopAutoRefresh();
});

test('KDG email client refuses private keys, unsafe endpoints and unavailable storage before Auth I/O',()=>{
 let requests=0;const storage={getItem(){throw new Error('PRIVATE');},setItem(){},removeItem(){}},request=async()=>{requests++;throw new Error('must not request');};
 for(const [url,publicKey] of [['https://synthetic-auth.invalid','sb_secret_not_public'],['http://auth.example.invalid','sb_publishable_synthetic_public_123456'],['https://user:PRIVATE@auth.invalid','sb_publishable_synthetic_public_123456']])assert.throws(()=>createKdgEmailAuth({url,publicKey,storage,request}),{message:'auth_configuration_invalid'});
 assert.throws(()=>createKdgEmailAuth({url:'https://synthetic-auth.invalid',publicKey:'sb_publishable_synthetic_public_123456',storage,request}),{message:'auth_storage_unavailable'});assert.equal(requests,0);
});

for(const failure of ['setItem','getItem','removeItem'])test('actual SDK runtime '+failure+' failure closes the client without claiming persistence or logout',async()=>{
 const values=new Map();let broken=null;const storage={getItem:k=>{if(broken==='getItem')throw Error('PRIVATE');return values.get(k)??null;},setItem:(k,v)=>{if(broken==='setItem')throw Error('PRIVATE');values.set(k,v);},removeItem:k=>{if(broken==='removeItem')throw Error('PRIVATE');values.delete(k);}};
 const token=Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:A,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})).toString('base64url')+'.c3ludGhldGlj';
 const auth=createKdgEmailAuth({url:'https://synthetic-auth.invalid',publicKey:'sb_publishable_synthetic_public_123456',storage,request:async input=>new URL(String(input)).pathname.endsWith('/logout')?new Response(null,{status:204}):new Response(JSON.stringify({access_token:token,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}),{headers:{'content-type':'application/json'}})});
 await auth.getSession();
 if(failure==='setItem'){
  broken=failure;const controller=createEmailCodeController({auth,publish:()=>{}});await controller.send('facilitator@example.invalid');await controller.verify('123456');assert.notEqual(controller.state().kind,'verified');assert.equal(controller.state().notice,'unavailable');assert.equal(values.has('kdg-capture-auth'),false);controller.dispose();
 }else{
  await auth.verifyOtp({email:'facilitator@example.invalid',token:'123456',type:'email'});broken=failure;
  await assert.rejects(failure==='getItem'?auth.getSession():auth.signOut({scope:'local'}),{message:'auth_storage_unavailable'});
 }
 broken=null;await assert.rejects(auth.getSession(),{message:'auth_storage_unavailable'});auth.stopAutoRefresh();
});
