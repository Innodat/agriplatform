// Actual Chromium DOM proof against the explicit host; all authority/data are synthetic.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,statSync} from 'node:fs';
import {join,resolve,extname,sep} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {spawnSync} from 'node:child_process';
import {A,O,C,OWNER,AUTHOR,EDITOR,Q,detail,history,aggregate,historyCursor,auditCursor} from './admin-portal-fixture.mjs';
const [proof,root]=process.argv.slice(2),capsule=join(proof,'capsule'),owner='apps/kdg-capture/web';
const scaffold=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root'),modules=join(scaffold,'apps/bootstrap-application/web/node_modules');
const require=createRequire(join(scaffold,'package.json'));
assert.equal(require('@playwright/test/package.json').version,'1.64.0');
for(const [name,version] of [['vite','8.3.4'],['@vitejs/plugin-react','6.1.2']])assert.equal(JSON.parse(readFileSync(join(modules,name,'package.json'))).version,version);
const config={configFile:false,tsconfig:join(capsule,owner,'tsconfig.admin-portal.json'),root:join(capsule,owner,'tests/admin-portal-fixture'),logLevel:'warn',build:{outDir:join(proof,'dist'),emptyOutDir:false}};
writeFileSync(join(proof,'build.mjs'),`import {build} from ${JSON.stringify(pathToFileURL(join(modules,'vite/dist/node/index.js')).href)};import react from ${JSON.stringify(pathToFileURL(join(modules,'@vitejs/plugin-react/dist/index.js')).href)};await build({...${JSON.stringify(config)},plugins:[react()]});`);
const built=spawnSync(process.execPath,[join(proof,'build.mjs')],{cwd:root,encoding:'utf8',timeout:30000});writeFileSync(join(proof,'build.log'),built.stdout+built.stderr);assert.equal(built.status,0,'vite_build_failed');
const {chromium}=require('@playwright/test'),checks=[],requests=[],issues=[],failedResponses=[],consoleErrors=[],sockets=new Set(),held=[];
const INITIATOR='99999999-9999-4999-8999-999999999999';
const records=Array.from({length:7},(_,i)=>detail({capture_id:i===0?C:`cccccccc-cccc-4ccc-8ccc-ccccccccccc${i}`,child_label:i===0?'Original child':`Child ${i+1}`,revision:'7',created_at:`2026-10-26T10:00:0${7-i}Z`}));
let mode='success',browser,server,stopped=true;
function valueFor(path){
 const parsed=new URL(path,'http://local'),id=/\/captures\/([^/]+)/.exec(parsed.pathname)?.[1],record=records.find(d=>d.capture_id===id)??records[0];
 if(parsed.pathname.endsWith('/audit-details')){
  const limit=Number(parsed.searchParams.get('limit')),isEarlier=parsed.searchParams.has('cursor');
  const events=(limit===1?[7]:isEarlier?[2,1]:[7,6,5,4,3]).map(r=>({revision:String(r),command_type:r===1?'capture.create':'capture.edit',executor_actor_id:r===1?AUTHOR:EDITOR,initiator_actor_id:r===7?INITIATOR:null,recorded_at:r===1?record.created_at:record.updated_at}));
  const result=aggregate(record,limit,{events,next_cursor:limit===5&&!isEarlier?auditCursor(id,5,'3'):null});
  if(mode==='outage')result.actor_display={status:'temporarily_unavailable'};
  if(mode==='unmapped')result.actor_display.labels[0]={actor_id:AUTHOR,status:'unavailable'};
  if(mode==='partial')result.actor_display.labels.pop();
  if(mode==='foreign')result.actor_display.labels[0].actor_id=Q;
  if(mode==='mismatch')result.audit.updated_at='2026-10-26T11:02:00Z';
  if(result.actor_display.status==='loaded'&&events.some(event=>event.initiator_actor_id===INITIATOR)){result.actor_display.labels.push({actor_id:INITIATOR,status:'resolved',display_name:'Separate initiator'});result.actor_display.labels.sort((a,b)=>a.actor_id.localeCompare(b.actor_id));}
  return result;
 }
 if(id)return record;
 if(parsed.searchParams.get('from_date')==='2026-10-20'&&parsed.searchParams.get('to_date')==='2026-10-27')return history([{...records[6],child_label:'Filtered child'}],{from_date:'2026-10-20',to_date:'2026-10-27',next_cursor:null});
 const items=parsed.searchParams.has('cursor')?records.slice(5):records.slice(0,5);
 return history(mode==='empty'?[]:items,{from_date:parsed.searchParams.get('from_date'),to_date:parsed.searchParams.get('to_date'),next_cursor:mode==='empty'||parsed.searchParams.has('cursor')?null:historyCursor(items.at(-1))});
}
try{
 server=createServer((request,response)=>{
  response.setHeader('Cache-Control','private, no-store');
  if(request.url.startsWith('/api/')){
   assert.equal(request.method,'GET');assert.equal(request.headers.authorization,'Bearer synthetic');assert.equal(request.headers['x-service-key'],undefined);
   const path=request.url;requests.push({path,method:request.method});const selected=mode;
   const send=()=>{if(response.destroyed)return;response.setHeader('Content-Type','application/json');
    if((selected==='missing-detail'&&/^\/api\/v1\/admin\/captures\/[^/?]+$/.test(path))||(selected==='missing-audit-page'&&path.includes('/audit-details?')&&path.includes('cursor='))){response.writeHead(404).end(JSON.stringify({error:'PRIVATE FAILURE',error_id:'capture_unavailable'}));return;}
    if(['denied','expired','unavailable','held-denied'].includes(selected)){response.writeHead(selected==='denied'||selected==='held-denied'?403:selected==='expired'?401:503).end(JSON.stringify({error:'PRIVATE FAILURE',error_id:selected==='denied'||selected==='held-denied'?'access_denied':selected==='expired'?'authentication_required':'authorization_unavailable'}));return;}
    const previous=mode;mode=selected==='held'?'success':selected;const value=valueFor(path);mode=previous;response.end(JSON.stringify(value));
   };if(selected.startsWith('held')||(selected==='hold-last'&&path.includes(records[4].capture_id)))held.push(send);else send();return;
  }
  if(request.url==='/favicon.ico'){response.writeHead(204).end();return;}
  const directory=join(proof,'dist'),path=resolve(directory,'.'+new URL(request.url,'http://local').pathname),file=path===directory?join(directory,'index.html'):path;
  if(!file.startsWith(directory+sep)||!existsSync(file)||!statSync(file).isFile()){response.writeHead(404).end();return;}
  response.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[extname(file)]??'application/octet-stream');response.end(readFileSync(file));
 });
 server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});server.listen(0,'127.0.0.1');await once(server,'listening');stopped=false;
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 await page.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
 page.on('pageerror',()=>issues.push('pageerror'));page.on('console',message=>{if(message.type()==='error'){let path='<unknown>';try{path=new URL(message.location().url).pathname;}catch{}consoleErrors.push({path,resource_failure:message.text().startsWith('Failed to load resource:')});}});
 page.on('response',response=>{if(!response.ok())failedResponses.push({path:new URL(response.url()).pathname,status:response.status()});});
 const historyHeading=()=>page.getByRole('heading',{name:'Observation history',exact:true}),detailHeading=()=>page.getByRole('heading',{name:'Observation details',exact:true});
 const selectedRow=()=>page.locator('#capture-'+C);
 async function fresh(){mode='success';await page.evaluate(()=>window.fixture.portal.refresh());await historyHeading().waitFor();}
 function release(){for(const send of held.splice(0))send();}
 async function waitHeld(){const end=Date.now()+3000;while(!held.length&&Date.now()<end)await new Promise(resolve=>setTimeout(resolve,10));assert.ok(held.length>0,'synthetic held HTTP response must actually arrive before invalidation');}
 async function noBusiness(){assert.equal(await page.locator('[id^="capture-"]').count(),0);assert.equal(await page.getByText('Original answer',{exact:true}).count(),0);}
 async function layout(){assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);for(const button of await page.getByRole('button').all())assert.ok((await button.boundingBox()).height>=48);}
 const initialOffline=await browser.newPage();await initialOffline.addInitScript(()=>Object.defineProperty(navigator,'onLine',{get:()=>false}));const offlineCalls=requests.length;await initialOffline.goto(origin);await initialOffline.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();assert.equal(requests.length,offlineCalls);await initialOffline.close();checks.push('initial_browser_offline_no_all_read_dispatch');
 await page.goto(origin);await historyHeading().waitFor();
 assert.equal(await page.locator('.kdg-admin-history li').count(),5);assert.equal(requests.length,6);assert.equal(await page.locator('img').count(),0);assert.ok((await selectedRow().innerText()).includes('<img src=x onerror=alert(1)> Capturer'));checks.push('authorized_cross_owner_five_rows_one_history_five_enrichments_html_name_escaped');
 await selectedRow().focus();await selectedRow().press('Enter');await detailHeading().waitFor();assert.equal(await detailHeading().evaluate(e=>document.activeElement===e),true);
 assert.equal(await page.getByText('Ja',{exact:true}).count(),1);assert.equal(await page.getByText('Original details',{exact:true}).count(),1);assert.equal(await page.getByText('Original answer',{exact:true}).count(),1);
 assert.deepEqual(await page.locator('.kdg-admin-questions h3').allTextContents(),['Hoe voel die kind?','Het die kind hulp nodig?','Opmerkings']);assert.equal(await page.getByRole('heading',{name:'Read-only audit',exact:true}).count(),0);checks.push('keyboard_original_question_order_values_details_initially_collapsed_audit');
 await page.getByRole('button',{name:'Show audit',exact:true}).click();assert.equal(await page.getByText('Actual executor',{exact:true}).count(),5);assert.equal(await page.getByText('Initiator',{exact:true}).count(),1);assert.equal(await page.locator('.kdg-admin-events li').count(),5);
 const latestEvent=page.locator('.kdg-admin-events li').filter({has:page.getByRole('heading',{name:'Revision 7',exact:true})});
 assert.equal(await latestEvent.locator('dt:has-text("Actual executor") + dd').innerText(),'Actual editor');assert.equal(await latestEvent.locator('dt:has-text("Initiator") + dd').innerText(),'Separate initiator');assert.equal(await latestEvent.getByText('<img src=x onerror=alert(1)> Capturer',{exact:true}).count(),0);
 await page.getByRole('button',{name:'Earlier audit events',exact:true}).click();await page.getByRole('heading',{name:'Revision 1',exact:true}).waitFor();assert.equal(await page.locator('.kdg-admin-events li').count(),2);assert.equal(await page.getByRole('heading',{name:'Read-only audit',exact:true}).evaluate(e=>document.activeElement===e),true);assert.equal(await page.getByText('2026-10-26T11:01:00.000001Z',{exact:true}).count(),2);checks.push('audit_replaced_page_fresh_detail_header_exact_time_revision_separate_initiator_focus');
 await page.getByRole('button',{name:'Back to history',exact:true}).click();await historyHeading().waitFor();assert.equal(await selectedRow().evaluate(e=>document.activeElement===e),true);
 const lastRow=page.locator('#capture-'+records[4].capture_id);await lastRow.scrollIntoViewIfNeeded();const savedScroll=await page.evaluate(()=>window.scrollY);await lastRow.click();await detailHeading().waitFor();await page.getByRole('button',{name:'Back to history',exact:true}).click();await historyHeading().waitFor();assert.equal(await lastRow.evaluate(e=>document.activeElement===e),true);assert.ok(Math.abs((await page.evaluate(()=>window.scrollY))-savedScroll)<=1);checks.push('back_fresh_history_returns_selected_row_focus_and_scroll');
 await page.getByRole('button',{name:'Next history page',exact:true}).click();await page.getByText('Child 7',{exact:true}).waitFor();assert.equal(await page.locator('.kdg-admin-history li').count(),2);assert.equal(await selectedRow().count(),0);assert.equal(await historyHeading().evaluate(e=>document.activeElement===e),true);checks.push('opaque_history_cursor_replaces_five_row_page_and_focuses_heading');
 await page.getByLabel('From observation date',{exact:true}).fill('2026-10-20');await page.getByLabel('To observation date',{exact:true}).fill('2026-10-27');mode='held-dates';
 await page.getByRole('button',{name:'Apply dates',exact:true}).click();await noBusiness();await waitHeld();
 const changedQuery=new URL(requests.at(-1).path,origin).searchParams;assert.equal(changedQuery.get('from_date'),'2026-10-20');assert.equal(changedQuery.get('to_date'),'2026-10-27');assert.equal(changedQuery.has('cursor'),false);assert.equal(changedQuery.get('limit'),'5');mode='success';release();
 await page.getByText('Filtered child',{exact:true}).waitFor();assert.equal(await page.locator('.kdg-admin-history li').count(),1);assert.equal(await page.getByText('Child 7',{exact:true}).count(),0);assert.equal(await historyHeading().evaluate(e=>document.activeElement===e),true);checks.push('apply_both_dates_from_later_page_clears_dom_and_cursor_replaces_fresh_results');
 await page.getByLabel('From observation date',{exact:true}).fill('2026-10-01');await page.getByLabel('To observation date',{exact:true}).fill('2026-10-28');await page.getByRole('button',{name:'Apply dates',exact:true}).click();await selectedRow().waitFor();
 await page.getByRole('button',{name:'First history page',exact:true}).click();await selectedRow().waitFor();
 for(const [width,scale] of [[1440,100],[390,100],[320,200]]){
  await page.setViewportSize({width,height:900});await page.evaluate(scale=>{document.documentElement.style.fontSize=scale+'%';},scale);await layout();
  await selectedRow().click();await detailHeading().waitFor();await page.getByRole('button',{name:'Show audit',exact:true}).click();await layout();await page.screenshot({path:join(proof,`layout-${width}-${scale}.png`),fullPage:true});await page.getByRole('button',{name:'Back to history',exact:true}).click();await selectedRow().waitFor();
 }
 checks.push('desktop_phone_320px_200percent_wrapping_48px_controls_screenshots');
 await page.evaluate(()=>{document.documentElement.style.fontSize='100%';});await page.setViewportSize({width:390,height:844});
 const colors=await page.evaluate(()=>{const node=document.querySelector('.kdg-entry'),button=document.querySelector('button'),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');return [getComputedStyle(node).color,getComputedStyle(node).backgroundColor,getComputedStyle(button).color,getComputedStyle(button).backgroundColor].map(color=>{ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].slice(0,3);});});
 const luminance=rgb=>rgb.map(v=>{v/=255;return v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4;}).reduce((a,v,i)=>a+v*[0.2126,0.7152,0.0722][i],0),contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return(Math.max(x,y)+0.05)/(Math.min(x,y)+0.05);};
 assert.ok(contrast(colors[0],colors[1])>=4.5);assert.ok(contrast(colors[2],colors[3])>=4.5);await selectedRow().focus();assert.equal(await selectedRow().evaluate(e=>parseFloat(getComputedStyle(e).outlineWidth)>=3),true);checks.push('measured_neutral_text_control_contrast_and_visible_keyboard_focus');
 mode='unmapped';await page.evaluate(()=>window.fixture.portal.refresh());await historyHeading().waitFor();assert.equal(await page.getByText('Original capturer: Name unavailable',{exact:true}).count(),5);checks.push('unmapped_names_safe_without_uuid_or_guessed_system');
 mode='outage';await page.evaluate(()=>window.fixture.portal.refresh());await historyHeading().waitFor();assert.equal(await page.getByText('Original capturer: Names temporarily unavailable',{exact:true}).count(),5);const before=requests.length;mode='success';await page.getByRole('button',{name:'Retry',exact:true}).click();await selectedRow().waitFor();assert.equal(requests.length,before+6);checks.push('valid_name_outage_distinct_fallback_retry_full_history_read');
 for(const selectedMode of ['partial','foreign']){mode=selectedMode;await page.evaluate(()=>window.fixture.portal.refresh());await page.getByRole('heading',{name:'Review unavailable',exact:true}).waitFor();await noBusiness();assert.equal(await page.getByText('No observations in these dates.',{exact:true}).count(),0);await fresh();}checks.push('foreign_partial_labels_withhold_whole_page_not_empty');
 mode='mismatch';await selectedRow().click();await page.getByRole('heading',{name:'Review unavailable',exact:true}).waitFor();await noBusiness();mode='success';await page.getByRole('button',{name:'Retry',exact:true}).click();await detailHeading().waitFor();checks.push('concurrent_detail_audit_mismatch_withholds_answers_explicit_complete_retry');await fresh();
 for(const missing of ['missing-detail','missing-audit-page']){
  if(missing==='missing-audit-page'){await selectedRow().click();await detailHeading().waitFor();await page.getByRole('button',{name:'Show audit',exact:true}).click();mode=missing;await page.getByRole('button',{name:'Earlier audit events',exact:true}).click();}
  else {mode=missing;await selectedRow().click();}
  await page.getByRole('heading',{name:'Review unavailable',exact:true}).waitFor();await noBusiness();await page.getByRole('button',{name:'Retry',exact:true}).click();await page.getByRole('heading',{name:'Review unavailable',exact:true}).waitFor();
  const start=requests.length;await page.getByRole('button',{name:'Return to history',exact:true}).click();await historyHeading().waitFor();assert.equal(requests.length,start+6);assert.equal(new URL(requests[start].path,origin).searchParams.has('cursor'),false);assert.equal(await selectedRow().count(),1);mode='success';
 }checks.push('persistent_record_and_audit_cursor_404_exit_via_visible_fresh_history');
 mode='empty';const emptyStart=requests.length;await page.evaluate(()=>window.fixture.portal.refresh());await historyHeading().waitFor();assert.equal(await page.getByText('No observations in these dates.',{exact:true}).count(),1);assert.equal(requests.length,emptyStart+1);checks.push('successful_empty_page_no_enrichment');await fresh();
 mode='hold-last';await page.evaluate(()=>{void window.fixture.portal.refresh();});await waitHeld();await noBusiness();release();await historyHeading().waitFor();checks.push('last_enrichment_delayed_never_publishes_partial_rows');mode='success';
 // Inspect the DOM inside the invalidating call, before awaiting a browser turn.
 for(const loss of ['fresh','offline','event','account','signout','org']){
  mode='held';
  const cleared=await page.evaluate(({loss,owner,org})=>{
   if(loss==='fresh')void window.fixture.portal.refresh();
   if(loss==='offline')window.dispatchEvent(new Event('offline'));
   if(loss==='event')window.fixture.event('TOKEN_REFRESHED');
   if(loss==='account')window.fixture.event('SIGNED_IN',owner);
   if(loss==='signout')void window.fixture.portal.signOut();
   if(loss==='org')void window.fixture.portal.replaceOrganization(org);
   return document.querySelectorAll('[id^="capture-"]').length===0&&!document.body.textContent.includes('Original answer');
  },{loss,owner:OWNER,org:Q});assert.equal(cleared,true,loss+' synchronous DOM removal');
  release();mode='success';
  if(loss==='offline')await page.evaluate(()=>window.dispatchEvent(new Event('online')));
  if(loss==='account')await page.evaluate(account=>window.fixture.event('SIGNED_IN',account),A);
  if(loss==='org')await page.evaluate(org=>window.fixture.portal.replaceOrganization(org),O);
  else if(loss==='signout'){await page.evaluate(()=>window.fixture.portal.refresh());await page.getByRole('heading',{name:'Sign in to review',exact:true}).waitFor();await page.getByRole('button',{name:'Sign in',exact:true}).click();}
  else await page.evaluate(()=>window.fixture.portal.refresh());
  await historyHeading().waitFor();release();
 }
 checks.push('synchronous_dom_clearing_fresh_offline_auth_event_account_signout_org');
 for(const late of ['success','denied']){
  await page.evaluate(()=>window.fixture.ignoreAbort(true));mode=late==='success'?'held':'held-denied';
  const clearedOnView=await page.evaluate(capture=>{void window.fixture.portal.select(capture);return document.querySelectorAll('[id^="capture-"]').length===0;},C);assert.equal(clearedOnView,true);await waitHeld();
  const removed=await page.evaluate(()=>{window.fixture.event('SIGNED_OUT',null);return !document.body.textContent.includes('Original answer');});assert.equal(removed,true);release();mode='success';await page.getByRole('heading',{name:'Sign in to review',exact:true}).waitFor();await noBusiness();await new Promise(r=>setTimeout(r,50));await noBusiness();await page.evaluate(()=>window.fixture.ignoreAbort(false));
  await page.evaluate(account=>window.fixture.event('SIGNED_IN',account),A);await fresh();
 }checks.push('actual_held_http_success_and_denied_after_signout_ignored_abort_cannot_reopen');
 for(const selectedMode of ['denied','unavailable','expired']){
  await page.evaluate(()=>window.dispatchEvent(new Event('offline')));mode=selectedMode;await page.evaluate(()=>window.dispatchEvent(new Event('online')));
  await page.getByRole('heading',{name:selectedMode==='denied'?'Access denied':selectedMode==='expired'?'Sign in to review':'Review unavailable',exact:true}).waitFor();await noBusiness();await fresh();
 }checks.push('reconnect_rechecks_all_read_denied_expired_unavailable_distinct');
 assert.deepEqual(await page.evaluate(async()=>({local:localStorage.length,session:sessionStorage.length,idb:await indexedDB.databases(),caches:await caches.keys(),workers:(await navigator.serviceWorker.getRegistrations()).length})),{local:0,session:0,idb:[],caches:[],workers:0});assert.ok(!(await page.locator('body').innerText()).includes('PRIVATE FAILURE'));assert.deepEqual(issues,[]);
 assert.deepEqual(failedResponses,[...Array.from({length:2},()=>({path:'/api/v1/admin/captures/'+C,status:404})),...Array.from({length:2},()=>({path:'/api/v1/admin/captures/'+C+'/audit-details',status:404})),{path:'/api/v1/admin/captures/'+C,status:403},...[[403,'denied'],[503,'unavailable'],[401,'expired']].map(([status])=>({path:'/api/v1/admin/captures',status}))]);assert.equal(consoleErrors.length,failedResponses.length);assert.ok(consoleErrors.every(e=>e.resource_failure&&failedResponses.some(r=>r.path===e.path)));checks.push('no_business_storage_private_errors_or_external_calls_exact_expected_http_failures');
 mode='held';await page.evaluate(()=>{window.fixture.ignoreAbort(true);void window.fixture.portal.select('cccccccc-cccc-4ccc-8ccc-cccccccccccc');});await waitHeld();const disposed=await page.evaluate(()=>{window.fixture.dispose();return document.getElementById('root').textContent;});assert.equal(disposed,'');release();await new Promise(r=>setTimeout(r,50));assert.equal(await page.locator('#root').innerText(),'');checks.push('explicit_host_disposal_clears_dom_during_actual_ignored_abort_http');
 writeFileSync(join(proof,'browser-result.json'),JSON.stringify({passed:true,checks,requests,issues,failedResponses,consoleErrors,contrast:{text:contrast(colors[0],colors[1]),controls:contrast(colors[2],colors[3])},limits:['synthetic Auth port, same-origin API fixtures and loopback Chromium','viewport/font-size simulations; no physical device or native database qualification']},null,2)+'\n');
}finally{
 await browser?.close();for(const socket of sockets)socket.destroy();if(server){await new Promise(resolve=>server.close(resolve));stopped=true;}
 writeFileSync(join(proof,'browser-lifecycle.json'),JSON.stringify({fixture_server_stopped:stopped,remaining_sockets:sockets.size,retained_artifacts:true})+'\n');
}
