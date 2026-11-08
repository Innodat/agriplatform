// UI/control-flow doubles; genuine provider/image proof remains in the native fixture.
const {test,expect}=require('@playwright/test');
const {origin,sessionFor,installAuthNotificationHold}=require('./file-fixture.cjs');
const account='33333333-3333-4333-8333-333333333333';
const original=sessionFor(account,'original@example.invalid','original');
const renewed=sessionFor(account,'original@example.invalid','renewed');
const replacement=sessionFor('44444444-4444-4444-8444-444444444444','replacement@example.invalid');
const sessionId='55555555-5555-4555-8555-555555555555';
const switchingFailure='We could not finish switching accounts. Please retry Sign out.';
const signingOutFailure='We could not finish signing you out. Please retry Sign out.';

test('completed logout in another app tab supersedes held preparation and later login needs no old cleanup',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 let held,release,unavailable=false,clearAfterLogin=0;
 const waiting=new Promise(resolve=>release=resolve);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+replacement.access_token?replacement.user:original.user}));
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:replacement}));
 await context.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await context.route(origin+'/**',async r=>{
  if(!unavailable)return r.fallback();
  if(new URL(r.request().url()).pathname.endsWith('/clear'))clearAfterLogin++;
  return r.fulfill({status:503,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'current_session_unavailable'}}});
 });
 await page.route(origin+'/api/file-session/prepare',async r=>{
  if(r.request().method()==='OPTIONS')return r.fallback();
  held=true;await waiting;
  await r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'prepared',account_id:account,session_id:sessionId}});
 });
 await page.addInitScript(original=>{if(!sessionStorage.getItem('cross-tab-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('cross-tab-seeded','true');}},original);
 await page.goto('/');await expect.poll(()=>Boolean(held)).toBe(true);
 const other=await context.newPage();await other.goto('/');
 await other.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await other.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 release();await page.waitForLoadState('networkidle');
 expect(await page.evaluate(()=>{const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return !value||(!value.token&&!value.refreshToken&&!value.revocationToken&&!value.replacement);})).toBe(true);
 unavailable=true;
 await page.getByLabel('Email',{exact:true}).fill(replacement.user.email);await page.getByLabel('Password',{exact:true}).fill('fixture-password');await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);expect(clearAfterLogin).toBe(0);
 await other.close();
});

for(const failure of ['lock','storage'])test('unavailable private custody '+failure+' does not gate ordinary authorized reading',async({page})=>{
 const {files}=require('./file-fixture.cjs');await files(page);
 await page.addInitScript(({original,failure})=>{
  localStorage.setItem('pts-auth',JSON.stringify(original));
  if(failure==='lock'){
   const request=navigator.locks.request.bind(navigator.locks);
   navigator.locks.request=(name,...args)=>name==='pts-file-cleanup-v1'?Promise.reject(new Error('fixture_lock_unavailable')):request(name,...args);
  }else{
   const setItem=Storage.prototype.setItem;
   Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1')throw new Error('fixture_storage_unavailable');return setItem.call(this,key,value);};
  }
 },{original,failure});
 await page.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
 expect(await page.evaluate(()=>{const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return !value?.token&&!value?.refreshToken&&!value?.revocationToken&&!value?.replacement;})).toBe(true);
});

// Private browser faults affect only the private storage key and its Web Lock.
// The existing SDK storage and auth owner remain real application code.
async function privateFault(page,failure,enabled=true){
 await page.evaluate(({failure,enabled})=>{
  window.cleanupFault=enabled?failure:null;
  if(window.cleanupFaultInstalled)return;
  window.cleanupFaultInstalled=true;
  const locks=navigator.locks,request=locks?.request.bind(locks);
  Object.defineProperty(navigator,'locks',{configurable:true,get(){
   if(window.cleanupFault==='absent')return undefined;
   return {...locks,request(name,options,operation){
    if(name!=='pts-file-cleanup-v1'||!window.cleanupFault)return request(name,options,operation);
    if(window.cleanupFault==='timeout')return new Promise((_,reject)=>options.signal.addEventListener('abort',()=>reject(options.signal.reason),{once:true}));
    if(window.cleanupFault==='lock')return Promise.reject(new Error('fixture_lock_failed'));
    return request(name,options,operation);
   }};
  }});
  const setItem=Storage.prototype.setItem;
  Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1'&&window.cleanupFault==='storage')throw new Error('fixture_storage_failed');return setItem.call(this,key,value);};
 },{failure,enabled});
}
async function ordinaryFixture(page){
 const {files}=require('./file-fixture.cjs');await files(page);
 await page.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
}
test('Sign out auth-storage initialization failure stays incomplete and first Retry completes',async({page})=>{
 await ordinaryFixture(page);let revoked=false,revokes=0;
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization).toBe('Bearer '+original.access_token);revokes++;revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}}));
 await page.addInitScript(original=>{localStorage.setItem('pts-auth',JSON.stringify(original));},original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 await page.waitForLoadState('networkidle');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 const before=await page.evaluate(()=>({auth:localStorage.getItem('pts-auth'),custody:localStorage.getItem('pts-file-cleanup-v1')}));
 await page.evaluate(()=>{
  window.logoutAuthReadFault=true;window.logoutAuthReadFailures=0;
  const get=Storage.prototype.getItem;
  Storage.prototype.getItem=function(key){if(key==='pts-auth'&&window.logoutAuthReadFault){window.logoutAuthReadFailures++;throw new Error('fixture_auth_storage_unreadable');}return get.call(this,key);};
 });
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>window.logoutAuthReadFailures)).toBeGreaterThan(0);
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 await expect(page.getByText('0 poems and excerpts shown')).toHaveCount(0);expect(revokes).toBe(0);
 await page.evaluate(()=>{window.logoutAuthReadFault=false;});
 expect(await page.evaluate(()=>({auth:localStorage.getItem('pts-auth'),custody:localStorage.getItem('pts-file-cleanup-v1')}))).toEqual(before);
 await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
 expect(revokes).toBeGreaterThan(0);
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return localStorage.getItem('pts-auth')===null&&!saved?.token&&!saved?.refreshToken&&!saved?.revocationToken&&!saved?.replacement;})).toBe(true);
});
for(const fault of ['absent','lock','timeout','storage'])test('ordinary no-custody Sign out survives private '+fault+' failure',async({page})=>{
 await ordinaryFixture(page);
 let revokes=0,prepares=0;
 await page.route(origin+'/api/file-session/prepare',r=>{prepares++;return r.fulfill({status:403,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'file_cleanup_unavailable'}}});});
 await page.route('**/auth/v1/logout*',r=>{revokes++;return r.fulfill({status:204});});
 await page.addInitScript(original=>{localStorage.setItem('pts-auth',JSON.stringify(original));},original);
 await page.goto('/');await page.waitForLoadState('networkidle');
 await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();expect(prepares).toBeGreaterThan(0);
 await privateFault(page,fault);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);expect(revokes).toBe(1);
 expect(await page.evaluate(()=>localStorage.getItem('pts-auth')===null)).toBe(true);
});
for(const fault of ['absent','timeout','storage'])test('receipted Sign out attempts original provider under private '+fault+' failure and recovers honestly',async({page})=>{
 await ordinaryFixture(page);let revokes=0,revoked=false;
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revokes++;revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}}));
 await page.addInitScript(original=>{localStorage.setItem('pts-auth',JSON.stringify(original));},original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await privateFault(page,fault);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect.poll(()=>revokes).toBeGreaterThan(0);
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await page.evaluate(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token))).toBe(true);
 await privateFault(page,fault,false);
 await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});
for(const fault of ['absent','storage'])test('pending replacement cleanup revokes only original under private '+fault+' failure',async({page})=>{
 await ordinaryFixture(page);let revokes=0,revoked=false;
 await page.addInitScript(({original,replacement,sessionId})=>{
  localStorage.setItem('pts-auth',JSON.stringify(replacement));
  localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token,pending:true,replacement:{id:replacement.user.id,sessionId:'66666666-6666-4666-8666-666666666666',token:replacement.access_token,refreshToken:replacement.refresh_token}}));
 },{original,replacement:sessionFor(replacement.user.id,'replacement@example.invalid','replacement','66666666-6666-4666-8666-666666666666'),sessionId});
 await page.route('**/auth/v1/user',r=>r.fulfill({json:replacement.user}));
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revokes++;revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}}));
 await page.goto('/');await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();await page.waitForLoadState('networkidle');
 await privateFault(page,fault);await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect.poll(()=>revokes).toBeGreaterThan(0);await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')),sdk=JSON.parse(localStorage.getItem('pts-auth'));return saved.pending&&saved.replacement.token===sdk.access_token;})).toBe(true);
 await privateFault(page,fault,false);await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});

test('confirmed original cleanup keeps an SDK refresh failure visible and repeated Sign out recovers',async({page})=>{
 const {files}=require('./file-fixture.cjs');await files(page);
 await page.clock.install({time:new Date(Date.now())});
 let revoked=false,clearCalls=0,refreshFailures=0,clockPastCredentialExpiry=false;
 await page.addInitScript(original=>{localStorage.setItem('pts-auth',JSON.stringify(original));},original);
 await page.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await page.route('**/auth/v1/logout*',r=>{revoked=true;return r.fulfill({status:204});});
 await page.route('**/auth/v1/token*',r=>{refreshFailures++;return r.fulfill({status:400,json:{error_code:'refresh_token_not_found',msg:'fixture original already revoked'}});});
 await page.route(origin+'/api/file-session/clear',async r=>{
  const headers={'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'};
  if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers});
  clearCalls++;
  // Advance the fixture clock into the actual JWT/session expiry margin without
  // editing SDK storage or firing refresh timers; the existing SDK owns refresh.
  if(revoked&&clearCalls>=2){await page.clock.setSystemTime((original.expires_at+1)*1000);clockPastCredentialExpiry=await page.evaluate(expiry=>Date.now()>expiry*1000,original.expires_at);}
  return r.fulfill({headers,json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});
 });
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect.poll(()=>refreshFailures).toBeGreaterThan(0);expect(clockPastCredentialExpiry).toBe(true);
 await expect(page.getByRole('alert').filter({hasText:'We could not sign you out. Please try again.'})).toBeVisible();
 expect(revoked).toBe(true);expect(clearCalls).toBeGreaterThanOrEqual(2);expect(refreshFailures).toBeGreaterThan(0);
 expect(await page.evaluate(()=>{
  const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');
  return localStorage.getItem('pts-auth')===null&&value?.cleared===true&&!value.token&&!value.refreshToken&&!value.revocationToken&&!value.replacement;
 })).toBe(true);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
});

async function setup(page,pending=false){
 let reads=0,postRefreshFailures=0;
 await page.addInitScript(({original,current,pending,sessionId})=>{
  if(!localStorage.getItem('pts-file-cleanup-v1'))localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token,pending}));
  if(!localStorage.getItem('pts-auth'))localStorage.setItem('pts-auth',JSON.stringify(current));
 },{original,current:pending?renewed:replacement,pending,sessionId});
 await page.route(origin+'/**',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:'present'}}));
 await page.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+replacement.access_token?replacement.user:renewed.user}));
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:renewed}));
 await page.route('**/auth/v1/logout*',r=>{
  if(r.request().headers().authorization==='Bearer '+original.access_token)return r.fulfill({status:403,json:{code:'bad_jwt',msg:'fixture expired original'}});
  postRefreshFailures++;return r.fulfill({status:503,json:{code:'fixture_provider_unavailable'}});
 });
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>{
  reads++;return r.fulfill({status:401,json:{detail:{code:'authentication_required'}}});
 });
 return {reads:()=>reads,failures:()=>postRefreshFailures};
}

test('failed account cleanup remains visible without resuming expired collection requests',async({page})=>{
 const observed=await setup(page);await page.goto('/?poem=OLD');
 await expect.poll(observed.failures).toBeGreaterThan(0);
 await expect(page.getByRole('alert').filter({hasText:switchingFailure})).toBeVisible();
 await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await page.waitForTimeout(150);expect(observed.reads()).toBe(0);
 expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).pending)).toBe(true);
});

test('pending cleanup remains visible after reload and retains the existing Sign out recovery',async({page})=>{
 const observed=await setup(page,true);await page.goto('/');
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 await page.reload();await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 expect(observed.reads()).toBe(0);
});

for(const outage of [false,true])test('verified same-account replacement '+(outage?'retains recovery across failure/reload/retry':'cleans original before repeated Open'),async({page})=>{
 const {files}=require('./file-fixture.cjs');await files(page);
 const next=sessionFor(account,'original@example.invalid','independent','66666666-6666-4666-8666-666666666666');
 let revoked=false,unavailable=outage,contexts=0;
 await page.addInitScript(({original,next,sessionId})=>{
  if(!localStorage.getItem('pts-file-cleanup-v1'))localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token}));
  if(!localStorage.getItem('pts-auth'))localStorage.setItem('pts-auth',JSON.stringify(next));
  window.open=()=>{window.openCount=(window.openCount||0)+1;return null;};
 },{original,next,sessionId});
 await page.route('**/auth/v1/user',r=>r.fulfill({json:next.user}));
 await page.route('**/auth/v1/logout*',r=>{
  expect(r.request().headers().authorization).toBe('Bearer '+original.access_token);
  revoked=true;return r.fulfill({status:204});
 });
 await page.route(origin+'/api/file-session/clear',r=>{
  const headers={'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'};
  if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers});
  return unavailable?r.fulfill({status:503,headers,json:{detail:{code:'current_session_unavailable'}}}):r.fulfill({headers,json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});
 });
 await page.route(origin+'/api/file-contexts/**',async r=>{
  if(r.request().method()==='POST'){expect(revoked).toBe(true);contexts++;}
  await r.fallback();
 });
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:new URL(r.request().url()).pathname.startsWith('/api/documents/')?{status:'stored',document:{}}:{sources:[{id:'S1',title:'Replacement source',document_id:'D1'}],rights:[],source_documents:[{id:'D1',source_id:'S1',title:'Replacement PDF',local_path:'sources/replacement.pdf'}]}}));
 await page.goto('/?view=sources');
 if(outage){
  await expect(page.getByRole('alert').filter({hasText:switchingFailure})).toBeVisible();
  expect(contexts).toBe(0);
  expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).replacement.sessionId)).toBe('66666666-6666-4666-8666-666666666666');
  await page.reload();await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
  unavailable=false;await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 }
 const open=page.getByRole('button',{name:'Open document',exact:true});await expect(open).toBeVisible();
 await open.click();await expect.poll(()=>contexts).toBe(1);await expect.poll(()=>page.evaluate(()=>window.openCount)).toBe(1);
 await open.click();await expect.poll(()=>contexts).toBe(2);await expect.poll(()=>page.evaluate(()=>window.openCount)).toBe(2);
 expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).sessionId)).toBe('66666666-6666-4666-8666-666666666666');
 await expect(page.getByRole('alert')).toHaveCount(0);
});

test('pending replacement retains owner-verified same-session rotation on reload',async({page})=>{
 const previous=sessionFor(account,'original@example.invalid','replacement-before-refresh','66666666-6666-4666-8666-666666666666');
 const current=sessionFor(account,'original@example.invalid','replacement-after-refresh','66666666-6666-4666-8666-666666666666');
 await page.addInitScript(({original,previous,current,sessionId})=>{
  localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token,pending:true,
   replacement:{id:previous.user.id,sessionId:'66666666-6666-4666-8666-666666666666',token:previous.access_token,refreshToken:previous.refresh_token}}));
  localStorage.setItem('pts-auth',JSON.stringify(current));
 },{original,previous,current,sessionId});
 await page.route('**/auth/v1/user',r=>r.fulfill({json:current.user}));
 await page.goto('/');await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 await expect.poll(()=>page.evaluate(()=>{
  const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')),session=JSON.parse(localStorage.getItem('pts-auth'));
  return saved.pending===true&&saved.token!==session.access_token&&saved.replacement.token===session.access_token&&saved.replacement.refreshToken===session.refresh_token;
 })).toBe(true);
});

for(const {sameAccount,verificationUnavailable=false,automatic=false} of [{sameAccount:false},{sameAccount:true},{sameAccount:false,verificationUnavailable:true},{sameAccount:false,verificationUnavailable:true,automatic:true}])test('cleanup retains '+(sameAccount?'same-account':'different-account')+' replacement rotated by existing SDK session loads'+(verificationUnavailable?' when verification fails after original absence':'')+(automatic?' during automatic switching':''),async({page})=>{
 const next=sessionFor(sameAccount?account:replacement.user.id,'replacement@example.invalid','before-cleanup','66666666-6666-4666-8666-666666666666');
 const first=sessionFor(next.user.id,'replacement@example.invalid','implicit-first','66666666-6666-4666-8666-666666666666');
 const latest=sessionFor(next.user.id,'replacement@example.invalid','implicit-latest','66666666-6666-4666-8666-666666666666');
 if(automatic)await page.clock.install({time:new Date(Date.now())});
 let revoked=verificationUnavailable,replacementRefreshes=0,expiredForAutomatic=false;
 await page.addInitScript(({original,next,sessionId,automatic})=>{
  localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token,pending:!automatic,replacement:{id:next.user.id,sessionId:'66666666-6666-4666-8666-666666666666',token:next.access_token,refreshToken:next.refresh_token}}));
  localStorage.setItem('pts-auth',JSON.stringify(next));
 },{original,next,sessionId,automatic});
 await page.route('**/auth/v1/user',async r=>{
  const token=r.request().headers().authorization?.slice(7);
  if(verificationUnavailable&&[first,latest].some(value=>value.access_token===token))return r.fulfill({status:503,json:{code:'fixture_provider_unavailable'}});
  if(automatic&&!expiredForAutomatic&&token===next.access_token){
   expiredForAutomatic=true;
   // Keep JWT/session metadata coherent and let the SDK own refresh. Advance
   // into its 90s margin without editing persisted SDK state or firing timers.
   await page.clock.setSystemTime((next.expires_at-60)*1000);
  }
  return r.fulfill({json:[next,first,latest].some(value=>value.access_token===token)?next.user:renewed.user});
 });
 await page.route('**/auth/v1/token*',r=>{
  const refresh=r.request().postDataJSON().refresh_token;
  if(refresh===original.refresh_token)return r.fulfill({json:renewed});
  replacementRefreshes++;
  // The SDK loads the current foreign session both before explicit original
  // recovery and within refreshSession(original). Both rotations are genuine
  // SDK notifications; the short lifetime exercises its existing expiry margin.
  return r.fulfill({json:{...(refresh===next.refresh_token?first:latest),expires_in:60,expires_at:Math.floor(Date.now()/1000)+60}});
 });
 await page.route('**/auth/v1/logout*',r=>{
  if(r.request().headers().authorization==='Bearer '+original.access_token)return r.fulfill({status:403,json:{code:'bad_jwt',msg:'fixture expired original'}});
  revoked=true;return r.fulfill({status:204});
 });
 await page.route(origin+'/**',r=>{
  const headers={'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'};
  if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers});
  const path=new URL(r.request().url()).pathname;
  return r.fulfill({headers,json:path.endsWith('/clear')?{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}:{status:'prepared',account_id:next.user.id,session_id:'66666666-6666-4666-8666-666666666666'}});
 });
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 const failedVerification=verificationUnavailable?page.waitForResponse(response=>new URL(response.url()).pathname.endsWith('/auth/v1/user')&&response.status()===503):null;
 await page.goto('/');
 if(!automatic){
  await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
  await page.evaluate(()=>{const session=JSON.parse(localStorage.getItem('pts-auth'));session.expires_at=Math.floor(Date.now()/1000);localStorage.setItem('pts-auth',JSON.stringify(session));});
  await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 }
 if(verificationUnavailable){
  await failedVerification;await page.waitForLoadState('networkidle');
  await expect(page.getByRole('alert').filter({hasText:automatic?switchingFailure:signingOutFailure})).toBeVisible();
  expect(replacementRefreshes).toBeGreaterThan(0);
  expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).pending===true)).toBe(true);
  if(automatic){
   expect(await page.evaluate(expiry=>Date.now()>=expiry*1000-90000&&Date.now()<expiry*1000,next.expires_at),'clock must keep actual JWT valid within SDK refresh margin').toBe(true);
   expect(await page.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')).refresh_token===expected,first.refresh_token)).toBe(true);
  }
  return;
 }
 await expect(page.getByRole('alert')).toHaveCount(0);
 expect(replacementRefreshes).toBeGreaterThanOrEqual(2);
 expect(await page.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')).refresh_token===expected,latest.refresh_token)).toBe(true);
 await expect.poll(()=>page.evaluate(expected=>{
  const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');
  return saved?.pending===false&&saved.sessionId==='66666666-6666-4666-8666-666666666666'&&saved.refreshToken===expected;
 },latest.refresh_token)).toBe(true);
});

// A first failed automatic replacement write must be recovered before SDK loads
// can rotate that replacement during a later original-session cleanup.
test('first replacement write failure preserves sole-SDK rotation on retry',async({page})=>{
 await ordinaryFixture(page);
 const next=sessionFor(replacement.user.id,'replacement@example.invalid','first-write','66666666-6666-4666-8666-666666666666');
 const latest=sessionFor(next.user.id,next.user.email,'first-write-rotated','66666666-6666-4666-8666-666666666666');
 let failedFirst=false,revoked=false,refreshes=0;
 await page.addInitScript(({original,next,sessionId})=>{
  localStorage.setItem('pts-auth',JSON.stringify(next));
  localStorage.setItem('pts-file-cleanup-v1',JSON.stringify({version:1,id:original.user.id,sessionId,token:original.access_token,refreshToken:original.refresh_token}));
 },{original,next,sessionId});
 await page.route('**/auth/v1/user',async r=>{
  const isReplacement=r.request().headers().authorization==='Bearer '+next.access_token;
  if(isReplacement&&!failedFirst){failedFirst=true;await privateFault(page,'storage');}
  return r.fulfill({json:r.request().headers().authorization==='Bearer '+original.access_token?original.user:next.user});
 });
 await page.route('**/auth/v1/token*',r=>{refreshes++;return r.fulfill({json:latest});});
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}}));
 await page.goto('/');await expect(page.getByRole('alert').filter({hasText:switchingFailure})).toBeVisible();
 await privateFault(page,'storage',false);
 await page.evaluate(()=>{const sdk=JSON.parse(localStorage.getItem('pts-auth'));sdk.expires_at=Math.floor(Date.now()/1000);localStorage.setItem('pts-auth',JSON.stringify(sdk));});
 await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 expect(refreshes).toBeGreaterThan(0);
 expect(await page.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')).refresh_token===expected,latest.refresh_token)).toBe(true);
 await expect.poll(()=>page.evaluate(expected=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.refreshToken===expected,latest.refresh_token)).toBe(true);
});

for(const receipted of [false,true])test('unreadable private custody still attempts known '+(receipted?'original':'ordinary current')+' provider and remains incomplete',async({page})=>{
 await ordinaryFixture(page);let revokes=0,revoked=false;
 if(!receipted)await page.route(origin+'/api/file-session/prepare',r=>r.fulfill({status:403,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'file_cleanup_unavailable'}}}));
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revokes++;revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}}));
 await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForLoadState('networkidle');
 if(receipted)await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.evaluate(()=>{
  window.privateReadFailure=true;const read=Storage.prototype.getItem;
  Storage.prototype.getItem=function(key){if(key==='pts-file-cleanup-v1'&&window.privateReadFailure)throw new Error('fixture_read_failed');return read.call(this,key);};
 });
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect.poll(()=>revokes).toBeGreaterThan(0);
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await page.evaluate(()=>Boolean(localStorage.getItem('pts-auth')))).toBe(true);
 await page.evaluate(()=>{window.privateReadFailure=false;});
 await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});

for(const fault of ['absent','storage'])test('held other-tab preparation cannot regain custody after ordinary logout with private '+fault+' failure',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 let held=false,release;const waiting=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await context.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(installAuthNotificationHold,true);
 await page.addInitScript(original=>{
  if(!sessionStorage.getItem('combined-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('combined-seeded','true');}
  // Delay cross-tab notifications so freshness must inspect actual shared auth
  // storage, independently of eventual subscription/event delivery.
 },original);
 await page.route(origin+'/api/file-session/prepare',async r=>{
  if(r.request().method()==='OPTIONS')return r.fallback();held=true;await waiting;
  return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'prepared',account_id:account,session_id:sessionId}});
 });
 await page.goto('/');await expect.poll(()=>held).toBe(true);await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 const other=await context.newPage();await other.addInitScript(fault=>{
  if(fault==='absent')Object.defineProperty(navigator,'locks',{value:undefined,configurable:true});
  else{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1')throw new Error('fixture_private_storage_failed');return set.call(this,key,value);};}
 },fault);
 await other.goto('/');await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();
 await other.getByRole('button',{name:'Sign out',exact:true}).click();await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>localStorage.getItem('pts-auth')===null)).toBe(true);
 release();await page.waitForLoadState('networkidle');
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return !saved?.token&&!saved?.refreshToken&&!saved?.revocationToken&&!saved?.replacement;})).toBe(true);
 await expect.poll(()=>page.evaluate(()=>window.heldAuthNotifications.length)).toBeGreaterThan(0);
 await page.evaluate(()=>{window.holdAuthNotifications=false;for(const deliver of window.heldAuthNotifications)deliver();window.heldAuthNotifications=[];});
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await other.close();
});

for(const fault of ['absent'])test('queued final custody write rejects physical SDK logout while auth notifications are held',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 let held=false,release;const waiting=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await context.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(installAuthNotificationHold,true);
 await page.addInitScript(original=>{
  if(!sessionStorage.getItem('combined-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('combined-seeded','true');}
  // Delay cross-tab notifications so freshness must inspect actual shared auth
  // storage, independently of eventual subscription/event delivery.
 },original);
 await page.route(origin+'/api/file-session/prepare',async r=>{
  if(r.request().method()==='OPTIONS')return r.fallback();held=true;await waiting;
  return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'prepared',account_id:account,session_id:sessionId}});
 });
 await page.goto('/');await expect.poll(()=>held).toBe(true);await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 const other=await context.newPage();await other.addInitScript(fault=>{
  if(fault==='absent')Object.defineProperty(navigator,'locks',{value:undefined,configurable:true});
  else{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1')throw new Error('fixture_private_storage_failed');return set.call(this,key,value);};}
 },fault);
 await other.goto('/');await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();
 await page.evaluate(()=>{
  window.finalLockHeld=false;
  void navigator.locks.request('pts-file-cleanup-v1',async()=>{window.finalLockHeld=true;await new Promise(done=>window.releaseFinalLock=done);});
 });
 await page.waitForFunction(()=>window.finalLockHeld===true);
 release();
 await page.waitForFunction(async()=>{const locks=await navigator.locks.query();return locks.pending.some(lock=>lock.name==='pts-file-cleanup-v1');});
 await other.getByRole('button',{name:'Sign out',exact:true}).click();await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>localStorage.getItem('pts-auth')===null)).toBe(true);
 await page.evaluate(()=>window.releaseFinalLock());await page.waitForLoadState('networkidle');
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return !saved?.token&&!saved?.refreshToken&&!saved?.revocationToken&&!saved?.replacement;})).toBe(true);
 await expect.poll(()=>page.evaluate(()=>window.heldAuthNotifications.length)).toBeGreaterThan(0);
 await page.evaluate(()=>{window.holdAuthNotifications=false;for(const deliver of window.heldAuthNotifications)deliver();window.heldAuthNotifications=[];});
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await other.close();
});


test('short-lived provider session prepares cleanup without a session-load refresh loop',async({page})=>{
 await ordinaryFixture(page);let refreshes=0;
 function shortSession(label){
  const value=sessionFor(account,original.user.email,label),expires=Math.floor(Date.now()/1000)+60;
  const [header,payload,signature]=value.access_token.split('.');const claims=JSON.parse(Buffer.from(payload,'base64url').toString());claims.exp=expires;
  return {...value,access_token:[header,Buffer.from(JSON.stringify(claims)).toString('base64url'),signature].join('.'),expires_in:60,expires_at:expires};
 }
 await page.addInitScript(session=>localStorage.setItem('pts-auth',JSON.stringify(session)),shortSession('short-initial'));
 await page.route('**/auth/v1/token*',r=>{refreshes++;return r.fulfill({json:shortSession('short-refresh-'+refreshes)});});
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token),null,{timeout:5000});
 expect(refreshes).toBeLessThan(10);
});

test('ordinary logout preserves native custody prepared by another tab during provider logout for honest Retry',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);await ordinaryFixture(page);
 let release,started=false,revoked=false,clears=0;const held=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await context.route('**/auth/v1/logout*',async r=>{started=true;await held;revoked=true;return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.route(origin+'/api/file-session/clear',r=>{clears++;return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});});
 await page.route(origin+'/api/file-session/prepare',r=>r.fulfill({status:403,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'file_cleanup_unavailable'}}}));
 await page.addInitScript(original=>{if(!sessionStorage.getItem('new-custody-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('new-custody-seeded','true');}},original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForLoadState('networkidle');
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect.poll(()=>started).toBe(true);
 const other=await context.newPage();await other.goto('/');await other.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 release();
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await page.evaluate(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token))).toBe(true);expect(clears).toBe(0);
 await page.reload();await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).pending===true)).toBe(true);
 await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);expect(clears).toBeGreaterThan(0);await other.close();
});

for(const sameAccount of [false,true])test('delayed native logout preserves another real tab later '+(sameAccount?'same-account independent session':'different-account session')+' and fresh custody',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 const next=sessionFor(sameAccount?account:replacement.user.id,'replacement@example.invalid','later-independent','77777777-7777-4777-8777-777777777777');
 const revokes=[];let held=false,release;const waiting=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+next.access_token?next.user:original.user}));
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:next}));
 await context.route('**/auth/v1/logout*',r=>{revokes.push(r.request().headers().authorization);return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(original=>{if(!sessionStorage.getItem('later-session-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('later-session-seeded','true');}},original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.route(origin+'/api/file-session/clear',async r=>{
  if(r.request().method()==='OPTIONS')return r.fallback();held=true;await waiting;
  return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:'absent'}});
 });
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect.poll(()=>held&&revokes.length>0).toBe(true);
 const other=await context.newPage();await other.goto('/');await other.getByRole('button',{name:/^(Retry )?Sign out$/,exact:true}).first().click();
 await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await other.getByLabel('Email',{exact:true}).fill(next.user.email);await other.getByLabel('Password',{exact:true}).fill('fixture-password');await other.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();
 await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token===token,next.access_token);
 const before=await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;});
 release();await page.waitForLoadState('networkidle');
 expect(revokes.includes('Bearer '+next.access_token),'stale operation revoked later verified provider session').toBe(false);
 expect(await other.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,next.refresh_token),'later SDK pair was overwritten or cleared').toBe(true);
 expect(await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;}),'later custody was erased or changed').toEqual(before);
 await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toHaveCount(0);await other.close();
});

for(const reject of [false,true])test('account observation clears prior rendered actions and late results before '+(reject?'rejected':'held')+' claims verification',async({page})=>{
 await ordinaryFixture(page);
 await page.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+original.access_token?original.user:replacement.user}));
 const poem={id:'OLD',title:'Prior account poem',text:'Prior private text',source_id:'SOURCE',creator:{name:'Poet'},classification:{},geography:{},quality:{},source:{citation:'Prior citation'}};
 const corpus={poems:[poem],sources:[{id:'SOURCE',title:'Source'}],rights:[],source_documents:[],total:1,collection_total:1,filters:{},witnesses:[]};
 let late,lateStarted=false;const waiting=new Promise(done=>late=done);
 await page.route('http://127.0.0.1:8010/**',async r=>{
  if(new URL(r.request().url()).pathname==='/api/poetry/OLD'){lateStarted=true;await waiting;return r.fulfill({json:{poem,evidence:corpus,citation:'Prior citation'}});}
  return r.fulfill({json:corpus});
 });
 await page.addInitScript(original=>{localStorage.setItem('pts-auth',JSON.stringify(original));Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copied=text;}}});},original);
 await page.goto('/');await expect(page.getByRole('heading',{name:poem.title})).toBeVisible();await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();await expect.poll(()=>lateStarted).toBe(true);
 await page.evaluate(async({replacement,reject})=>{
  const {auth}=await import('/src/auth.ts');const claims=auth.getClaims.bind(auth);
  auth.getClaims=token=>token===replacement.access_token?new Promise((resolve,rejectPromise)=>{window.releaseClaims=()=>reject?rejectPromise(new Error('fixture_claims_unavailable')):resolve({data:{claims:{sub:replacement.user.id,session_id:'66666666-6666-4666-8666-666666666666'}},error:null});}):claims(token);
  window.switchSession=auth.setSession({access_token:replacement.access_token,refresh_token:replacement.refresh_token});
 },{replacement:sessionFor(replacement.user.id,replacement.user.email,'replacement','66666666-6666-4666-8666-666666666666'),reject});
 await page.waitForFunction(()=>typeof window.releaseClaims==='function');
 await expect(page.getByRole('heading',{name:poem.title})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Copy poem with citation',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Export results (JSON)'})).toHaveCount(0);await expect(page.getByRole('button',{name:'Open source document'})).toHaveCount(0);
 late();await page.waitForTimeout(100);expect(await page.evaluate(()=>window.copied||'')).toBe('');
 if(reject){await page.evaluate(()=>window.releaseClaims());await expect(page.getByRole('button',{name:'Retry Sign out',exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:poem.title})).toHaveCount(0);}
});

test('automatic switch catch tolerates unreadable custody and exposes bounded Retry',async({page})=>{
 await ordinaryFixture(page);await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+original.access_token?original.user:replacement.user}));
 await page.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.route(origin+'/api/file-session/clear',async r=>{
  if(r.request().method()==='OPTIONS')return r.fallback();
  await page.evaluate(()=>{const read=Storage.prototype.getItem;Storage.prototype.getItem=function(key){if(key==='pts-file-cleanup-v1')throw new Error('fixture_read_failed');return read.call(this,key);};});
  return r.fulfill({status:503,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'current_session_unavailable'}}});
 });
 await page.evaluate(async next=>{const {auth}=await import('/src/auth.ts');window.switchSession=auth.setSession({access_token:next.access_token,refresh_token:next.refresh_token});},sessionFor(replacement.user.id,replacement.user.email,'replacement','66666666-6666-4666-8666-666666666666'));
 await expect(page.getByRole('button',{name:'Retry Sign out',exact:true})).toBeVisible();
 await expect(page.getByText('Checking your session…',{exact:true})).toHaveCount(0);await expect(page.getByText('0 poems and excerpts shown')).toHaveCount(0);
});

for(const sameAccount of [false,true])test('later independent session survives delayed final SDK original logout '+(sameAccount?'within same account':'across accounts'),async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 const next=sessionFor(sameAccount?account:replacement.user.id,'replacement@example.invalid','during-sdk','77777777-7777-4777-8777-777777777777');
 let count=0,held=false,release;const waiting=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>r.fulfill({json:r.request().headers().authorization==='Bearer '+next.access_token?next.user:original.user}));
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:next}));
 await context.route('**/auth/v1/logout*',async r=>{
  expect(r.request().headers().authorization==='Bearer '+original.access_token,'later session reached old provider logout').toBe(true);
  if(++count===2){held=true;await waiting;}return r.fulfill({status:204});
 });
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(original=>{if(!sessionStorage.getItem('sdk-delay-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('sdk-delay-seeded','true');}},original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect.poll(()=>held).toBe(true);
 const other=await context.newPage();await other.goto('/');
 await other.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const result=await auth.signOut({scope:'local'});if(result.error)throw result.error;});
 await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await other.getByLabel('Email',{exact:true}).fill(next.user.email);await other.getByLabel('Password',{exact:true}).fill('fixture-password');await other.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token===token,next.access_token);
 const before=await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;});
 release();await page.waitForLoadState('networkidle');
 expect(await other.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,next.refresh_token),'SDK response erased later pair').toBe(true);
 expect(await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;}),'SDK response erased later custody').toEqual(before);
 await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await other.close();
});

for(const sameAccount of [false,true])test('automatic switch cannot restore obsolete replacement over later SDK-only '+(sameAccount?'same-account independent session':'different-account independent session'),async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 const obsolete=sessionFor(account,original.user.email,'obsolete-replacement','66666666-6666-4666-8666-666666666666');
 const next=sessionFor(sameAccount?account:replacement.user.id,'later@example.invalid','sdk-only-later','77777777-7777-4777-8777-777777777777');
 const revokes=[];let held=false,release;const waiting=new Promise(done=>release=done);
 await context.route('**/auth/v1/user',r=>{const token=r.request().headers().authorization;return r.fulfill({json:token==='Bearer '+next.access_token?next.user:token==='Bearer '+obsolete.access_token?obsolete.user:original.user});});
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:next}));
 await context.route('**/auth/v1/logout*',r=>{revokes.push(r.request().headers().authorization);return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(installAuthNotificationHold,false);
 await page.addInitScript(original=>{
  if(!sessionStorage.getItem('automatic-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('automatic-seeded','true');}
 },original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.route(origin+'/api/file-session/clear',async r=>{if(r.request().method()==='OPTIONS')return r.fallback();held=true;await waiting;return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:'absent'}});});
 await page.evaluate(async obsolete=>{const {auth}=await import('/src/auth.ts');await auth.setSession({access_token:obsolete.access_token,refresh_token:obsolete.refresh_token});},obsolete);
 await expect.poll(()=>held&&revokes.length>0).toBe(true);
 await page.evaluate(()=>{window.holdAuthNotifications=true;});
 const before=await page.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;});
 const other=await context.newPage();await other.addInitScript(()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1')throw new Error('fixture_private_storage_failed');return set.call(this,key,value);};});
 await other.goto('/');await other.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const result=await auth.signInWithPassword({email:'later@example.invalid',password:'fixture-password'});if(result.error)throw result.error;});
 await other.waitForFunction(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,next.refresh_token);
 await expect.poll(()=>page.evaluate(()=>window.heldAuthNotifications.length)).toBeGreaterThan(0);
 expect(await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;}),'fixture must establish replacement without changing durable private custody').toEqual(before);
 release();await page.waitForLoadState('networkidle');
 expect(await other.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,next.refresh_token),'old automatic switch restored obsolete SDK recovery pair').toBe(true);
 expect(revokes.includes('Bearer '+next.access_token),'old automatic switch revoked later independent session').toBe(false);
 await expect(page.getByText('Checking your session…',{exact:true})).toHaveCount(0);await other.close();
});

test('current native clear401 prepares receipt and completes first Sign out with its own revision handoff',async({page})=>{
 await ordinaryFixture(page);let clearCalls=0,preparations=0,revoked=false;
 const headers={'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'};
 await page.route(origin+'/api/file-session/prepare',r=>{if(r.request().method()==='OPTIONS')return r.fallback();preparations++;return r.fulfill({headers,json:{status:'prepared',account_id:account,session_id:sessionId}});});
 await page.route(origin+'/api/file-session/clear',r=>{if(r.request().method()==='OPTIONS')return r.fallback();clearCalls++;return clearCalls===2?r.fulfill({status:401,headers,json:{detail:{code:'file_cleanup_proof_required'}}}):r.fulfill({headers,json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:clearCalls===1?'present':revoked?'absent':'present'}});});
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revoked=true;return r.fulfill({status:204});});
 await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 const before=preparations;await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
 expect(preparations).toBeGreaterThan(before);expect(clearCalls).toBeGreaterThanOrEqual(3);expect(revoked).toBe(true);
 expect(await page.evaluate(()=>{const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return localStorage.getItem('pts-auth')===null&&value?.cleared===true&&!value.token&&!value.refreshToken&&!value.revocationToken&&!value.replacement;})).toBe(true);
});

test('revoked original getUser401 during private-fault Retry clears SDK and completes first Retry',async({page})=>{
 await ordinaryFixture(page);let revoked=false,user401s=0,logoutCalls=0,absentProofs=0;
 await page.route('**/auth/v1/user',r=>{if(revoked){user401s++;return r.fulfill({status:401,json:{error_code:'session_not_found',msg:'Fixture original session absent'}});}return r.fulfill({json:original.user});});
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);logoutCalls++;if(revoked)return r.fulfill({status:403,json:{error_code:'session_not_found',msg:'Fixture original session absent'}});revoked=true;return r.fulfill({status:204});});
 await page.route('**/auth/v1/token*',r=>r.fulfill({status:400,json:{error_code:'refresh_token_not_found',msg:'Fixture revoked original refresh'}}));
 await page.route(origin+'/api/file-session/clear',r=>{if(r.request().method()==='OPTIONS')return r.fallback();if(revoked)absentProofs++;return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});});
 await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await privateFault(page,'absent');await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();expect(revoked).toBe(true);
 await privateFault(page,'absent',false);await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();
 await expect.poll(()=>user401s).toBeGreaterThan(0);
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return localStorage.getItem('pts-auth')===null&&saved?.cleared===true&&!saved.token&&!saved.refreshToken&&!saved.revocationToken&&!saved.replacement;}),'first actual Retry left original cleanup credentials').toBe(true);
 expect(logoutCalls).toBeGreaterThanOrEqual(2);expect(absentProofs).toBeGreaterThan(0);await expect(page.getByRole('alert')).toHaveCount(0);
});

for(const sameAccount of [false,true])test('delayed real SDK profile401 preserves later '+(sameAccount?'same-account':'different-account')+' session while newer claims overlap',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 const candidate=sessionFor(replacement.user.id,'candidate@example.invalid','candidate-profile','66666666-6666-4666-8666-666666666666');
 const later=sessionFor(sameAccount?candidate.user.id:'88888888-8888-4888-8888-888888888888','later@example.invalid','later-profile','77777777-7777-4777-8777-777777777777');
 const rotated=sessionFor(later.user.id,later.user.email,'later-profile-rotated','77777777-7777-4777-8777-777777777777');
 let oldHeld=false,newHeld=false,releaseOld,releaseNew,candidateProfiles=0,laterRevokes=0;
 const oldWait=new Promise(done=>releaseOld=done),newWait=new Promise(done=>releaseNew=done);
 await context.route('**/auth/v1/user',r=>{const bearer=r.request().headers().authorization;return r.fulfill({json:bearer==='Bearer '+candidate.access_token?candidate.user:[later.access_token,rotated.access_token].includes(bearer?.replace(/^Bearer /,''))?later.user:original.user});});
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:new URL(r.request().url()).searchParams.get('grant_type')==='refresh_token'?rotated:later}));
 await context.route('**/auth/v1/logout*',r=>{if([later.access_token,rotated.access_token].includes(r.request().headers().authorization?.replace(/^Bearer /,'')))laterRevokes++;return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(installAuthNotificationHold,false);
 await page.addInitScript(original=>{if(!sessionStorage.getItem('profile-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('profile-seeded','true');}},original);
 await page.route('**/auth/v1/user',async r=>{
  const bearer=r.request().headers().authorization;
  if(bearer==='Bearer '+candidate.access_token&&++candidateProfiles===2){oldHeld=true;await oldWait;return r.fulfill({status:401,json:{error_code:'session_not_found',msg:'Fixture obsolete profile session absent'}});}
  if(bearer==='Bearer '+rotated.access_token){newHeld=true;await newWait;}
  return r.fallback();
 });
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.evaluate(async next=>{const {auth}=await import('/src/auth.ts');await auth.setSession({access_token:next.access_token,refresh_token:next.refresh_token});},candidate);
 await expect.poll(()=>oldHeld).toBe(true);await page.evaluate(()=>{window.holdAuthNotifications=true;});
 const other=await context.newPage();await other.goto('/');await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();
 await other.getByRole('button',{name:'Sign out',exact:true}).click();await expect(other.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 await other.getByLabel('Email',{exact:true}).fill(later.user.email);await other.getByLabel('Password',{exact:true}).fill('fixture-password');await other.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token===token,later.access_token);
 // A real same-session SDK refresh changes credentials while a private-lock
 // fault keeps durable custody at B1. The old App must verify real B2 claims.
 await privateFault(other,'absent');
 await other.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const result=await auth.refreshSession();if(result.error)throw result.error;});
 await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.access_token===token,rotated.access_token);
 await page.waitForFunction(()=>{const sdk=JSON.parse(localStorage.getItem('pts-auth'));return window.heldAuthNotifications.some(deliver=>deliver.authData?.event==='TOKEN_REFRESHED'&&deliver.authData.session?.access_token===sdk.access_token);});
 await page.evaluate(()=>{const sdk=JSON.parse(localStorage.getItem('pts-auth'));const deliver=window.heldAuthNotifications.findLast(deliver=>deliver.authData?.event==='TOKEN_REFRESHED'&&deliver.authData.session?.access_token===sdk.access_token);window.holdAuthNotifications=false;deliver();window.holdAuthNotifications=true;});
 await expect.poll(()=>newHeld).toBe(true);
 const custody=await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;});
 const failed=page.waitForResponse(response=>new URL(response.url()).pathname==='/auth/v1/user'&&response.status()===401).then(response=>response.finished());
 releaseOld();await failed;await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,100)));
 expect(await other.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,rotated.refresh_token),'obsolete profile401 removed later SDK pair during overlapping current claims').toBe(true);
 expect(await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;}),'obsolete profile401 changed later native custody').toEqual(custody);expect(laterRevokes).toBe(0);
 releaseNew();await privateFault(other,'absent',false);await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();expect(laterRevokes).toBe(0);await other.close();
});

test('receipted first Sign out completes after redundant SDK profile403 proves original absent',async({page})=>{
 await ordinaryFixture(page);let revoked=false,profiles403=0,absentProofs=0,logoutCalls=0;
 await page.route('**/auth/v1/user',r=>{if(revoked){profiles403++;return r.fulfill({status:403,json:{error_code:'session_not_found',msg:'Fixture revoked original absent'}});}return r.fulfill({json:original.user});});
 await page.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);logoutCalls++;revoked=true;return r.fulfill({status:204});});
 await page.route(origin+'/api/file-session/clear',r=>{if(r.request().method()==='OPTIONS')return r.fallback();if(revoked)absentProofs++;return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});});
 await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect.poll(()=>profiles403).toBeGreaterThan(0);expect(absentProofs).toBeGreaterThan(0);expect(logoutCalls).toBeGreaterThan(0);
 expect(await page.evaluate(()=>localStorage.getItem('pts-auth')===null),'real SDK missing-session profile response must remove its own original pair').toBe(true);
 await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return saved?.cleared===true&&!saved.token&&!saved.refreshToken&&!saved.revocationToken&&!saved.replacement;})).toBe(true);
});

for(const sameAccount of [false,true])test('obsolete queued SDK refresh profile403 preserves already-current '+(sameAccount?'same-account':'different-account')+' independent session',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);
 const rotated=sessionFor(account,original.user.email,'queued-original-rotation',sessionId);
 const later=sessionFor(sameAccount?account:replacement.user.id,'later@example.invalid','after-queued-rotation','77777777-7777-4777-8777-777777777777');
 let refuseRotated=false,profile403=0,laterRevokes=0;
 await context.route('**/auth/v1/user',r=>{const token=r.request().headers().authorization?.replace(/^Bearer /,'');if(refuseRotated&&token===rotated.access_token){profile403++;return r.fulfill({status:403,json:{error_code:'session_not_found',msg:'Fixture obsolete original absent'}});}return r.fulfill({json:token===later.access_token?later.user:original.user});});
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:new URL(r.request().url()).searchParams.get('grant_type')==='refresh_token'?rotated:later}));
 await context.route('**/auth/v1/logout*',r=>{if(r.request().headers().authorization==='Bearer '+later.access_token)laterRevokes++;return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.addInitScript(installAuthNotificationHold,false);
 await page.addInitScript(original=>{if(!sessionStorage.getItem('queued-profile-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('queued-profile-seeded','true');}},original);
 await page.goto('/');await page.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token===token,original.access_token);
 await page.evaluate(()=>{window.holdAuthNotifications=true;});
 const other=await context.newPage();await other.goto('/');await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();
 await privateFault(other,'absent');
 await other.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const result=await auth.refreshSession();if(result.error)throw result.error;});
 await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.access_token===token,rotated.access_token);
 await other.waitForLoadState('networkidle');
 await page.waitForFunction(token=>window.heldAuthNotifications.some(deliver=>deliver.authData?.event==='TOKEN_REFRESHED'&&deliver.authData.session?.access_token===token),rotated.access_token);
 await other.evaluate(async email=>{const {auth}=await import('/src/auth.ts');const result=await auth.signInWithPassword({email,password:'fixture-password'});if(result.error)throw result.error;},later.user.email);
 await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===token,later.refresh_token);
 await expect(other.getByRole('alert').filter({hasText:switchingFailure})).toBeVisible();
 const custody=await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;});
 expect(custody.token,'private fault must keep original A1 custody').toBe(original.access_token);expect(laterRevokes).toBe(0);
 refuseRotated=true;
 await page.evaluate(token=>{const deliver=window.heldAuthNotifications.find(deliver=>deliver.authData?.event==='TOKEN_REFRESHED'&&deliver.authData.session?.access_token===token);window.holdAuthNotifications=false;deliver();window.holdAuthNotifications=true;},rotated.access_token);
 await expect.poll(()=>profile403).toBeGreaterThan(0);await page.waitForLoadState('networkidle');
 expect(await other.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,later.refresh_token),'obsolete queued profile403 removed already-current independent SDK pair').toBe(true);
 expect(await other.evaluate(()=>{const {revision,...record}=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return record;}),'obsolete queued profile403 changed durable original custody').toEqual(custody);expect(laterRevokes).toBe(0);
 await expect(page.getByRole('alert').filter({hasText:'We could not verify your session. Please retry Sign out.'})).toBeVisible();await expect(page.getByText('0 poems and excerpts shown')).toHaveCount(0);await other.close();
});

test('held same-account replacement claims do not gate independent original provider logout under private fault',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);await ordinaryFixture(page);
 const next=sessionFor(account,original.user.email,'held-same-account-provider','66666666-6666-4666-8666-666666666666');
 let profiles=0,held=false,release;const wait=new Promise(done=>release=done),revokes=[];
 await page.route('**/auth/v1/user',async r=>{if(r.request().headers().authorization==='Bearer '+next.access_token&&++profiles===2){held=true;await wait;}return r.fulfill({json:original.user});});
 await page.route('**/auth/v1/logout*',r=>{revokes.push(r.request().headers().authorization);return r.fulfill({status:204});});
 await page.addInitScript(original=>localStorage.setItem('pts-auth',JSON.stringify(original)),original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await privateFault(page,'absent');
 await page.evaluate(async next=>{const {auth}=await import('/src/auth.ts');await auth.setSession({access_token:next.access_token,refresh_token:next.refresh_token});},next);
 await expect.poll(()=>held).toBe(true);await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect.poll(()=>revokes.includes('Bearer '+original.access_token),'held unrelated claims must not gate exact-original provider request').toBe(true);
 expect(revokes.includes('Bearer '+next.access_token)).toBe(false);
 expect(await page.evaluate(expected=>JSON.parse(localStorage.getItem('pts-auth')||'null')?.refresh_token===expected,next.refresh_token)).toBe(true);
 release();await page.waitForLoadState('networkidle');
});

test('ordinary SDK session observation cannot gate original provider logout when healthy reader prepares same-session custody',async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);await ordinaryFixture(page);
 const revokes=[];
 await context.route('**/auth/v1/user',r=>r.fulfill({json:original.user}));
 await context.route('**/auth/v1/logout*',r=>{revokes.push(r.request().headers().authorization);return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.route(origin+'/api/file-session/prepare',r=>r.fulfill({status:503,headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{detail:{code:'fixture_initial_prepare_unavailable'}}}));
 await page.addInitScript(original=>{if(!sessionStorage.getItem('ordinary-observation-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('ordinary-observation-seeded','true');}},original);
 await page.goto('/');await expect(page.getByText('0 poems and excerpts shown')).toBeVisible();await page.waitForLoadState('networkidle');
 expect(await page.evaluate(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token))).toBe(false);
 await privateFault(page,'absent');
 // Delay only delivery of the real public SDK result. Its session load and
 // provider behavior remain actual; no session/result/completion is fabricated.
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const get=auth.getSession.bind(auth);let once=true;auth.getSession=async(...args)=>{const result=await get(...args);if(once){once=false;window.actualSDKObservationHeld=true;await new Promise(done=>window.releaseSDKObservation=done);}return result;};});
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.waitForFunction(()=>window.actualSDKObservationHeld===true);
 const other=await context.newPage();await other.goto('/');await expect(other.getByText('0 poems and excerpts shown')).toBeVisible();await other.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token===token,original.access_token);
 await privateFault(page,'absent',false);await page.evaluate(()=>window.releaseSDKObservation());
 await expect.poll(()=>revokes.includes('Bearer '+original.access_token),'same-session native preparation must not gate exact-original provider attempt').toBe(true);
 expect(revokes.every(token=>token==='Bearer '+original.access_token)).toBe(true);
 await expect(page.getByRole('alert').filter({hasText:signingOutFailure})).toBeVisible();
 expect(await other.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return saved?.pending===true&&Boolean(saved.token);}), 'new same-original native custody must remain pending for honest Retry').toBe(true);await other.close();
});

for(const peerRetained of [false,true])test('same-original SDK missing-session removal in another App completes first proven native Sign out'+(peerRetained?' after peer-owned recovery revision':''),async({page,context})=>{
 const {files}=require('./file-fixture.cjs');await files(context);await ordinaryFixture(page);
 let revoked=false,proofHeld=false,profiles403=0,release,claimsHeld=false,releaseClaims;const wait=new Promise(done=>release=done),claimsWait=new Promise(done=>releaseClaims=done);
 await context.route('**/auth/v1/user',r=>{if(revoked){profiles403++;return r.fulfill({status:403,json:{error_code:'session_not_found',msg:'Fixture original provider session absent'}});}return r.fulfill({json:original.user});});
 await context.route('**/auth/v1/logout*',r=>{expect(r.request().headers().authorization==='Bearer '+original.access_token).toBe(true);revoked=true;return r.fulfill({status:204});});
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}}));
 await page.route(origin+'/api/file-session/clear',async r=>{if(r.request().method()==='OPTIONS')return r.fallback();if(revoked){proofHeld=true;await wait;}return r.fulfill({headers:{'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true'},json:{status:'cleared',account_id:account,session_id:sessionId,provider_session:revoked?'absent':'present'}});});
 if(peerRetained)await page.route('**/auth/v1/user',async r=>{if(!claimsHeld){claimsHeld=true;await claimsWait;}return r.fulfill({json:original.user});});
 await page.addInitScript(installAuthNotificationHold,false);
 await page.addInitScript(original=>{if(!sessionStorage.getItem('nil-convergence-seeded')){localStorage.setItem('pts-auth',JSON.stringify(original));sessionStorage.setItem('nil-convergence-seeded','true');}},original);
 await page.goto('/');await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 let other;
 if(peerRetained){
  await expect.poll(()=>claimsHeld).toBe(true);await page.evaluate(()=>{window.holdAuthNotifications=true;});
  const originalRecord=await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1'))),originalRevision=originalRecord.revision;
  other=await context.newPage();await other.goto('/');
  await other.waitForFunction(({token,revision})=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1'));return saved.pending===true&&saved.token===token&&saved.revocationToken===token&&saved.revision!==revision;},{token:original.access_token,revision:originalRevision});
  const peerRecord=await other.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')));
  const {revision:oldRevision,revocationToken:oldRevocation,...beforeBase}=originalRecord,{revision:newRevision,revocationToken:newRevocation,...afterBase}=peerRecord;
  expect(afterBase,'peer recovery may change only revision and its verified original revocation token').toEqual(beforeBase);expect(newRevocation).toBe(original.access_token);expect(newRevision).not.toBe(oldRevision);
  releaseClaims();
 }
 await expect.poll(()=>proofHeld).toBe(true);
 await page.evaluate(()=>{window.holdAuthNotifications=true;});const before=await page.evaluate(()=>localStorage.getItem('pts-file-cleanup-v1'));
 if(!other){other=await context.newPage();await other.goto('/');}
 else await other.evaluate(async token=>{const {auth}=await import('/src/auth.ts');await auth.getClaims(token);},original.access_token);
 await expect.poll(()=>profiles403).toBeGreaterThan(0);await other.waitForFunction(()=>localStorage.getItem('pts-auth')===null);
 expect(await other.evaluate(()=>localStorage.getItem('pts-file-cleanup-v1')),'SDK-only missing-session removal must leave exact owned private observation unchanged').toBe(before);
 await expect.poll(()=>page.evaluate(()=>window.heldAuthNotifications.length)).toBeGreaterThan(0);
 release();await page.waitForLoadState('networkidle');await expect(page.getByRole('heading',{name:'Sign in to read',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>{const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');return localStorage.getItem('pts-auth')===null&&saved?.cleared===true&&!saved.token&&!saved.refreshToken&&!saved.revocationToken&&!saved.replacement;}),'proven original absence with unchanged private custody left credentials after same-original SDK removal').toBe(true);
 await expect(page.getByRole('alert')).toHaveCount(0);await other.close();
});
