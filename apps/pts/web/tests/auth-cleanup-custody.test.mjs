import test from 'node:test';
import assert from 'node:assert/strict';
import {registerHooks} from 'node:module';

// Actual auth.ts recovery helper, with only the provider client/config replaced.
globalThis.location={origin:'https://pts.fixture.test',hash:''};
// Physical SDK storage is a negative observation; mocked provider claims remain
// the only positive identity evidence in this focused owner test.
globalThis.localStorage={getItem:()=>null};
let claims;
globalThis.ptsCleanupAuth={getClaims:token=>claims(token)};
registerHooks({
 resolve(specifier,context,next){
  if(specifier==='@supabase/supabase-js')return {url:'data:text/javascript,export function createClient(url,key,options){globalThis.ptsCleanupOptions=options;return {auth:globalThis.ptsCleanupAuth}}',shortCircuit:true};
  if(specifier==='./sessionRevocation'&&context.parentURL?.endsWith('/src/auth.ts'))return {url:new URL('../src/sessionRevocation.ts',import.meta.url).href,shortCircuit:true};
  return next(specifier,context);
 },
 load(url,context,next){
  const loaded=next(url,context);
  if(url.endsWith('/src/auth.ts'))return {...loaded,source:'import.meta.env={};\n'+loaded.source};
  return loaded;
 },
});
const {retainCurrentCleanup,revokeLocalSession,observeAuthChange,verifiedSessionIdentity}=await import('../src/auth.ts');
const original={id:'account',sessionId:'session',token:'original',refreshToken:'original-refresh'};
const older={id:'account',token:'older',refreshToken:'older-refresh'};
const newer={id:'account',token:'newer',refreshToken:'newer-refresh'};
const evidence={data:{claims:{sub:'account',session_id:'session'}},error:null};
const deferred=()=>{let resolve;const promise=new Promise(done=>{resolve=done;});return {promise,resolve};};

test('delayed verified claims cannot downgrade newer same-session cleanup rotation',async()=>{
 const delayed=deferred();claims=token=>token==='older'?delayed.promise:Promise.resolve(evidence);
 let current=older,saved;const retain=async(_,refreshed)=>{saved=refreshed;};
 const old=retainCurrentCleanup(older,original,retain,()=>current===older).catch(error=>error);
 current=newer;await retainCurrentCleanup(newer,original,retain,()=>current===newer);
 delayed.resolve(evidence);await old;
 assert(saved.refreshToken===newer.refreshToken,'older claims response downgraded verified refresh custody');
});

test('logout or account-switch supersession prevents late auth recovery writes',async()=>{
 const delayed=deferred();claims=()=>delayed.promise;let active=true,writes=0;
 const old=retainCurrentCleanup(older,original,async()=>{writes++;},()=>active).catch(error=>error);
 active=false;delayed.resolve(evidence);await old;
 assert.equal(writes,0,'superseded auth observation wrote cleanup custody');
});

test('current verified same-session rotation is retained; foreign session is refused',async()=>{
 let writes=0;claims=async()=>evidence;
 await retainCurrentCleanup(newer,original,async(_,refreshed)=>{writes++;assert(refreshed.refreshToken===newer.refreshToken);},()=>true);
 claims=async()=>({data:{claims:{sub:'account',session_id:'foreign'}},error:null});
 await assert.rejects(()=>retainCurrentCleanup(newer,original,async()=>{writes++;},()=>true));
 assert.equal(writes,1);
});

test('current verified original SDK pair avoids explicit stale refresh after implicit rotation',async()=>{
 const revoked=[];let explicitRefresh=0,retained;
 globalThis.ptsCleanupAuth.getSession=async()=>({data:{session:{user:{id:'account'},access_token:'sdk-fresh',refresh_token:'sdk-latest-refresh'}},error:null});
 globalThis.ptsCleanupAuth.onAuthStateChange=()=>({data:{subscription:{unsubscribe(){}}}});
 globalThis.ptsCleanupAuth.admin={signOut:async token=>{revoked.push(token);return {error:token==='sdk-fresh'?null:{status:403}};}};
 // The installed SDK first refreshes its stored session in _useSession and then
 // attempts the explicit old credential. Native7 observed the resulting400.
 globalThis.ptsCleanupAuth.refreshSession=async()=>{explicitRefresh++;return {data:{session:null},error:{status:400,code:'refresh_token_already_used'}};};
 claims=async()=>evidence;
 await revokeLocalSession(original,async(_,fresh)=>{retained=fresh;});
 assert.deepEqual(revoked,['sdk-fresh']);assert.equal(explicitRefresh,0);
 assert(retained.refreshToken==='sdk-latest-refresh','current verified SDK rotation was not retained before revoke');
});

test('different current session in the same account cannot replace original cleanup authority',async()=>{
 const revoked=[];let retained;
 globalThis.ptsCleanupAuth.getSession=async()=>({data:{session:{user:{id:'account'},access_token:'foreign-current',refresh_token:'foreign-refresh'}},error:null});
 globalThis.ptsCleanupAuth.onAuthStateChange=()=>({data:{subscription:{unsubscribe(){}}}});
 globalThis.ptsCleanupAuth.admin={signOut:async token=>{revoked.push(token);return {error:token==='original-renewed'?null:{status:403}};}};
 globalThis.ptsCleanupAuth.refreshSession=async({refresh_token})=>{assert.equal(refresh_token,original.refreshToken);return {data:{session:{user:{id:'account'},access_token:'original-renewed',refresh_token:'original-latest-refresh'}},error:null};};
 claims=async token=>({data:{claims:{sub:'account',session_id:token==='foreign-current'?'foreign':'session'}},error:null});
 await revokeLocalSession(original,async(_,fresh)=>{retained=fresh;});
 assert(!revoked.includes('foreign-current'),'different session was revoked');
 assert.equal(retained.token,'original-renewed');
});

test('new SDK observation during current-pair verification prevents stale recovery adoption',async()=>{
 const delayed=deferred(),started=deferred();let writes=0;const revoked=[];
 globalThis.ptsCleanupAuth.getSession=async()=>({data:{session:{user:{id:'account'},access_token:'sdk-fresh',refresh_token:'sdk-latest-refresh'}},error:null});
 globalThis.ptsCleanupAuth.onAuthStateChange=()=>assert.fail('recovery must observe the existing app subscription without another SDK session load');
 globalThis.ptsCleanupAuth.admin={signOut:async token=>{revoked.push(token);return {error:{status:403}};}};
 globalThis.ptsCleanupAuth.refreshSession=async()=>({data:{session:null},error:{status:400}});
 claims=()=>{started.resolve();return delayed.promise;};
 const result=revokeLocalSession(original,async()=>{writes++;}).catch(error=>error);
 const readiness=await Promise.race([started.promise.then(()=>true),result.then(()=>false)]);
 assert(readiness,'recovery started another subscription instead of verifying the existing current pair');
 observeAuthChange('TOKEN_REFRESHED');delayed.resolve(evidence);await result;
 assert.equal(writes,0);assert.deepEqual(revoked,[original.token]);
});

test('session comparison uses owner-verified session evidence and rejects superseded observations',async()=>{
 const session={user:{id:'account'},access_token:'replacement',refresh_token:'replacement-refresh'};
 claims=async()=>({data:{claims:{sub:'account',session_id:'replacement-session'}},error:null});
 const identity=await verifiedSessionIdentity(session,()=>true);
 assert.equal(identity.sessionId,'replacement-session');
 const delayed=deferred();claims=()=>delayed.promise;let current=true;
 const result=verifiedSessionIdentity(session,()=>current);
 current=false;delayed.resolve(evidence);
 await assert.rejects(()=>result,/superseded/);
 claims=async()=>({data:{claims:{sub:'foreign',session_id:'forged'}},error:null});
 await assert.rejects(()=>verifiedSessionIdentity(session,()=>true),/mismatch/);
});

test('failed replacement observation still attempts exact original and remains rejected before restoration',async()=>{
 let revoked=0;
 globalThis.ptsCleanupAuth.getSession=async()=>{throw Object.assign(new Error('file_cleanup_replacement_unavailable'),{code:'file_cleanup_replacement_unavailable'});};
 globalThis.ptsCleanupAuth.admin={signOut:async()=>{revoked++;return {error:null};}};
 await assert.rejects(()=>revokeLocalSession(original),error=>error.code==='file_cleanup_replacement_unavailable');
 assert.equal(revoked,1);
});

test('unavailable private custody still attempts only the retained original without session loads or refresh',async()=>{
 const revoked=[];let loads=0,refreshes=0,retentions=0;
 globalThis.ptsCleanupAuth.getSession=async()=>{loads++;return {data:{session:null},error:null};};
 globalThis.ptsCleanupAuth.refreshSession=async()=>{refreshes++;return {data:{session:null},error:{status:400}};};
 globalThis.ptsCleanupAuth.admin={signOut:async token=>{revoked.push(token);return {error:null};}};
 await revokeLocalSession(original,async()=>{retentions++;},false);
 assert.deepEqual(revoked,[original.token]);assert.equal(loads,0);assert.equal(refreshes,0);assert.equal(retentions,0);
});

test('failed current-original persistence attempts verified current token without unsafe refresh',async()=>{
 const revoked=[];
 globalThis.ptsCleanupAuth.getSession=async()=>({data:{session:{user:{id:'account'},access_token:'sdk-current',refresh_token:'sdk-current-refresh'}},error:null});
 claims=async()=>evidence;
 globalThis.ptsCleanupAuth.refreshSession=async()=>assert.fail('failed persistence must not refresh');
 globalThis.ptsCleanupAuth.admin={signOut:async token=>{revoked.push(token);return {error:null};}};
 await assert.rejects(()=>revokeLocalSession(original,async()=>{throw new Error('fixture_storage_failed');}),/fixture_storage_failed/);
 assert.deepEqual(revoked,['sdk-current']);
});

test('file preparation freshness reads physical SDK storage without relying on delivered auth notifications',async()=>{
 const {filePreparationIsCurrent}=await import('../src/auth.ts');let session={user:{id:original.id},access_token:original.token,refresh_token:original.refreshToken};
 globalThis.localStorage={getItem:()=>JSON.stringify(session)};
 assert.equal(filePreparationIsCurrent(original),true);
 session=null;assert.equal(filePreparationIsCurrent(original),false,'physically cleared SDK storage accepted delayed preparation');
 session={user:{id:original.id},access_token:newer.token};
 assert.equal(filePreparationIsCurrent(original),false,'older token superseded newer same-session observation');
});

test('each synchronous freshness call rechecks physical SDK state instead of retaining an earlier positive observation',async()=>{
 const {filePreparationIsCurrent}=await import('../src/auth.ts');let raw=JSON.stringify({user:{id:original.id},access_token:original.token,refresh_token:original.refreshToken});
 globalThis.localStorage={getItem:()=>raw};assert.equal(filePreparationIsCurrent(original),true);
 raw=null;observeAuthChange('SIGNED_OUT');assert.equal(filePreparationIsCurrent(original),false);
 raw='invalid';assert.equal(filePreparationIsCurrent(original),false);
});

test('preparation freshness is synchronous and never loads or refreshes the existing SDK session',async()=>{
 const {filePreparationIsCurrent}=await import('../src/auth.ts');let loads=0,refreshes=0;
 globalThis.localStorage={getItem:()=>JSON.stringify({user:{id:original.id},access_token:original.token,refresh_token:original.refreshToken})};
 globalThis.ptsCleanupAuth.getSession=async()=>{loads++;return {data:{session:{user:{id:original.id},access_token:original.token,refresh_token:original.refreshToken}},error:null};};
 globalThis.ptsCleanupAuth.refreshSession=async()=>{refreshes++;return {data:{session:null},error:{status:400}};};
 const current=filePreparationIsCurrent(original);
 assert.equal(typeof current,'boolean','freshness started an asynchronous SDK session load');
 assert.equal(current,true);assert.equal(loads,0);assert.equal(refreshes,0);
});

test('same access token with a newer SDK refresh pair supersedes delayed preparation recovery',async()=>{
 const {filePreparationIsCurrent}=await import('../src/auth.ts');let refresh=original.refreshToken;
 globalThis.localStorage={getItem:()=>JSON.stringify({user:{id:original.id},access_token:original.token,refresh_token:refresh})};
 assert.equal(filePreparationIsCurrent(original),true);
 refresh='newer-same-access-refresh';
 assert.equal(filePreparationIsCurrent(original),false,'same-access JWT observation downgraded rotated refresh custody');
 assert.equal(filePreparationIsCurrent({id:original.id,token:original.token}),true,'token-only compatible callers must remain a negative freshness check');
});


test('profile error parsing cannot remove a newer SDK pair while current claims overlap',async()=>{
 // Simulate the SDK's documented storage boundary after its profile response
 // has been parsed. This also exercises the window after fetch has returned.
 const adapter=globalThis.ptsCleanupOptions.auth.storage;
 let raw=JSON.stringify({access_token:'old-profile',refresh_token:'old-refresh'});
 globalThis.localStorage={getItem:()=>raw,setItem:(_,value)=>{raw=value;},removeItem:()=>{raw=null;}};
 const old=deferred(),next=deferred(),oldStarted=deferred(),nextStarted=deferred();
 claims=async token=>{
  if(token==='old-profile'){oldStarted.resolve();await old.promise;adapter.removeItem('pts-auth');return {data:null,error:{code:'session_not_found'}};}
  nextStarted.resolve();await next.promise;return {data:{claims:{sub:'account',session_id:'new-session'}},error:null};
 };
 const obsolete=verifiedSessionIdentity({user:{id:'account'},access_token:'old-profile',refresh_token:'old-refresh'},()=>true).catch(error=>error);
 await oldStarted.promise;
 const pair=JSON.stringify({access_token:'new-profile',refresh_token:'new-refresh'});raw=pair;
 const current=verifiedSessionIdentity({user:{id:'account'},access_token:'new-profile',refresh_token:'new-refresh'},()=>true);
 await nextStarted.promise;old.resolve();
 assert.equal((await obsolete).code,'file_cleanup_superseded');assert.equal(raw,pair,'obsolete parsed profile error removed the current SDK pair');
 next.resolve();assert.equal((await current).sessionId,'new-session');assert.equal(raw,pair);
});

test('empty-original SDK logout cannot send a later selected token to the provider',async()=>{
 const {finishOriginalAuthLogout}=await import('../src/auth.ts');let raw=null,requests=0;
 globalThis.localStorage={getItem:()=>raw,setItem:(_,value)=>{raw=value;},removeItem:()=>{raw=null;}};
 globalThis.ptsCleanupAuth.getSession=async()=>({data:{session:null},error:null});
 const replacement=JSON.stringify({access_token:'later-selected',refresh_token:'later-refresh'}),originalFetch=globalThis.fetch;
 globalThis.fetch=async()=>{requests++;return new Response(null,{status:204});};
 globalThis.ptsCleanupAuth.signOut=async()=>{
  // The public SDK can select storage after an internal await. Simulate another
  // tab's physical write at that boundary, then use its configured real fetch.
  raw=replacement;
  await globalThis.ptsCleanupOptions.global.fetch('https://auth.fixture.test/auth/v1/logout',{method:'POST',headers:{Authorization:'Bearer later-selected'}});
  return {error:null};
 };
 try{await assert.rejects(()=>finishOriginalAuthLogout(null,()=>true),error=>error.code==='file_cleanup_superseded');assert.equal(requests,0);assert.equal(raw,replacement);}
 finally{globalThis.fetch=originalFetch;}
});
