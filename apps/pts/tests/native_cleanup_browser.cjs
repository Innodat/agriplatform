// Actual browser/auth owners and TLS; faults affect only this fresh fixture.
const fs=require('node:fs');const assert=require('node:assert/strict');const {execFileSync}=require('node:child_process');
const {createHash}=require('node:crypto');
const {chromium}=require('../../../node_modules/@playwright/test');
const {login,ownContext,statuses}=require('./native_browser.cjs');
const {installAuthNotificationHold}=require('../web/tests/file-fixture.cjs');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const checks=[];
const progress=config.output+'/native-cleanup-browser-progress.jsonl';
fs.writeFileSync(progress,'',{mode:0o600,flag:'wx'});
function observe(observation){fs.appendFileSync(progress,JSON.stringify({observed_at:new Date().toISOString(),...observation})+'\n');}
function checkpoint(observation){checks.push(observation);observe(observation);}
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const failText='We could not finish signing you out. Please retry Sign out.';
async function record(page){
 const counts={};const listener=response=>{const url=new URL(response.url());const operation=url.pathname==='/auth/v1/token'?'provider-token':url.pathname==='/api/file-session/prepare'?'cleanup-prepare':null;if(operation){const key=operation+'-'+response.status();counts[key]=(counts[key]||0)+1;}};
 page.on('response',listener);
 try{await page.waitForFunction(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token));return await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')));}
 catch(error){await stateObservation(page,'cleanup-record-timeout');observe({phase:'cleanup-record-timeout',safe_operation_status_counts:counts});throw error;}
 finally{page.off('response',listener);}
}
function cleanupCleared(){
 const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');
 return !value||(value.version===1&&value.cleared===true&&typeof value.revision==='string'&&Object.keys(value).every(key=>['version','cleared','revision'].includes(key)));
}
async function noCleanupCredentials(page){return page.evaluate(cleanupCleared);}
async function clearedCustodySettled(page){return page.evaluate(async()=>{
 // Observe the private custody queue after the selected response finishes, not
 // unrelated SDK network activity. Any credential resurrection fails at once;
 // do not wait for it to be removed again. Require a stable clear interval.
 let stableSince;const deadline=performance.now()+2500;
 do{
  const value=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null');
  if(value&&!(value.version===1&&value.cleared===true&&typeof value.revision==='string'&&Object.keys(value).every(key=>['version','cleared','revision'].includes(key))))return false;
  const locks=await navigator.locks.query();
  const active=[...locks.held,...locks.pending].some(lock=>lock.name==='pts-file-cleanup-v1');
  if(active)stableSince=undefined;
  else if(stableSince===undefined)stableSince=performance.now();
  else if(performance.now()-stableSince>=250)return true;
  await new Promise(resolve=>setTimeout(resolve,25));
 }while(performance.now()<deadline);
 return false;
});}
async function clearProof(page,token){return page.evaluate(async({files,token})=>{const response=await fetch(files+'/api/file-session/clear',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}});return {status:response.status,body:await response.json()};},{files:config.files,token});}
async function stateObservation(page,phase){
 const state=await page.evaluate(()=>{
  const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null'),session=JSON.parse(localStorage.getItem('pts-auth')||'null');
  const expired=token=>{if(!token)return null;try{return JSON.parse(atob(token.split('.')[1].replaceAll('-','+').replaceAll('_','/'))).exp*1000<=Date.now();}catch{return null;}};
  const text=document.body.textContent||'';
  return {window_open_calls:Number.isSafeInteger(window.actualNativeOpenCalls)?window.actualNativeOpenCalls:null,checking_session_visible:text.includes('Checking your session…'),signed_out_heading_visible:text.includes('Sign in to read'),collection_result_visible:/\d+ poems and excerpts shown/.test(text),cleanup_present:Boolean(saved?.token),cleanup_pending:saved?.pending===true,sdk_session_present:Boolean(session),sdk_account_matches_original:Boolean(saved?.token&&session?.user?.id===saved.id),sdk_credential_matches_recovery:Boolean(saved?.token&&session?.access_token===saved.revocationToken),sdk_refresh_matches_retained:Boolean(saved?.token&&session?.refresh_token===saved.refreshToken),original_credential_expired:expired(saved?.token),recovery_credential_expired:expired(saved?.revocationToken),sdk_credential_expired:expired(session?.access_token),document_open_error_visible:text.includes('We could not open the document. Please retry.'),session_or_access_changed_visible:text.includes('Session or access changed. Please try again.'),document_signin_required_visible:text.includes('Please sign in again to reopen this document.'),known_error:text.includes('We could not finish signing you out.')?'file_cleanup_incomplete':text.includes('We could not finish switching accounts.')?'switch_cleanup_incomplete':text.includes('We could not sign you out.')?'ordinary_auth_logout_failed':null};
 });observe({phase,...state});
}
function operationObservations(page,phase){
 page.on('response',async response=>{
  const url=new URL(response.url());
  const method=response.request().method();
  const operation=url.pathname==='/auth/v1/token'&&url.searchParams.get('grant_type')==='refresh_token'?'provider-refresh':url.pathname==='/auth/v1/logout'?'provider-local-logout':url.pathname==='/auth/v1/user'&&method==='GET'?'provider-profile-check':url.pathname==='/api/file-session/prepare'?'file-prepare':url.pathname==='/api/file-session'?'file-setup':url.pathname.startsWith('/api/file-contexts/')?'file-context':url.pathname.startsWith('/api/files/')?'native-file-read':url.pathname.startsWith('/api/documents/')?'document-metadata':null;
  if(operation){
   let provider_error_id=null;
   if(response.status()>=400)try{const body=await response.json(),code=body.error_code||body.code||body.detail?.code;if(typeof code==='string'&&/^[a-z_]{1,64}$/.test(code))provider_error_id=code;}catch{/* Never record raw error text/payloads. */}
   observe({phase,operation,method,status:response.status(),range_requested:Boolean(response.request().headers().range),provider_error_id});
  }
  if(url.pathname==='/api/file-session/clear'){
   let provider_session='unavailable';try{const body=await response.json();if(['present','absent'].includes(body.provider_session))provider_session=body.provider_session;}catch{/* Only safe closed evidence is observed. */}
   observe({phase,operation:'file-cleanup',status:response.status(),provider_session});
  }
 });
}
async function signedOut(page){try{await page.getByRole('heading',{name:'Sign in to read',exact:true}).waitFor();await page.waitForFunction(cleanupCleared);}catch(error){await stateObservation(page,'signout-timeout');throw error;}}
async function replacementRestored(page,account,sessionId){
 await page.waitForFunction(({account,sessionId})=>{
  const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null'),session=JSON.parse(localStorage.getItem('pts-auth')||'null');
  if(!saved||saved.pending||saved.replacement||saved.id!==account||session?.user?.id!==account||saved.refreshToken!==session.refresh_token)return false;
  try{
   const claims=JSON.parse(atob(session.access_token.split('.')[1].replaceAll('-','+').replaceAll('_','/')));
   return claims.sub===account&&claims.session_id===saved.sessionId&&(!sessionId||saved.sessionId===sessionId)&&claims.exp*1000>Date.now()+1000&&!document.body.textContent.includes('We could not finish');
  }catch{return false;}
 },{account,sessionId},{timeout:45000});
 await page.getByRole('button',{name:'Sources',exact:true}).waitFor();
}
async function cleanupFailure(page){await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.getByRole('alert').filter({hasText:failText}).first().waitFor({timeout:45000});assert(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).pending===true),'pending cleanup custody missing');}

async function independentLogin(page,index){
 return page.evaluate(async subject=>{
  const result=await fetch('/auth/v1/token?grant_type=password',{method:'POST',headers:{'Content-Type':'application/json',apikey:'synthetic-public-key'},body:JSON.stringify({email:subject.email,password:subject.password})});
  if(result.status!==200)throw new Error('independent_provider_signin_failed');
  const session=await result.json();session.expires_at=Math.floor(Date.now()/1000)+session.expires_in;
  localStorage.setItem('pts-auth',JSON.stringify(session));
  const claims=JSON.parse(atob(session.access_token.split('.')[1].replaceAll('-','+').replaceAll('_','/')));
  return {account:session.user.id,sessionId:claims.session_id};
 },config.subjects[index]);
}
async function actualOpen(page,context){
 await page.getByRole('button',{name:'Sources',exact:true}).click();
 const document=page.getByRole('region',{name:config.document.title,exact:true,includeHidden:true});
 await document.waitFor({state:'attached'});
 const details=page.locator('details').filter({has:document}).first();
 if(await details.count()&&!await details.evaluate(element=>element.open))await details.locator('summary').first().click();
 const popup=context.waitForEvent('page');
 const response=context.waitForEvent('response',response=>response.url().startsWith(config.files+'/api/files/')&&response.status()===200);
 const [,viewer,opened]=await Promise.all([document.getByRole('button',{name:'Open document',exact:true}).click(),popup,response]);
 const url=opened.url();
 assert.deepEqual(await statuses(page,url),[206,200]);await viewer.close();return url;
}

async function sharedTabCleanup(browser){
  // Two real App tabs share SDK storage and private file custody. Hold tab A's
  // actual background owner200 after verification, selected by its verified
  // account/session rather than a bearer snapshot the existing SDK may rotate.
  // Open B only after the hold so it cannot consume A's arm; B then completes
  // provider/file cleanup before A receives it. No injected auth owner is used.
  const context=await browser.newContext();const page=await context.newPage();await login(page,0);const original=await record(page);const opened=await ownContext(page);
  fs.writeFileSync(config.gate_control+'/prepare-pair-armed',JSON.stringify({account_id:original.id,session_id:original.sessionId}),{mode:0o600,flag:'wx'});
  const lateAppPreparation=page.waitForResponse(response=>response.url()===config.files+'/api/file-session/prepare'&&response.request().method()==='POST'&&response.headers()['x-fixture-held-preparation']==='verified-owner-pair').then(async response=>{
   await response.finished();
   const body=await response.json();return {status:response.status(),account_matches_expected:body.account_id===original.id,session_matches_expected:body.session_id===original.sessionId};
  }).catch(error=>({error:error.name}));
  await page.reload({waitUntil:'domcontentloaded'});
  let heldDeadline=Date.now()+15000;while(!fs.existsSync(config.gate_control+'/prepare-held')){if(Date.now()>=heldDeadline){await stateObservation(page,'cross-tab-preparation-not-held');throw new Error('actual app preparation was not held');}await pause(50);}
  const held=JSON.parse(fs.readFileSync(config.gate_control+'/prepare-held','utf8'));
  assert.equal(held.actual_upstream_status,200);assert.equal(held.matched_by,'verified-owner-pair');assert(held.account_matches_expected&&held.session_matches_expected);
  const otherApp=await context.newPage();await otherApp.goto(config.frontend);await otherApp.getByText(/\d+ poems and excerpts shown/).waitFor();
  await otherApp.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(otherApp);
  await page.getByRole('heading',{name:'Sign in to read',exact:true}).waitFor();
  const crossTabAbsent=await clearProof(otherApp,original.token);assert.equal(crossTabAbsent.status,200);assert.equal(crossTabAbsent.body.provider_session,'absent');assert.equal(crossTabAbsent.body.session_id,original.sessionId);
  fs.writeFileSync(config.gate_control+'/prepare-release','release',{mode:0o600,flag:'wx'});
  const late=await lateAppPreparation;assert.equal(late.status,200);assert(late.account_matches_expected&&late.session_matches_expected);
  await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,0)));
  assert(await clearedCustodySettled(page),'late preparation resurrected credentials or failed to settle private custody');
  assert(await noCleanupCredentials(page),'late other-tab preparation resurrected original/replacement credentials');
  fs.writeFileSync(config.gate_control+'/file-origin-unavailable','fixture-only control-origin outage',{mode:0o600,flag:'wx'});
  try{
   await login(page,1);await page.getByText(/\d+ poems and excerpts shown/).waitFor();
   assert.equal(await page.getByRole('alert').count(),0);
   assert(await clearedCustodySettled(page),'unavailable preparation retained credentials after completed cleanup');
  }finally{fs.unlinkSync(config.gate_control+'/file-origin-unavailable');}
  assert.deepEqual(await statuses(page,opened.url),[401,401]);
  await actualOpen(page,context);assert.deepEqual(await statuses(page,opened.url),[404,404]);
  const finalOriginal=await record(page);operationObservations(page,'cross-tab-final-authorized-logout');
  await page.getByRole('button',{name:'Sign out',exact:true}).click();
  await page.waitForFunction(()=>document.body.textContent.includes('Sign in to read')||document.body.textContent.includes('We could not sign you out. Please try again.'));
  let ordinarySdkRetry=false;
  if(await page.getByRole('alert').filter({hasText:'We could not sign you out. Please try again.'}).count()){
   // Preserve the existing visible SDK failure and use the actual Sign out
   // recovery. Neither a generic owner denial nor empty SDK state proves revoke.
   const proof=await clearProof(page,finalOriginal.token);
   assert.equal(proof.status,200);assert.equal(proof.body.account_id,finalOriginal.id);assert.equal(proof.body.session_id,finalOriginal.sessionId);assert.equal(proof.body.provider_session,'absent');
   assert(await noCleanupCredentials(page));assert(await page.evaluate(()=>localStorage.getItem('pts-auth')===null));
   await page.getByRole('button',{name:'Sign out',exact:true}).click();ordinarySdkRetry=true;
  }
  await signedOut(page);assert.equal(await page.getByRole('alert').count(),0);
  checkpoint({case:'two-real-app-tabs-completed-cleanup-supersedes-held-owner200-preparation',actual_owner_preparation_status:200,provider_original_absence_before_release:true,no_original_or_replacement_credentials_after_release:true,ordinary_authorized_entry_during_control_origin_outage:true,old_file_context_denied:true,new_authorized_actual_Open:true,subsequent_authorized_logout_completed:true,retry_observed:ordinarySdkRetry});
  await otherApp.close();await context.close();
  for(const name of ['prepare-held','prepare-release','prepare-released'])fs.unlinkSync(config.gate_control+'/'+name);

}

// Faults apply only to the private key/lock in a NEW fixture browser. The SDK
// storage, provider, owner services and production UI code remain unchanged.
function installPrivateFault(fault){
 window.privateCleanupFault=fault;
 if(window.privateCleanupFaultInstalled)return;
 window.privateCleanupFaultInstalled=true;
 const locks=navigator.locks,request=locks?.request.bind(locks);
 Object.defineProperty(navigator,'locks',{configurable:true,get(){
  if(window.privateCleanupFault==='absent')return undefined;
  return {...locks,request(name,options,operation){
   if(name!=='pts-file-cleanup-v1'||!window.privateCleanupFault)return request(name,options,operation);
   if(window.privateCleanupFault==='timeout')return new Promise((_,reject)=>options.signal.addEventListener('abort',()=>reject(options.signal.reason),{once:true}));
   return request(name,options,operation);
  }};
 }});
 const setItem=Storage.prototype.setItem;
 Storage.prototype.setItem=function(key,value){if(key==='pts-file-cleanup-v1'&&window.privateCleanupFault==='storage')throw new Error('fixture_private_storage_failed');return setItem.call(this,key,value);};
}
async function boundedOriginalLogout(page,action,original){
 const started=Date.now();
 const response=page.waitForResponse(response=>{
  const url=new URL(response.url());if(url.pathname!=='/auth/v1/logout')return false;
  // Same-session SDK refresh may supply a newer original token. Identify its
  // exact provider pair, then require the real provider's successful response.
  try{
   const token=response.request().headers().authorization?.slice(7),claims=JSON.parse(Buffer.from(token.split('.')[1],'base64url').toString());
   const expected=original.sessionId||JSON.parse(Buffer.from(original.token.split('.')[1],'base64url').toString()).session_id;
   return claims.sub===original.id&&claims.session_id===expected;
  }catch{return false;}
 },{timeout:20000});
 await action();const actual=await response;assert([200,204].includes(actual.status()),'private_fault_actual_provider_logout_failed');
 assert(Date.now()-started<20000,'private_fault_provider_attempt_exceeded_bound');return actual.status();
}
async function privateFaultSharedTabs(browser){
 const context=await browser.newContext(),page=await context.newPage();
 let phase='ordinary-tab-login';
 try{
 // Initialize the ordinary private-fault tab first. Its legitimate initial SDK
 // refresh must finish before the observed App's preparation is selected; later
 // notifications to the observed App are still held through physical logout.
 const other=await context.newPage();await other.addInitScript(installPrivateFault,'absent');await login(other,0);await other.getByText(/poems and excerpts shown/).waitFor();assert(await noCleanupCredentials(other));
 await page.goto(config.frontend+'/cleanup-probe.html');
 const original=await page.evaluate(()=>{const sdk=JSON.parse(localStorage.getItem('pts-auth'));return {id:sdk.user.id,token:sdk.access_token};});
 const session={account:original.id,sessionId:JSON.parse(Buffer.from(original.token.split('.')[1],'base64url').toString()).session_id};
 fs.writeFileSync(config.gate_control+'/prepare-all-pair-armed',JSON.stringify({account_id:session.account,session_id:session.sessionId}),{mode:0o600,flag:'wx'});
 await page.addInitScript(installAuthNotificationHold,true);
 let receipted;const late=page.waitForResponse(response=>response.url()===config.files+'/api/file-session/prepare'&&response.headers()['x-fixture-held-preparation']==='verified-owner-pair-all').then(async response=>{await response.finished();const body=await response.json();const authorization=(await response.request().allHeaders()).authorization;assert(typeof authorization==='string'&&authorization.startsWith('Bearer '),'held_original_bearer_missing');receipted={id:body.account_id,sessionId:body.session_id,token:authorization.slice(7)};return {status:response.status(),same_account:body.account_id===session.account,same_session:body.session_id===session.sessionId};}).catch(error=>({error:error.name}));
 phase='app-entry';await page.goto(config.frontend,{waitUntil:'domcontentloaded'});
 const deadline=Date.now()+15000;while(!fs.existsSync(config.gate_control+'/prepare-held')){assert(Date.now()<deadline,'private_fault_other_tab_preparation_not_held');await pause(25);}
 const held=JSON.parse(fs.readFileSync(config.gate_control+'/prepare-held','utf8'));assert.equal(held.actual_upstream_status,200);assert(held.account_matches_expected&&held.session_matches_expected);
 phase='other-no-custody';assert(await noCleanupCredentials(other));
 // Hold the actual final write after its owner200 has returned. The shared SDK
 // can be physically cleared while this private lock remains queued, without
 // relying on delivered auth notifications or changing private marker state.
 phase='acquire-final-lock';await page.evaluate(()=>{window.finalLockHeld=false;void navigator.locks.request('pts-file-cleanup-v1',async()=>{window.finalLockHeld=true;await new Promise(done=>window.releaseFinalLock=done);});});
 await page.waitForFunction(()=>window.finalLockHeld===true);
 phase='release-owner-response';fs.writeFileSync(config.gate_control+'/prepare-release','release',{mode:0o600,flag:'wx'});
 const received=await late;assert.equal(received.status,200);assert(received.same_account&&received.same_session);
 await page.waitForFunction(async()=>{const locks=await navigator.locks.query();return locks.pending.some(lock=>lock.name==='pts-file-cleanup-v1');});
 phase='ordinary-provider-logout';const status=await boundedOriginalLogout(other,()=>other.getByRole('button',{name:'Sign out',exact:true}).click(),original);await signedOut(other);
 phase='exact-original-absence';const absent=await clearProof(other,receipted.token);assert.equal(absent.status,200);assert.equal(absent.body.account_id,session.account);assert.equal(absent.body.session_id,session.sessionId);assert.equal(absent.body.provider_session,'absent');
 assert(await page.evaluate(()=>localStorage.getItem('pts-auth')===null),'cross_tab_sdk_storage_not_physically_cleared');
 assert(await page.evaluate(async()=>{const locks=await navigator.locks.query();return locks.pending.some(lock=>lock.name==='pts-file-cleanup-v1');}),'private_final_lock_expired_before_original_absence_proof');
 phase='release-final-lock';await page.evaluate(()=>window.releaseFinalLock());await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,0)));assert(await clearedCustodySettled(page),'private_fault_late_preparation_recreated_credentials_before_notifications');
 await page.waitForFunction(()=>window.heldAuthNotifications.length>0);
 await page.evaluate(()=>{window.holdAuthNotifications=false;for(const deliver of window.heldAuthNotifications)deliver();window.heldAuthNotifications=[];});await page.getByRole('heading',{name:'Sign in to read',exact:true}).waitFor();
 const denied=await page.evaluate(async({files,token})=>(await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}})).status,{files:config.files,token:original.token});assert.equal(denied,401);
 fs.writeFileSync(config.gate_control+'/file-origin-unavailable','fixture-only later ordinary entry',{mode:0o600,flag:'wx'});
 try{await login(page,1);await page.getByText(/poems and excerpts shown/).waitFor();assert.equal(await page.getByRole('alert').count(),0);assert(await noCleanupCredentials(page));}finally{fs.unlinkSync(config.gate_control+'/file-origin-unavailable');}
 await actualOpen(page,context);const finalOriginal=await record(page);operationObservations(page,'private-tabs-final-authorized-logout');phase='later-signout';
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await page.waitForFunction(()=>document.body.textContent.includes('Sign in to read')||document.body.textContent.includes('We could not sign you out. Please try again.'));
 let ordinarySdkRetry=false;
 if(await page.getByRole('alert').filter({hasText:'We could not sign you out. Please try again.'}).count()){
  // The existing supported SDK failure remains visible. Neither SDK-null nor a
  // generic denial establishes original revocation; require fresh exact proof
  // and strict credential absence before one actual bounded recovery attempt.
  const proof=await clearProof(page,finalOriginal.token);
  assert.equal(proof.status,200);assert.equal(proof.body.account_id,finalOriginal.id);assert.equal(proof.body.session_id,finalOriginal.sessionId);assert.equal(proof.body.provider_session,'absent');
  assert(await noCleanupCredentials(page));assert(await page.evaluate(()=>localStorage.getItem('pts-auth')===null));
  await page.getByRole('button',{name:'Sign out',exact:true}).click();ordinarySdkRetry=true;
 }
 await signedOut(page);assert.equal(await page.getByRole('alert').count(),0);
 checkpoint({case:'two-real-tabs-private-lock-failure-ordinary-logout-supersedes-held-final-write',actual_provider_logout_status:status,exact_original_absence_before_release:true,actual_owner_preparation_status:received.status,physical_sdk_storage_cleared:true,auth_notifications_held_until_no_credentials:true,final_write_queued_across_physical_sdk_clear:true,revoked_setup_denied:denied,later_ordinary_entry_during_file_outage:true,later_actual_Open_and_logout:true,retry_observed:ordinarySdkRetry});
 phase='complete';await context.close();for(const name of ['prepare-all-pair-armed','prepare-held','prepare-release','prepare-released'])fs.unlinkSync(config.gate_control+'/'+name);
 }catch(error){
  await stateObservation(page,'private-tabs-primary-failure').catch(()=>{});
  observe({phase:'private-tabs-primary-failure',step:phase,gate:Object.fromEntries(['prepare-all-pair-armed','prepare-held','prepare-release','prepare-released'].map(name=>[name,fs.existsSync(config.gate_control+'/'+name)])),page_closed:page.isClosed()});
  throw error;
 }

}

async function custodyDuringOrdinaryLogout(browser){
 const context=await browser.newContext(),departing=await context.newPage();operationObservations(departing,'ordinary-custody-departing');await departing.addInitScript(installPrivateFault,'absent');await login(departing,0);
 const reader=await context.newPage();operationObservations(reader,'ordinary-custody-reader');await reader.addInitScript(installPrivateFault,'storage');await reader.goto(config.frontend);await reader.getByText(/poems and excerpts shown/).waitFor();assert(await noCleanupCredentials(reader));
 const original=await reader.evaluate(()=>{const session=JSON.parse(localStorage.getItem('pts-auth'));return {id:session.user.id,token:session.access_token};});
 let release,held=false;const gate=new Promise(done=>release=done);
 // Hold the genuine logout request before forwarding it. No successful provider
 // decision is fabricated, and the existing other App can still use its current
 // authority to establish native custody while ordinary logout is in flight.
 await departing.route('**/auth/v1/logout*',async route=>{held=true;await gate;await route.continue();});
 await reader.evaluate(()=>{window.privateCleanupFault=null;});
 const logout=boundedOriginalLogout(departing,()=>departing.getByRole('button',{name:'Sign out',exact:true}).click(),original).catch(error=>({error:error.name}));
 const deadline=Date.now()+15000;while(!held){if(Date.now()>=deadline){await stateObservation(departing,'ordinary-provider-not-held');assert.fail('ordinary_actual_provider_logout_request_not_held');}await pause(25);}
 const opened=await actualOpen(reader,context),native=await record(reader);
 release();const status=await logout;assert.equal(status,204);
 await departing.getByRole('alert').filter({hasText:failText}).waitFor();
 assert(await departing.evaluate(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token)),'ordinary_logout_erased_new_native_custody');
 assert.deepEqual(await statuses(reader,opened),[401,401]);
 const absent=await clearProof(departing,native.token);assert.equal(absent.status,200);assert.equal(absent.body.account_id,native.id);assert.equal(absent.body.session_id,native.sessionId);assert.equal(absent.body.provider_session,'absent');
 await departing.evaluate(()=>{window.privateCleanupFault=null;});await departing.getByRole('button',{name:'Retry Sign out',exact:true}).click();await signedOut(departing);
 checkpoint({case:'new-native-custody-during-ordinary-provider-logout',actual_provider_logout_status:status,actual_other_App_Open_before_provider_revoke:true,new_native_custody_retained:true,incomplete_visible:true,old_native_context_denied:true,exact_original_absence_verified:true,retry_file_cleanup_and_custody_clear_completed:true});await context.close();
}

async function laterSessionDuringOriginalCleanup(browser){
 for(const sameAccount of [false,true]){
  const context=await browser.newContext(),departing=await context.newPage();operationObservations(context,'later-session-current-native');
  await context.addInitScript(()=>{const open=window.open;window.actualNativeOpenCalls=0;window.open=function(...args){window.actualNativeOpenCalls++;return Reflect.apply(open,this,args);};});
  let step='login',heldProof;
  const release=()=>{const path=config.gate_control+'/clear-release';if(!fs.existsSync(path))fs.writeFileSync(path,'release',{mode:0o600,flag:'wx'});};
  try{
   await login(departing,0);const original=await record(departing),oldUrl=await actualOpen(departing,context);
   fs.writeFileSync(config.gate_control+'/clear-pair-armed',JSON.stringify({account_id:original.id,session_id:original.sessionId}),{mode:0o600,flag:'wx'});
   const heldArrival=departing.waitForResponse(response=>new URL(response.url()).pathname==='/api/file-session/clear'&&response.headers()['x-fixture-held-clear']==='verified-owner-pair').then(response=>({response}),()=>({error_id:'fixture_held_browser_response_unavailable'}));
   step='hold-actual-original-cleanup';
   const originalLogout=boundedOriginalLogout(departing,()=>departing.getByRole('button',{name:'Sign out',exact:true}).click(),original).catch(error=>({error:error.name}));
   const deadline=Date.now()+15000;while(!fs.existsSync(config.gate_control+'/clear-held')){assert(Date.now()<deadline,'actual_original_cleanup_response_not_held');await pause(25);}
   heldProof=JSON.parse(fs.readFileSync(config.gate_control+'/clear-held','utf8'));assert.equal(heldProof.actual_upstream_status,200);assert(heldProof.account_matches_expected&&heldProof.session_matches_expected);
   const originalStatus=await originalLogout;assert.equal(originalStatus,204);
   const other=await context.newPage();step='other-tab-completes-original';await other.goto(config.frontend);
   await other.getByRole('button',{name:'Retry Sign out',exact:true}).click();await signedOut(other);
   const absent=await clearProof(other,original.token);assert.equal(absent.status,200);assert.equal(absent.body.account_id,original.id);assert.equal(absent.body.session_id,original.sessionId);assert.equal(absent.body.provider_session,'absent');
   step='other-tab-independent-login-and-Open';await login(other,sameAccount?0:1);await actualOpen(other,context);const replacement=await record(other);
   assert.equal(replacement.id===original.id,sameAccount);assert.notEqual(replacement.sessionId,original.sessionId);
   let wrongLogout=false;
   const observeLogout=request=>{
    if(new URL(request.url()).pathname!=='/auth/v1/logout')return;
    try{const claims=JSON.parse(Buffer.from(request.headers().authorization.slice(7).split('.')[1],'base64url').toString());if(claims.sub===replacement.id&&claims.session_id===replacement.sessionId)wrongLogout=true;}catch{/* Unknown request cannot supply the proof below. */}
   };
   context.on('request',observeLogout);step='release-old-cleanup';release();
   const received=await heldArrival;assert(received.response,'fixture_held_browser_response_unavailable');const arrived=received.response;assert.equal(arrived.status(),200);assert((await arrived.finished())===null,'fixture_held_browser_response_not_finished');assert(fs.existsSync(config.gate_control+'/clear-released'));
   await replacementRestored(departing,replacement.id,replacement.sessionId);
   const current=await record(other);assert.equal(current.id,replacement.id);assert.equal(current.sessionId,replacement.sessionId);assert(!current.pending&&!current.replacement,'later native custody became pending old recovery');
   assert(!wrongLogout,'stale_logout_requested_replacement_revocation');
   step='later-authorized-Open';await actualOpen(departing,context);assert.deepEqual(await statuses(departing,oldUrl),[404,404]);
   const stillAbsent=await clearProof(departing,original.token);assert.equal(stillAbsent.body.provider_session,'absent');
   context.off('request',observeLogout);
   checkpoint({case:'delayed-original-native-cleanup-versus-later-'+(sameAccount?'same-account':'different-account')+'-independent-session',actual_original_cleanup_status:heldProof.actual_upstream_status,held_response_exact_original:heldProof.account_matches_expected&&heldProof.session_matches_expected,actual_held_browser_response_arrived:true,actual_original_provider_logout_status:originalStatus,other_real_App_completed_original_cleanup:true,exact_original_absence_before_release:true,independent_provider_session:true,later_native_custody_retained:true,no_later_provider_logout_request:true,later_authorized_actual_Open:true,old_context_denied:true});
   step='later-logout';operationObservations(departing,'later-session-final-departing');operationObservations(other,'later-session-final-other');await departing.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(departing);
  }catch(error){await stateObservation(departing,'later-session-primary-failure').catch(()=>{});observe({phase:'later-session-primary-failure',step,same_account:sameAccount});throw error;}
  finally{release();await context.close();for(const name of ['clear-pair-armed','clear-held','clear-release','clear-released']){const path=config.gate_control+'/'+name;if(fs.existsSync(path))fs.unlinkSync(path);}}
 }
}

async function privateFaultJourneys(browser){
 const oracles=[];
 for(const fault of ['absent','timeout','storage']){
  let context=await browser.newContext();await context.addInitScript(installPrivateFault,fault);let page=await context.newPage();await login(page,0);
  await page.getByText(/poems and excerpts shown/).waitFor();
  assert(await noCleanupCredentials(page),'ordinary_fault_created_cleanup_credentials');
  const current=await page.evaluate(()=>{const session=JSON.parse(localStorage.getItem('pts-auth'));return {id:session.user.id,token:session.access_token};});
  const claims=JSON.parse(Buffer.from(current.token.split('.')[1],'base64url').toString());assert.equal(claims.sub,current.id);
  const status=await boundedOriginalLogout(page,()=>page.getByRole('button',{name:'Sign out',exact:true}).click(),current);
  await signedOut(page);assert.equal(await page.getByRole('alert').count(),0);
  assert(await page.evaluate(()=>localStorage.getItem('pts-auth')===null),'ordinary_fault_retained_sdk_custody');
  const denied=await page.evaluate(async({files,token})=>(await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}})).status,{files:config.files,token:current.token});assert.equal(denied,401);
  oracles.push({case:'ordinary-'+fault,account_id:claims.sub,session_id:claims.session_id});
  checkpoint({case:'ordinary-no-native-custody-private-'+fault,actual_provider_logout_status:status,bounded_provider_attempt:true,no_cleanup_credentials:true,old_setup_denied:denied,exact_absence_oracle:'post-browser fresh-owner query'});await context.close();

  context=await browser.newContext();page=await context.newPage();operationObservations(page,'receipted-private-'+fault);await login(page,0);const original=await record(page),opened=await actualOpen(page,context);
  await page.evaluate(installPrivateFault,fault);
  const nativeStatus=await boundedOriginalLogout(page,()=>page.getByRole('button',{name:'Sign out',exact:true}).click(),original);
  await page.getByRole('alert').filter({hasText:failText}).waitFor();
  assert(await page.evaluate(()=>Boolean(JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null')?.token)),'failed_mutation_lost_original_custody');
  const absent=await clearProof(page,original.token);assert.equal(absent.status,200);assert.equal(absent.body.account_id,original.id);assert.equal(absent.body.session_id,original.sessionId);assert.equal(absent.body.provider_session,'absent');
  assert.deepEqual(await statuses(page,opened),[401,401]);
  await page.evaluate(()=>{window.privateCleanupFault=null;});await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();await signedOut(page);
  checkpoint({case:'receipted-native-private-'+fault,actual_provider_logout_status:nativeStatus,incomplete_visible:true,original_absence_verified:true,old_native_context_denied:true,retry_after_private_recovery_completed:true});await context.close();
 }
 // The first failed replacement write occurs on automatic same-account switch.
 // Retry must persist its verified replacement before the sole SDK can rotate it.
 const context=await browser.newContext();let page=await context.newPage();await login(page,0);const original=await record(page),opened=await actualOpen(page,context);
 const next=await independentLogin(page,0);await context.addInitScript(installPrivateFault,'storage');
 const status=await boundedOriginalLogout(page,()=>page.reload(),original);
 await page.getByRole('alert').filter({hasText:'We could not finish switching accounts. Please retry Sign out.'}).waitFor();
 const absent=await clearProof(page,original.token);assert.equal(absent.status,200);assert.equal(absent.body.session_id,original.sessionId);assert.equal(absent.body.provider_session,'absent');
 await page.evaluate(()=>{window.privateCleanupFault=null;});await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();await replacementRestored(page,next.account,next.sessionId);
 await actualOpen(page,context);assert.deepEqual(await statuses(page,opened),[404,404]);
 checkpoint({case:'automatic-same-account-replacement-private-first-write-failure',actual_original_provider_logout_status:status,original_absence_verified:true,replacement_preserved:true,retry_and_actual_Open:true,old_native_context_denied:true});
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);await context.close();
 await privateFaultSharedTabs(browser);
 await custodyDuringOrdinaryLogout(browser);
 await laterSessionDuringOriginalCleanup(browser);
 fs.writeFileSync(config.output+'/private-fault-session-oracles-private.json',JSON.stringify(oracles)+'\n',{mode:0o600,flag:'wx'});
}

async function run(){
 const browser=await chromium.launch({headless:false,args:['--no-proxy-server','--host-resolver-rules=MAP *.pts.fixture.test 127.0.0.1, MAP pts.fixture.test 127.0.0.1','--ignore-certificate-errors-spki-list='+config.spki]});
 try{
  if(process.env.PTS_FIXTURE_CLEANUP_TABS_ONLY==='1'){await sharedTabCleanup(browser);}else if(process.env.PTS_FIXTURE_CLEANUP_PRIVATE_ONLY==='1'){await privateFaultJourneys(browser);}else{
  await privateFaultJourneys(browser);
  // File cleanup fails first; provider revocation must still be attempted.
  let context=await browser.newContext();let page=await context.newPage();await login(page,0);let original=await record(page);let opened=await ownContext(page);
  fs.writeFileSync(config.gate_control+'/clear-unavailable','fixture-only outage',{mode:0o600,flag:'wx'});
  try{
   await cleanupFailure(page);
   const revoked=await page.evaluate(async({files,token})=>(await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}})).status,{files:config.files,token:original.token});assert.equal(revoked,401);
   await page.reload();await page.getByRole('button',{name:'Sign out',exact:true}).waitFor();
   assert(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-file-cleanup-v1')).pending===true));
  }finally{fs.unlinkSync(config.gate_control+'/clear-unavailable');}
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);assert.deepEqual(await statuses(page,opened.url),[401,401]);
  checkpoint({case:'file-origin-outage-provider-local-revocation-still-attempted',revoked_setup_status:401,pending_survived_reload:true,repeated_signout_recovered:true});await context.close();

  // Context cleanup succeeds first; actual provider outage leaves honest pending.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);opened=await ownContext(page);
  execFileSync('docker',['pause',config.provider_container],{stdio:'ignore'});
  try{await cleanupFailure(page);}
  finally{execFileSync('docker',['unpause',config.provider_container],{stdio:'ignore'});}
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);
  checkpoint({case:'genuine-provider-outage-after-successful-file-cleanup',incomplete_visible:true,repeated_signout_recovered:true});await context.close();

  // External provider-local revocation, while the original app remains signed in.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);await ownContext(page);
  const revoked=await page.evaluate(async token=>(await fetch('/auth/v1/logout?scope=local',{method:'POST',headers:{Authorization:'Bearer '+token,apikey:'synthetic-public-key'}})).status,original.token);assert([200,204].includes(revoked));
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);
  checkpoint({case:'externally-revoked-original',ordinary_authority_not_restored:true,cleanup_recovered:true});await context.close();

  // Stop the app's sole refresh owner naturally by closing its tab. A blank
  // same-origin fixture page has no auth client or refresh loop.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);opened=await ownContext(page);
  const claims=JSON.parse(Buffer.from(original.token.split('.')[1],'base64url').toString());await page.close();
  page=await context.newPage();await page.goto(config.frontend+'/cleanup-probe.html');
  while(Date.now()<=claims.exp*1000+1100)await pause(Math.min(1000,claims.exp*1000+1100-Date.now()+10));
  const live=await clearProof(page,original.token);assert.equal(live.status,200);assert.equal(live.body.provider_session,'present');assert.equal(live.body.session_id,original.sessionId);
  checkpoint({case:'expired-original-before-cleanup',credential_expired:true,exact_original_provider_session_present:true,cleanup_status:live.status});
  // A genuine different-account provider Session becomes auth's current session
  // before the app reopens; cleanup must explicitly refresh the old session.
  await page.evaluate(async subject=>{
   const response=await fetch('/auth/v1/token?grant_type=password',{method:'POST',headers:{'Content-Type':'application/json',apikey:'synthetic-public-key'},body:JSON.stringify({email:subject.email,password:subject.password})});
   if(response.status!==200)throw new Error('replacement_provider_signin_failed');const session=await response.json();session.expires_at=Math.floor(Date.now()/1000)+session.expires_in;localStorage.setItem('pts-auth',JSON.stringify(session));
  },config.subjects[1]);
  const observed=[];page.on('response',response=>{
   const url=new URL(response.url());
   if(url.pathname==='/auth/v1/token'&&url.searchParams.get('grant_type')==='refresh_token'){observed.push(response);observe({phase:'expired-original-switch',operation:'provider-refresh',status:response.status()});}
   if(url.pathname==='/auth/v1/logout')observe({phase:'expired-original-switch',operation:'provider-local-logout',status:response.status()});
  });
  fs.writeFileSync(config.gate_control+'/fail-logout-after-refresh','fixture-only post-refresh provider outage',{mode:0o600,flag:'wx'});
  let rotated;
  try{
   await page.goto(config.frontend);
   await page.getByRole('alert').filter({hasText:'We could not finish switching accounts. Please retry Sign out.'}).waitFor({timeout:45000});
   rotated=await record(page);
   assert(rotated.token===original.token,'original cleanup proof was overwritten');
   assert(rotated.refreshToken!==original.refreshToken,'rotated refresh credential was not retained');
   assert(typeof rotated.revocationToken==='string'&&rotated.revocationToken!==original.token,'verified revocation credential was not retained');
   assert(rotated.pending===true,'failed post-refresh revoke lost pending state');
  }finally{fs.unlinkSync(config.gate_control+'/fail-logout-after-refresh');}
  let originalRefresh=false;
  for(const response of observed){const request=response.request();const body=request.postDataJSON();if(body.refresh_token===original.refreshToken){const result=await response.json();const verified=JSON.parse(Buffer.from(result.access_token.split('.')[1],'base64url').toString());originalRefresh=response.status()===200&&result.user.id===original.id&&verified.session_id===original.sessionId;}}
  assert(originalRefresh,'existing auth owner did not refresh the explicit original session');
  // Close the auth owner again, then exceed the renewed credential lifetime and
  // provider refresh-reuse grace before recovery. No second refresh loop exists.
  const rotatedExpiry=JSON.parse(Buffer.from(rotated.revocationToken.split('.')[1],'base64url').toString()).exp;
  await page.close();page=await context.newPage();await page.goto(config.frontend+'/cleanup-probe.html');
  const until=Math.max(rotatedExpiry*1000+1100,Date.now()+31000);
  while(Date.now()<=until)await pause(Math.min(1000,until-Date.now()+10));
  const recoveryRefresh=[];
  const freshOriginalCredentials=new Set();let latestProviderRefresh=rotated.refreshToken;
  operationObservations(page,'second-expiry-recovery');
  page.on('request',request=>{
   const url=new URL(request.url());if(url.pathname!=='/auth/v1/token'||url.searchParams.get('grant_type')!=='refresh_token')return;
   const credential=request.postDataJSON()?.refresh_token;recoveryRefresh.push(credential);
   observe({phase:'second-expiry-recovery',operation:'provider-refresh-request',matches_retained_rotation:credential===rotated.refreshToken,matches_latest_observed_provider_rotation:credential===latestProviderRefresh});
  });
  page.on('response',async response=>{
   const url=new URL(response.url());if(url.pathname!=='/auth/v1/token'||url.searchParams.get('grant_type')!=='refresh_token')return;
   try{
    const result=await response.json();
    if(response.status()!==200){observe({phase:'second-expiry-recovery',operation:'provider-refresh-evidence',status:response.status(),provider_error_id:typeof result.error_code==='string'&&/^[a-z_]{1,64}$/.test(result.error_code)?result.error_code:null});return;}
    const claims=JSON.parse(Buffer.from(result.access_token.split('.')[1],'base64url').toString());
    const account_matches_original=result.user.id===original.id,session_matches_original=claims.session_id===original.sessionId,credential_fresh=claims.exp*1000>Date.now()+1000;
    observe({phase:'second-expiry-recovery',operation:'provider-refresh-evidence',status:200,account_matches_original,session_matches_original,credential_fresh});
    if(account_matches_original&&session_matches_original&&credential_fresh){freshOriginalCredentials.add(result.access_token);latestProviderRefresh=result.refresh_token;}
   }catch{/* Failed evidence is never a successful provider decision. */}
  });
  await page.goto(config.frontend);await page.getByRole('button',{name:'Sign out',exact:true}).waitFor();
  await page.waitForFunction(()=>{
   const saved=JSON.parse(localStorage.getItem('pts-file-cleanup-v1')||'null'),session=JSON.parse(localStorage.getItem('pts-auth')||'null');
   if(!saved?.pending||saved.replacement?.token!==session?.access_token||saved.replacement?.refreshToken!==session?.refresh_token)return false;
   try{const claims=JSON.parse(atob(session.access_token.split('.')[1].replaceAll('-','+').replaceAll('_','/')));return claims.sub===saved.replacement.id&&claims.session_id===saved.replacement.sessionId&&claims.exp*1000>Date.now()+1000;}catch{return false;}
  });
  const recovered=await record(page);assert(recovered.replacement&&recovered.replacement.id===config.subjects[1].account,'replacement session was lost during failed original cleanup/reload');
  await stateObservation(page,'second-expiry-before-signout');
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await replacementRestored(page,recovered.replacement.id,recovered.replacement.sessionId);
  assert(recoveryRefresh.includes(rotated.refreshToken),'retry failed to use latest retained original-session refresh');
  assert(freshOriginalCredentials.size>0,'retry recovery credential lacks a fresh successful original-session provider response');
  const absent=await clearProof(page,original.token);assert.equal(absent.status,200);assert.equal(absent.body.provider_session,'absent');
  const current=await record(page);assert.equal(current.id,config.subjects[1].account);assert.notEqual(current.sessionId,original.sessionId);
  const newFile=await ownContext(page);assert.deepEqual(await statuses(page,opened.url),[404,404]);assert.deepEqual(await statuses(page,newFile.url),[206,200]);
  // Loading the current SDK session during original cleanup may itself rotate
  // the foreign replacement. Exceed provider reuse grace, then ask the same SDK
  // owner to refresh and reload it; restoring an obsolete pair must fail here.
  await pause(11000);
  const replacementRefresh=await page.waitForResponse(async response=>{
   const url=new URL(response.url());
   if(url.origin!==config.frontend||url.pathname!=='/auth/v1/token'||url.searchParams.get('grant_type')!=='refresh_token'||response.status()!==200)return false;
   const session=await response.json();
   if(typeof session.access_token!=='string'||session.access_token===current.token)return false;
   const claims=JSON.parse(Buffer.from(session.access_token.split('.')[1],'base64url').toString());
   return session.user.id===current.id&&claims.sub===current.id&&claims.session_id===current.sessionId;
  },{timeout:45000});
  assert.equal(replacementRefresh.status(),200,'restored replacement could not refresh after provider reuse grace');
  await replacementRestored(page,current.id,current.sessionId);await page.reload();await replacementRestored(page,current.id,current.sessionId);await actualOpen(page,context);
  checkpoint({case:'expired-live-original-then-different-account-session-on-reload',original_provider_session_was_present:true,explicit_original_refresh_owner:true,exact_original_session_verified_before_revoke:true,rotated_recovery_durable_before_failed_revoke:true,closed_app_wait_exceeded_renewed_credential_and_reuse_grace:true,reload_used_latest_original_refresh:true,original_absence_verified:true,replacement_context_only_after_cleanup:true,replacement_refresh_after_reuse_grace:true,replacement_reload_and_actual_Open:true});
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);await context.close();

  await sharedTabCleanup(browser);

  // Same-account independent provider session. Hold a real already-verified old
  // preparation across replacement; its late200 creates no new file authority.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);opened=await ownContext(page);
  const probe=await context.newPage();await probe.goto(config.frontend+'/cleanup-probe.html');
  fs.writeFileSync(config.gate_control+'/prepare-armed',createHash('sha256').update('Bearer '+original.token).digest('hex'),{mode:0o600,flag:'wx'});
  await probe.evaluate(({files,token})=>{globalThis.latePreparation=fetch(files+'/api/file-session/prepare',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}}).then(response=>response.status);},{files:config.files,token:original.token});
  let deadline=Date.now()+15000;while(!fs.existsSync(config.gate_control+'/prepare-held')){assert(Date.now()<deadline,'old real preparation was not held');await pause(50);}
  const independent=await independentLogin(page,0);assert.equal(independent.account,original.id);assert.notEqual(independent.sessionId,original.sessionId);
  await page.reload();await replacementRestored(page,independent.account,independent.sessionId);
  fs.writeFileSync(config.gate_control+'/prepare-release','release',{mode:0o600,flag:'wx'});
  assert.equal(await probe.evaluate(()=>globalThis.latePreparation),200);await probe.close();
  const originalAbsent=await clearProof(page,original.token);assert.equal(originalAbsent.body.provider_session,'absent');
  const sameFirst=await actualOpen(page,context),sameSecond=await actualOpen(page,context);assert.notEqual(sameFirst,sameSecond);
  const sameCurrent=await record(page);assert.equal(sameCurrent.sessionId,independent.sessionId);
  assert.deepEqual(await statuses(page,opened.url),[404,404]);
  checkpoint({case:'same-account-independent-provider-session-and-delayed-old-preparation',same_account:true,provider_session_replaced:true,late_original_preparation_status:200,original_absence_verified:true,repeated_actual_Open:true,old_context_denied:true});
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);await context.close();

  // A failed same-account transition preserves BOTH original recovery and the
  // independent replacement across reload, then resumes the replacement on Retry.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);await ownContext(page);
  const retryReplacement=await independentLogin(page,0);assert.notEqual(retryReplacement.sessionId,original.sessionId);
  fs.writeFileSync(config.gate_control+'/clear-unavailable','fixture-only outage',{mode:0o600,flag:'wx'});
  try{
   await page.reload();await page.getByRole('alert').filter({hasText:'We could not finish switching accounts. Please retry Sign out.'}).waitFor({timeout:45000});
   const pending=await record(page);assert(pending.pending&&pending.replacement?.sessionId===retryReplacement.sessionId,'replacement recovery custody missing');
   await page.reload();await page.getByRole('alert').filter({hasText:failText}).waitFor();
  }finally{fs.unlinkSync(config.gate_control+'/clear-unavailable');}
  await page.getByRole('button',{name:'Retry Sign out',exact:true}).click();await replacementRestored(page,original.id,retryReplacement.sessionId);
  assert.equal((await clearProof(page,original.token)).body.provider_session,'absent');
  await actualOpen(page,context);await actualOpen(page,context);
  assert.equal((await record(page)).sessionId,retryReplacement.sessionId);
  checkpoint({case:'same-account-replacement-cleanup-outage-reload-retry',replacement_preserved:true,original_absence_verified:true,repeated_actual_Open:true});
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);await context.close();

  // Genuine provider recovery verification yields an independent same-account
  // session, consumed by the existing SDK's standard recovery callback.
  context=await browser.newContext();page=await context.newPage();await login(page,0);original=await record(page);await ownContext(page);
  assert(Array.isArray(config.recovery_command));execFileSync(config.recovery_command[0],config.recovery_command.slice(1),{stdio:'ignore'});
  const recovery=JSON.parse(fs.readFileSync(config.output+'/recovery-session-private.json','utf8'));
  const recoveryClaims=JSON.parse(Buffer.from(recovery.access_token.split('.')[1],'base64url').toString());
  assert.equal(recoveryClaims.sub,original.id);assert.notEqual(recoveryClaims.session_id,original.sessionId);
  await page.evaluate(({session,actor})=>{
   localStorage.setItem('pts-password-return',JSON.stringify({actor,query:'view=sources&availability=checked&search=synthetic',expires:Date.now()+3600000}));
   const fragment=new URLSearchParams({access_token:session.access_token,refresh_token:session.refresh_token,expires_in:String(session.expires_in),token_type:'bearer',type:'recovery'});
   history.replaceState(null,'',location.pathname+'#'+fragment);location.reload();
  },{session:recovery,actor:original.id});
  await page.getByRole('heading',{name:'Choose a new password',exact:true}).waitFor();
  assert(new URL(page.url()).searchParams.get('view')==='sources'&&new URL(page.url()).searchParams.get('search')==='synthetic','same-account recovery return context was lost');
  assert.equal((await clearProof(page,original.token)).body.provider_session,'absent');
  const password=config.subjects[0].password+'-replacement';
  await page.getByLabel('New password',{exact:true}).fill(password);await page.getByLabel('Confirm password',{exact:true}).fill(password);await page.getByRole('button',{name:'Save password',exact:true}).click();
  await page.getByRole('button',{name:'Sources',exact:true}).waitFor();await actualOpen(page,context);await actualOpen(page,context);
  assert.equal((await record(page)).sessionId,recoveryClaims.session_id);
  const restoredPassword=await page.evaluate(async password=>{const session=JSON.parse(localStorage.getItem('pts-auth'));return (await fetch('/auth/v1/user',{method:'PUT',headers:{Authorization:'Bearer '+session.access_token,apikey:'synthetic-public-key','Content-Type':'application/json'},body:JSON.stringify({password})})).status;},config.subjects[0].password);
  assert.equal(restoredPassword,200);
  checkpoint({case:'genuine-same-account-recovery-session-return-and-repeated-Open',provider_recovery_verified:true,independent_provider_session:true,original_absence_verified:true,return_context_preserved:true,actual_password_save:true,repeated_actual_Open:true});
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);await context.close();

  // A genuine user without app grants or an actor cannot establish file auth;
  // its ordinary existing auth logout remains usable, without actor creation.
  const unmapped=config.subjects.find(value=>value.unmapped);assert(unmapped);
  context=await browser.newContext();page=await context.newPage();await page.goto(config.frontend);await page.getByLabel('Email',{exact:true}).fill(unmapped.email);await page.getByLabel('Password',{exact:true}).fill(unmapped.password);await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('button',{name:'Sign out',exact:true}).waitFor();
  await page.waitForTimeout(300);assert.equal(await noCleanupCredentials(page),true);
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await signedOut(page);
  checkpoint({case:'no-actor-no-grants-no-native-file-session',ordinary_provider_logout:true,no_receipt_or_actor_created:true});await context.close();
  }
 }finally{await browser.close();}
 fs.writeFileSync(config.output+'/native-cleanup-browser-proof.json',JSON.stringify({checks,excluded:['human devices','hosted origins','resource performance']},null,2)+'\n',{mode:0o600,flag:'wx'});
}
run().catch(error=>{process.stderr.write('native_cleanup_browser_failed: '+(error.stack||error.name)+'\n');process.exitCode=1;});
