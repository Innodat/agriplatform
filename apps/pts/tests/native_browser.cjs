// No response mocks: actual UI, TLS gateway, GoTrue, Identity, Access and Content.
const fs=require('node:fs');const assert=require('node:assert/strict');const crypto=require('node:crypto');
const {chromium}=require('../../../node_modules/@playwright/test');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const checks=[];
const pause=milliseconds=>new Promise(resolve=>setTimeout(resolve,milliseconds));
function observeContext(context){context.on('page',page=>{
 page.__fileRequests=[];
 page.on('response',response=>{if(response.url().startsWith(config.files+'/api/files/'))page.__fileRequests.push({method:response.request().method(),status:response.status()});});
 page.on('requestfailed',request=>{if(request.url().startsWith(config.files+'/api/files/'))page.__fileRequests.push({method:request.method(),failed:true});});
});}
async function nativeViewer(page,screenshot){
 // Chromium's current native PDF viewer lives in an extension frame. Its
 // embed is not part of the top-level document (including under our CSP).
 const deadline=Date.now()+15000;let viewer;
 while(!viewer){
  viewer=page.frames().find(frame=>frame.url().startsWith('chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai/'));
  assert(Date.now()<deadline,'native PDF extension frame did not load');
  if(!viewer)await pause(50);
 }
 try{
  await viewer.locator('pdf-viewer').waitFor({state:'visible'});
  await viewer.locator('viewer-toolbar').waitFor({state:'visible'});
  // The toolbar shell is visible before the native plugin has loaded any PDF.
  // Wait for this fixture's one-page metadata and a native plugin viewport.
  await viewer.waitForFunction(()=>{
   const pdf=document.querySelector('pdf-viewer');
   const toolbar=pdf?.shadowRoot?.querySelector('viewer-toolbar');
   return toolbar?.docLength===1;
  },null,{timeout:15000});
  await viewer.locator('embed[type="application/x-google-chrome-pdf"]').waitFor({state:'visible',timeout:15000});
  // Metadata completion precedes the plugin's next compositor paint. Retain the
  // resulting page screenshot for independent inspection of actual PDF content.
  await page.waitForTimeout(500);
  await page.screenshot({path:screenshot});
 }catch(error){
  const diagnostics=await viewer.evaluate(()=>{
   const values=[];
   function visit(root){for(const element of root.querySelectorAll('*')){
    if(element.localName.startsWith('viewer-')||element.localName==='pdf-viewer')values.push({tag:element.localName,id:element.id,docLength:element.docLength,loading:element.loading});
    if(element.shadowRoot)visit(element.shadowRoot);
   }}visit(document);return values;
  }).catch(()=>[]);
  fs.writeFileSync(screenshot+'.diagnostics.json',JSON.stringify({native_viewer:diagnostics,file_requests:page.__fileRequests||[]},null,2)+'\n',{mode:0o600,flag:'wx'});
  await page.screenshot({path:screenshot+'.failed.png'}).catch(()=>{});throw error;
 }
}
async function login(page,index){
 await page.goto(config.frontend);await page.getByLabel('Email',{exact:true}).fill(config.subjects[index].email);await page.getByLabel('Password',{exact:true}).fill(config.subjects[index].password);await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('button',{name:'Sources',exact:true}).waitFor();
}
async function ownContext(page){return await page.evaluate(async({files,document})=>{
 const token=JSON.parse(localStorage.getItem('pts-auth')).access_token;
 const headers={Authorization:'Bearer '+token};
 const prepared=await fetch(files+'/api/file-session/prepare',{method:'POST',credentials:'include',headers});if(prepared.status!==200)throw new Error('current_cleanup_preparation_failed');
 const setup=await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers});if(setup.status!==200)throw new Error('current_setup_failed');
 const result=await fetch(files+'/api/file-contexts/'+document.id,{method:'POST',credentials:'include',headers});if(result.status!==200)throw new Error('current_context_failed');return {url:(await result.json()).url,token};
},{files:config.files,document:config.document});}
async function statuses(page,url){return await page.evaluate(async url=>{
 const result=[];for(const method of ['GET','HEAD']){const response=await fetch(url,{method,credentials:'include',headers:{Range:'bytes=0-7'}});result.push(response.status);}return result;
},url);}
async function providerRenewal(page,context,initial){
 const claims=token=>JSON.parse(Buffer.from(token.split('.')[1],'base64url').toString());
 const previous=claims(initial.token);
 assert(previous.sub===config.subjects[0].account,'initial renewal account mismatch');
 assert.equal(typeof previous.session_id,'string');assert(previous.session_id.length>0);
 // The real UI's existing Supabase client owns its automatic refresh. Observe
 // that actual provider response; no extra client, injected hook or response mock.
 const observed=new Set(),observations=[];
 const isRefresh=response=>{const url=new URL(response.url());return url.origin===config.frontend&&url.pathname==='/auth/v1/token'&&url.searchParams.get('grant_type')==='refresh_token'&&response.status()===200;};
 const observe=response=>{if(isRefresh(response))observations.push(response.json().then(result=>{assert(typeof result.access_token==='string','provider refresh credential missing');observed.add(result.access_token);}));};
 page.on('response',observe);
 const response=await page.waitForResponse(async response=>{
  const url=new URL(response.url());
  if(url.origin!==config.frontend||url.pathname!=='/auth/v1/token'||url.searchParams.get('grant_type')!=='refresh_token'||response.status()!==200)return false;
  const result=await response.json();
  return typeof result.access_token==='string'&&result.access_token!==initial.token&&claims(result.access_token).exp>previous.exp;
 },{timeout:45000});
 const refreshed=await response.json();const next=claims(refreshed.access_token);
 assert(next.sub===previous.sub,'renewal account changed');assert(next.session_id===previous.session_id,'renewal provider session changed');assert(next.exp>previous.exp,'renewal expiry did not extend');
 await page.waitForFunction(token=>JSON.parse(localStorage.getItem('pts-auth')).access_token===token,refreshed.access_token);
 await page.getByRole('button',{name:'Sources',exact:true}).click();
 const document=page.getByRole('region',{name:config.document.title,exact:true});
 const section=page.locator('details').filter({has:document}).first();
 if(await section.count())await section.locator('summary').first().click();
 const popup=context.waitForEvent('page');
 const fileResponse=context.waitForEvent('response',response=>response.url().startsWith(config.files+'/api/files/')&&response.status()===200);
 const setupResponse=page.waitForResponse(response=>response.url()===config.files+'/api/file-session'&&response.request().method()==='POST');
 await document.getByRole('button',{name:'Open document',exact:true}).click();
 const opened=await fileResponse;const viewer=await popup;
 const setup=await setupResponse;assert.equal(setup.status(),200);
 const authorization=(await setup.request().allHeaders()).authorization;
 assert(typeof authorization==='string'&&authorization.startsWith('Bearer '),'UI setup bearer missing');
 const transported=authorization.slice(7),transportedClaims=claims(transported);
 await Promise.all(observations);
 assert(observed.has(transported),'UI setup credential was not observed from the genuine provider refresh');
 assert(transported!==initial.token,'UI setup reused the initial credential');
 assert(transportedClaims.sub===previous.sub,'UI setup account changed');
 assert(transportedClaims.session_id===previous.session_id,'UI setup provider session changed');
 assert(transportedClaims.exp>previous.exp,'UI setup credential expiry did not extend');
 assert.equal(opened.headers()['content-type'],'application/pdf');
 await nativeViewer(viewer,config.output+'/native-renewed-viewer.png');
 const cookie=(await context.cookies(config.files)).find(cookie=>cookie.name==='__Host-pts-file');
 assert(cookie&&cookie.value===transported,'renewed cookie does not match the actual UI setup credential');
 assert(cookie.expires>previous.exp&&cookie.expires<=transportedClaims.exp,'renewed cookie expiry exceeds its credential or did not extend');
 assert(cookie.httpOnly&&cookie.secure&&cookie.sameSite==='Lax'&&!cookie.domain.startsWith('.'));
 const result=await statuses(page,opened.url());assert.deepEqual(result,[206,200]);
 assert(opened.url()!==initial.url,'renewed Open must create its own bounded context');
 checks.push({genuine_provider_refresh:true,refresh_owner:'existing-UI-Supabase-client',same_account:true,same_provider_session:true,access_credential_changed:true,credential_expiry_extended:true,real_Sources_Open_after_refresh:true,renewed_cookie_matches_actual_UI_setup_credential:true,setup_credential_from_observed_provider_refresh:true,observed_provider_refresh_responses:observed.size,setup_credential_differs_from_first_observed_refresh:transported!==refreshed.access_token,setup_credential_expiry_extension_seconds:transportedClaims.exp-previous.exp,cookie_expiry_relative_to_setup_credential_seconds:cookie.expires-transportedClaims.exp,cookie_expiry_after_previous_and_not_after_renewed_credential:true,host_only_secure_HttpOnly_Lax:true,native_renewed_GET:200,renewed_range_GET:result[0],renewed_HEAD:result[1],new_bounded_context:true});
 page.off('response',observe);await viewer.close();return {url:opened.url(),token:transported};
}
async function sessionRaces(browser){
 const context=await browser.newContext();observeContext(context);const page=await context.newPage();
 try{
  await login(page,0);const initialContext=await ownContext(page);
  const old=await providerRenewal(page,context,initialContext);
  fs.writeFileSync(config.gate_control+'/armed','arm',{mode:0o600,flag:'wx'});
  await page.evaluate(({files,token})=>{globalThis.__lateFileSetup=fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}}).then(response=>response.status);},{files:config.files,token:old.token});
  const gateDeadline=Date.now()+15000;while(!fs.existsSync(config.gate_control+'/held')){assert(Date.now()<gateDeadline,'real setup did not reach response gate');await pause(50);}
  const gate=JSON.parse(fs.readFileSync(config.gate_control+'/held','utf8'));assert(gate.actual_upstream_status===200&&gate.set_cookie_present);
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.getByRole('heading',{name:'Sign in to read',exact:true}).waitFor();
  await page.getByLabel('Email',{exact:true}).fill(config.subjects[1].email);await page.getByLabel('Password',{exact:true}).fill(config.subjects[1].password);await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('button',{name:'Sources',exact:true}).waitFor();
  const current=await ownContext(page);assert.deepEqual(await statuses(page,old.url),[404,404]);
  const newCookie=(await context.cookies(config.files)).find(cookie=>cookie.name==='__Host-pts-file');assert(newCookie.value===current.token,'new account cookie missing before delayed arrival');
  fs.writeFileSync(config.gate_control+'/release','release',{mode:0o600,flag:'wx'});
  assert.equal(await page.evaluate(()=>globalThis.__lateFileSetup),200);
  const lateCookie=(await context.cookies(config.files)).find(cookie=>cookie.name==='__Host-pts-file');assert(lateCookie.value===old.token,'delayed real response did not overwrite cookie');
  assert.deepEqual(await statuses(page,current.url),[401,401]);
  const revokedSetup=await page.evaluate(async({files,token})=>(await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}})).status,{files:config.files,token:old.token});assert.equal(revokedSetup,401);
  const repaired=await ownContext(page);assert.deepEqual(await statuses(page,current.url),[206,200]);assert.deepEqual(await statuses(page,old.url),[404,404]);
  checks.push({real_response_gate:true,provider_local_logout_before_new_login:true,late_cookie_physically_overwrote:true,revoked_cookie_new_context_denied:true,new_cookie_old_context_denied:true,revoked_setup_denied:true,current_cookie_repaired:true});
  const expiry=JSON.parse(Buffer.from(repaired.token.split('.')[1],'base64url').toString()).exp;
  const viewer=await context.newPage();
  const initial=await viewer.goto(repaired.url);assert.equal(initial.status(),200);assert.equal(initial.headers()['content-type'],'application/pdf');assert.match(initial.headers()['content-disposition'],/^inline;/);
  await nativeViewer(viewer,config.output+'/native-expiry-viewer.png');
  await page.close();
  while(Date.now()<expiry*1000+1200)await pause(Math.min(10000,expiry*1000+1200-Date.now()));
  // A real native navigation/range is not blocked by the PDF's restrictive CSP.
  // The resulting typed error document then permits the same-origin HEAD probe.
  await viewer.setExtraHTTPHeaders({Range:'bytes=0-7'});const expiredRead=await viewer.goto(repaired.url);assert.equal(expiredRead.status(),401);assert.match(expiredRead.headers()['content-type'],/application\/json/);
  const expired=await statuses(viewer,repaired.url);assert.deepEqual(expired,[401,401]);
  checks.push({genuine_provider_jwt_expiry_seconds:config.provider_jwt_expiry_seconds,initial_native_navigation:'headed-chromium-native-extension-viewer',app_tab_closed:true,native_viewer_new_GET_HEAD_range_after_expiry_denied:true,no_viewer_refresh_owner:true});
 }finally{await context.close();}
}
async function run(){
 const browser=await chromium.launch({headless:false,args:['--no-proxy-server','--host-resolver-rules=MAP *.pts.fixture.test 127.0.0.1, MAP pts.fixture.test 127.0.0.1','--ignore-certificate-errors-spki-list='+config.spki]});
 try{
  for(const [name,viewport] of [['desktop',{width:1280,height:900}],['mobile',{width:390,height:844}]]){
   const context=await browser.newContext({viewport,acceptDownloads:true});observeContext(context);const page=await context.newPage();
   const errors=[];page.on('pageerror',()=>errors.push('page_error'));
   await page.goto(config.frontend);await page.getByLabel('Email',{exact:true}).fill(config.subjects[0].email);await page.getByLabel('Password',{exact:true}).fill(config.subjects[0].password);await page.getByRole('button',{name:'Sign in',exact:true}).click();
   await page.getByRole('button',{name:'Sources',exact:true}).waitFor();
   await page.getByRole('button',{name:'App launcher',exact:true}).click();await page.getByRole('menuitem',{name:'Open PtS',exact:true}).waitFor();await page.keyboard.press('Escape');
   await page.getByRole('button',{name:'Sources',exact:true}).click();
   const document=page.getByRole('region',{name:config.document.title,exact:true});
   // Source details preserve their normal expansion/navigation behavior.
   const section=page.locator('details').filter({has:document}).first();if(await section.count())await section.locator('summary').first().click();
   await document.getByRole('button',{name:'Open document',exact:true}).waitFor();
   const fileResponse=context.waitForEvent('response',r=>r.url().startsWith(config.files+'/api/files/')&&r.status()===200);
   const popup=context.waitForEvent('page');
   await document.getByRole('button',{name:'Open document',exact:true}).click();const opened=await fileResponse;
   assert.equal(opened.headers()['content-type'],'application/pdf');assert.match(opened.headers()['content-disposition'],/^inline;/);
   const pdf=await popup;await nativeViewer(pdf,config.output+'/native-pdf-'+name+'.png');
   const cookies=await context.cookies(config.files);const cookie=cookies.find(c=>c.name==='__Host-pts-file');assert(cookie&&cookie.httpOnly&&cookie.secure&&cookie.sameSite==='Lax'&&!cookie.domain.startsWith('.'));assert(!await page.evaluate(()=>document.cookie.includes('__Host-pts-file')));
   // Browser download events may belong to the opener or a transient native tab.
   let settle;const downloadPromise=new Promise(resolve=>settle=resolve);
   page.once('download',settle);context.on('page',popup=>popup.once('download',settle));
   await document.getByRole('button',{name:/Download PDF|Download document/}).click();
   const received=await Promise.race([downloadPromise,new Promise((_,reject)=>setTimeout(()=>reject(new Error('native_download_timeout')),15000))]);assert(received);assert.equal(digest(fs.readFileSync(await received.path())),config.pdf_sha256);
   await page.screenshot({path:config.output+'/native-'+name+'.png'});
   const fileURL=opened.url();const token=await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-auth')).access_token);
   const head=await page.evaluate(async url=>{const response=await fetch(url,{method:'HEAD',credentials:'include'});return {status:response.status,length:response.headers.get('content-length')};},fileURL);assert.equal(head.status,200);assert(Number(head.length)>0);
   await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.getByRole('heading',{name:'Sign in to read',exact:true}).waitFor();
   const denial=await page.evaluate(async ({files,token,url})=>{const setup=await fetch(files+'/api/file-session',{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+token}});const read=await fetch(url,{method:'HEAD',credentials:'include'});return {statuses:[setup.status,read.status],code:read.headers.get('X-PtS-Error-Code')};},{files:config.files,token,url:fileURL});assert.deepEqual(denial,{statuses:[401,401],code:'authentication_required'});
   assert.equal(errors.length,0);checks.push({browser:'Chromium',viewport:name,real_password_login:true,directory:true,native_pdf_response:true,native_download_hash:true,host_only_cookie:true,provider_local_logout:true,revoked_setup_and_HEAD_denied:true,typed_HEAD_error_readable_across_TLS:true});await context.close();
  }
  if(config.session_races)await sessionRaces(browser);
 }finally{await browser.close();}
 fs.writeFileSync(config.output+'/native-browser-proof.json',JSON.stringify({checks,excluded:['human device','hosted origins',...(config.session_races?[]:['delayed setup race','closed-app expiry']),'128MiB resource matrix']},null,2)+'\n',{mode:0o600,flag:'wx'});
}
module.exports={login,ownContext,statuses};
if(require.main===module)run().catch(error=>{process.stderr.write('native_browser_failed: '+(error.stack||error.name)+'\n');process.exitCode=1;});
