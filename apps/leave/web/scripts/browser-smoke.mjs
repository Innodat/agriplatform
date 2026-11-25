// GENERATED Leave browser proof; update the owning native runner.
/** Genuine synthetic SDK sign-in/protected path; controlled Microsoft ports are separate. */
import {readFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {chromium,expect} from '@playwright/test';
import assert from 'node:assert/strict';
const path=process.argv[2];assert.ok(path,'leave_browser_private_fixture_required');
const f=JSON.parse(readFileSync(path));const checks=[],controlledOAuth=[];
function control(action,subject,session){const result=spawnSync(f.python,[f.control,'--fixture',path,'--action',action,'--account',subject.account,...(session?['--session',session]:[])],{encoding:'utf8',timeout:10000});assert.equal(result.status,0,'fresh-browser-control-failed');return JSON.parse(result.stdout);}const browser=await chromium.launch({headless:true});let lastPage;
try{
 for(const [index,origin] of f.origins.entries()){
  const context=await browser.newContext({viewport:{width:1280,height:850}}),page=await context.newPage();lastPage=page;
  const failed=[];page.on('pageerror',()=>failed.push('page-error'));
  async function sdkSession(action,subject){
   return page.evaluate(async({authUrl,anonKey,action,subject})=>{
    const source=await(await fetch('/src/leave-session.ts')).text();
    const module=source.match(/from\s*["']([^"']*supabase[^"']*)["']/)?.[1];if(!module)throw Error('sdk_module_not_found');
    const {createClient}=await import(module);
    const sdk=globalThis.__leaveQualificationSdk??=createClient(authUrl,anonKey,{auth:{storageKey:'leave-auth-v1',flowType:'pkce',detectSessionInUrl:false,persistSession:true,autoRefreshToken:false}});
    const result=action==='password'?await sdk.auth.signInWithPassword({email:subject.email,password:subject.password}):action==='refresh'?await sdk.auth.refreshSession():await sdk.auth.getSession();
    await sdk.auth.stopAutoRefresh();const session=result.data.session;const claims=session?JSON.parse(atob(session.access_token.split('.')[1].replaceAll('-','+').replaceAll('_','/'))):null;
    return{account_id:session?.user.id,error:!!result.error,stored:!!localStorage.getItem('leave-auth-v1'),access_token:session?.access_token,session_id:claims?.session_id};
   },{authUrl:f.auth_url,anonKey:f.anon_key,action,subject});
  }
  async function signIn(subject){
   await page.goto(origin+'/');await expect(page.getByRole('button',{name:'Sign in with Microsoft'})).toBeVisible();
   const bootstrap=await sdkSession('password',subject);assert.equal(bootstrap.account_id,subject.account);assert.equal(bootstrap.error,false);assert.equal(bootstrap.stored,true);
   await page.reload();await expect(page.getByRole('button',{name:'Sign out'})).toBeVisible();
   checks.push(`target-${index}-real-SDK-password-bootstrap-qualification-only`);
  }
  await signIn(f.subjects[0]);
  const picker=page.getByRole('combobox',{name:'Choose organization'});await expect(picker).toBeVisible();
  await picker.selectOption(f.orgs[0]);await expect(page.getByRole('heading',{name:f.names[0],exact:true})).toBeFocused();
  await expect(page.getByText('Welcome to Leave.')).toBeVisible();await page.screenshot({path:f.result.replace('.json','-desktop-'+index+'.png'),fullPage:true});assert.equal(new URL(page.url()).pathname,'/organizations/'+f.orgs[0]);
  // Actual API commit is held at the browser response boundary. Stay cancels
  // publication; the durable event does not claim navigation occurred.
  let releaseHeld,committedHeld;const held=new Promise(resolve=>{releaseHeld=resolve;}),committed=new Promise(resolve=>{committedHeld=resolve;});
  const heldPath='**/api/v1/organizations/'+f.orgs[1]+'/context/selection';
  await page.route(heldPath,async route=>{const response=await route.fetch();assert.equal(response.status(),200);committedHeld();await held;try{await route.fulfill({response});}catch{}});
  await picker.selectOption(f.orgs[1]);await committed;await page.getByRole('button',{name:'Stay',exact:true}).click();releaseHeld();await page.unroute(heldPath);
  await expect(page.getByRole('heading',{name:f.names[0],exact:true})).toBeFocused();assert.equal(new URL(page.url()).pathname,'/organizations/'+f.orgs[0]);checks.push(`target-${index}-actual-commit-held-ack-Stay-rejects-late-navigation`);
  await page.getByRole('combobox',{name:'Preferred language'}).selectOption('pt');await expect(page.getByText('Portuguese is preferred. English is shown where translation is unavailable.')).toBeVisible();
  await picker.focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');await expect(page.getByRole('heading',{name:f.names[1],exact:true})).toBeFocused();
  await expect(page.getByRole('combobox',{name:'Preferred language'})).toHaveValue('pt');
  // A real SDK refresh must recheck admission without creating a new selection.
  const countBeforeRenewal=control('count-selection',f.subjects[0]).count;
  const revisionBefore=await page.evaluate(async()=>{const {leaveSession}=await import('/src/leave-session.ts');return leaveSession.snapshot().revision;});
  const refreshed=await sdkSession('refresh');assert.equal(refreshed.error,false);
  await expect.poll(()=>page.evaluate(async()=>{const {leaveSession}=await import('/src/leave-session.ts');return leaveSession.snapshot().revision;})).toBeGreaterThan(revisionBefore);
  await expect(page.getByRole('heading',{name:f.names[1],exact:true})).toBeVisible();assert.equal(control('count-selection',f.subjects[0]).count,countBeforeRenewal);checks.push(`target-${index}-real-SDK-renewal-no-duplicate-selection-event`);
  // A concurrent real Identity preference update advances revision. User intent
  // survives conflict refresh and Retry uses a new operation/current revision.
  const currentSession=await sdkSession('read');const authorization={Authorization:'Bearer '+currentSession.access_token};
  await expect(page.getByRole('combobox',{name:'Preferred language'})).toHaveValue('pt');
  let releasePreference,receivedPreference,forwardedPreference;const preferenceForwarded=new Promise(resolve=>{forwardedPreference=resolve;}),preferenceHeld=new Promise(resolve=>{releasePreference=resolve;}),preferenceReceived=new Promise(resolve=>{receivedPreference=resolve;});
  const preferencePath='**/api/v1/me/preferences/language';let heldCommand;
  await page.route(preferencePath,async route=>{if(route.request().method()!=='PUT'){await route.continue();return;}heldCommand=route.request().postDataJSON();receivedPreference();await preferenceHeld;await route.continue();forwardedPreference();});
  const preferenceCommands=[];const capture=request=>{if(request.method()==='PUT'&&new URL(request.url()).pathname==='/api/v1/me/preferences/language')preferenceCommands.push(request.postDataJSON());};page.on('request',capture);
  await page.getByRole('combobox',{name:'Preferred language'}).selectOption('en');await preferenceReceived;
  const competing=await page.request.put(origin+'/api/v1/me/preferences/language',{headers:authorization,data:{operation_id:crypto.randomUUID(),expected_revision:heldCommand.expected_revision,preferred_locale:'pt'}});assert.equal(competing.status(),200);
  releasePreference();await preferenceForwarded;await page.unroute(preferencePath);await expect(page.getByRole('button',{name:'Retry language'})).toBeVisible();await expect(page.getByRole('combobox',{name:'Preferred language'})).toHaveValue('en');
  await page.getByRole('button',{name:'Retry language'}).click();await expect(page.getByRole('button',{name:'Retry language'})).toHaveCount(0);page.off('request',capture);
  assert.equal(preferenceCommands.length,2);assert.notEqual(preferenceCommands[0].operation_id,preferenceCommands[1].operation_id);assert.notEqual(preferenceCommands[0].expected_revision,preferenceCommands[1].expected_revision);assert.equal(preferenceCommands[1].preferred_locale,'en');checks.push(`target-${index}-actual-preference-conflict-retained-desired-locale-new-operation-Retry`);
  // Revoke this genuine provider session in the guarded fresh DB, reauthenticate
  // the same user through SDK, and establish a newly audited current return scope.
  const beforeReturn=control('count-selection',f.subjects[0]).count;control('revoke-session',f.subjects[0],currentSession.session_id);
  await page.getByRole('button',{name:'Refresh organization access'}).click();await expect(page.getByRole('button',{name:'Sign in with Microsoft'})).toBeVisible();await expect(page.getByText('Welcome to Leave.')).toHaveCount(0);
  const reauthenticated=await sdkSession('password',f.subjects[0]);assert.equal(reauthenticated.error,false);if(await page.getByRole('button',{name:'Retry access'}).isVisible())await page.getByRole('button',{name:'Retry access'}).click();
  await expect(page.getByRole('heading',{name:f.names[1],exact:true})).toBeVisible();assert.equal(control('count-selection',f.subjects[0]).count,beforeReturn+1);checks.push(`target-${index}-real-session-revocation-same-user-SDK-return-current-audited-scope`);
  // Actual keyboard launcher/menu navigation and focus return.
  await page.getByRole('button',{name:'App launcher'}).focus();await page.keyboard.press('Enter');
  await expect(page.getByRole('menuitem',{name:'Open Leave'})).toHaveAttribute('href',f.origins[0]+'/');await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'App launcher'})).toBeFocused();
  checks.push(`target-${index}-two-orgs-current-selection-language-and-keyboard-launcher`);
  for(const width of [390,320]){
   await page.setViewportSize({width,height:844});await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
   const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,controls:[...document.querySelectorAll('button,select')].every(e=>e.getBoundingClientRect().height>=44)}));
   assert.ok(dimensions.scroll<=dimensions.client+1,`reflow-${width}`);assert.ok(dimensions.controls);await expect(page.getByRole('heading',{name:f.names[1],exact:true})).toBeVisible();
   await page.screenshot({path:f.result.replace('.json','-narrow-'+index+'-'+width+'.png'),fullPage:true});checks.push(`target-${index}-long-name-narrow-${width}-200-percent-reflow-growing-controls`);
  }
  await page.evaluate(()=>{document.documentElement.style.fontSize='';document.documentElement.style.zoom='2';});await page.setViewportSize({width:640,height:900});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1));await page.screenshot({path:f.result.replace('.json','-css-zoom200-'+index+'.png'),fullPage:true});checks.push(`target-${index}-CSS-zoom-200-percent-reflow`);await page.evaluate(()=>{document.documentElement.style.zoom='';});await page.setViewportSize({width:1280,height:850});
  // Independent tabs establish separate scope; a reload performs audited deep-link entry.
  const second=await context.newPage();await second.goto(origin+'/organizations/'+f.orgs[0]);await expect(second.getByRole('heading',{name:f.names[0],exact:true})).toBeVisible();
  assert.equal(new URL(page.url()).pathname,'/organizations/'+f.orgs[1]);await second.close();checks.push(`target-${index}-independent-tabs-and-current-authorized-deep-link`);
  await page.getByRole('combobox',{name:'Preferred language'}).selectOption('pt');await expect(page.getByText('Portuguese is preferred. English is shown where translation is unavailable.')).toBeVisible();
  await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('button',{name:'Sign in with Microsoft'})).toBeVisible();await expect(page.getByText('Welcome to Leave.')).toHaveCount(0);
  await signIn(f.subjects[1]);await expect(page.getByRole('combobox',{name:'Preferred language'})).toHaveValue('en');await expect(page.getByRole('combobox',{name:'Choose organization'})).toHaveCount(0);await expect(page.getByRole('heading',{name:f.names[0],exact:true})).toBeVisible();checks.push(`target-${index}-single-org-name-without-switcher-and-account-isolation`);
  await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('button',{name:'Sign in with Microsoft'})).toBeVisible();await signIn(f.subjects[2]);await expect(page.getByText('You do not have access to a Leave organization.')).toBeVisible();await expect(page.getByText('Welcome to Leave.')).toHaveCount(0);checks.push(`target-${index}-real-provider-account-with-no-Leave-grants`);
  await context.close();assert.equal(failed.length,0);
  // Controlled Microsoft SDK/OAuth ports. The exchange below is deliberately a
  // double returning a genuine synthetic session; it never proves Microsoft/Entra.
  const oauthContext=await browser.newContext(),oauthPage=await oauthContext.newPage();let launches=0,exchanges=0;
  await oauthPage.route(f.auth_url+'/auth/v1/authorize**',async route=>{const url=new URL(route.request().url());assert.equal(url.searchParams.get('provider'),'azure');assert.equal(url.searchParams.get('scopes'),'email');assert.equal(url.searchParams.get('code_challenge_method'),'s256');assert.match(url.searchParams.get('code_challenge'),/^[A-Za-z0-9_-]{43}$/);launches++;await route.fulfill({contentType:'text/html',body:'<p>Controlled Microsoft provider port</p>'});});
  await oauthPage.route(f.auth_url+'/auth/v1/token?grant_type=pkce',async route=>{exchanges++;assert.equal(route.request().method(),'POST');await route.fulfill({json:f.subjects[0].provider_session,headers:{'Access-Control-Allow-Origin':origin}});});
  await oauthPage.goto(origin+'/');await oauthPage.getByRole('button',{name:'Sign in with Microsoft'}).click();await expect(oauthPage.getByText('Controlled Microsoft provider port')).toBeVisible();assert.equal(launches,1);
  await oauthPage.goto(origin+'/auth/callback?code=controlled-pkce');await expect(oauthPage.getByRole('combobox',{name:'Choose organization'})).toBeVisible();assert.equal(exchanges,1);assert.equal(new URL(oauthPage.url()).pathname,'/');assert.equal(await oauthPage.evaluate(()=>sessionStorage.getItem('leave.oauth.v1')),null);controlledOAuth.push(`target-${index}-actual-SDK-azure-PKCE-launch-and-controlled-exchange-current-admission`);
  await oauthPage.goto(origin+'/auth/callback?code=controlled-pkce');await expect(oauthPage.getByText('Current access could not be checked.')).toBeVisible();await expect(oauthPage.getByRole('combobox',{name:'Choose organization'})).toHaveCount(0);assert.equal(exchanges,1);controlledOAuth.push(`target-${index}-repeated-callback-no-prior-user-state-or-second-exchange`);
  await oauthPage.getByRole('button',{name:'Sign in with Microsoft'}).click();await expect(oauthPage.getByText('Controlled Microsoft provider port')).toBeVisible();await oauthPage.goto(origin+'/');
  await oauthPage.evaluate(()=>{const flow=JSON.parse(sessionStorage.getItem('leave.oauth.v1'));flow.created_at=0;sessionStorage.setItem('leave.oauth.v1',JSON.stringify(flow));});
  await oauthPage.goto(origin+'/auth/callback?code=stale-flow');await expect(oauthPage.getByText('Current access could not be checked.')).toBeVisible();await expect(oauthPage.getByRole('combobox',{name:'Choose organization'})).toHaveCount(0);assert.equal(exchanges,1);controlledOAuth.push(`target-${index}-stale-callback-consumed-without-prior-user-state`);await oauthContext.close();

  // A stale/unsafe callback with old persisted credentials cannot reveal their state.
  const invalid=await browser.newContext();await invalid.addInitScript(value=>localStorage.setItem('leave-auth-v1',value),JSON.stringify(f.subjects[0].provider_session));
  const bad=await invalid.newPage();await bad.goto(origin+'/auth/callback?code=unrequested');await expect(bad.getByText('Current access could not be checked.')).toBeVisible();await expect(bad.getByText('Welcome to Leave.')).toHaveCount(0);assert.equal(new URL(bad.url()).pathname,'/');await invalid.close();checks.push(`target-${index}-invalid-one-use-callback-reveals-no-prior-state`);
 }
 writeFileSync(f.result,JSON.stringify({status:'passed',checks,controlled_oauth:{checks:controlledOAuth,scope:'controlled SDK Microsoft launch/callback ports only; synthetic token exchange is a double, no Entra evidence'},scope:'genuine synthetic SDK/provider protected browser path; no Microsoft/Entra/device/hosted acceptance'},null,2)+'\n',{mode:0o600});
 console.log(JSON.stringify({status:'passed',checks:checks.length}));
}catch(error){try{await lastPage?.screenshot({path:f.result.replace('.json','-failure.png'),fullPage:true});}catch{}throw error;}finally{await browser.close();}
