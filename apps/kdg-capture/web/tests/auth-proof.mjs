// Synthetic SDK/session proof. All emitted files live in a fresh private capsule.
import assert from 'node:assert/strict';
import {readFileSync,mkdirSync,writeFileSync,symlinkSync,existsSync,statSync} from 'node:fs';
import {resolve,join,sep,extname} from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
const root=process.cwd(),hash=value=>createHash('sha256').update(value).digest('hex');
const retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(process.version,'v26.11.1');
for(const [name,version] of [['typescript','7.0.2'],['@supabase/supabase-js','2.117.3'],['@supabase/auth-js','2.117.3'],['react','19.3.0'],['react-dom','19.3.0']])assert.equal(JSON.parse(readFileSync(join(retained,'node_modules',name,'package.json'))).version,version);
const directory=join(root,'platform/deployment/.local/kdg-auth-entry-20261023');mkdirSync(directory,{recursive:true,mode:0o700});
const proof=join(directory,'auth-'+randomUUID());mkdirSync(proof,{mode:0o700});const capsule=join(proof,'capsule');mkdirSync(capsule);
writeFileSync(join(capsule,'package.json'),JSON.stringify({private:true,type:'module'}));symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
const owner='apps/kdg-capture/web';
const sources=[owner+'/src/history.ts',owner+'/src/history-entry.ts',owner+'/tests/history.test.mjs',owner+'/tests/history-entry.test.mjs',owner+'/tests/history-fixture.mjs',owner+'/tests/history.types.ts',owner+'/tests/history-entry.types.ts','apps/kdg-capture/contracts/history-generated/types.gen.ts','apps/kdg-capture/write-candidate/history-openapi.json',owner+'/src/read-validation.ts',owner+'/src/read.ts',owner+'/src/read-entry.ts',owner+'/tests/read.test.mjs',owner+'/tests/read-fixture.mjs',owner+'/tests/read-entry.test.mjs',owner+'/tests/read.types.ts',owner+'/tests/read-entry.types.ts','apps/kdg-capture/contracts/read-generated/types.gen.ts','apps/kdg-capture/write-candidate/read-openapi.json',owner+'/src/create.ts',owner+'/src/create-entry.ts',owner+'/tests/create.test.mjs',owner+'/tests/create-entry.test.mjs',owner+'/tests/create.types.ts',owner+'/tests/create-entry.types.ts','apps/kdg-capture/contracts/create-generated/types.gen.ts','apps/kdg-capture/write-candidate/create-openapi.json',owner+'/src/edit-entry.ts',owner+'/src/edit.ts',owner+'/tests/edit-entry.test.mjs',owner+'/tests/edit-entry.types.ts','apps/kdg-capture/contracts/edit-generated/types.gen.ts',owner+'/tests/recovery-entry.types.ts',owner+'/src/recovery-entry.ts',owner+'/src/recovery.ts',owner+'/tests/recovery-entry.test.mjs','apps/kdg-capture/contracts/recovery-generated/types.gen.ts',owner+'/index.html',owner+'/src/main.ts',owner+'/src/startup.tsx',owner+'/src/ClosedEntry.tsx',owner+'/src/auth-public-input.ts',owner+'/src/local-public-config.ts',owner+'/.generated-files.json',owner+'/src/auth/lifecycle.ts',owner+'/src/auth/use-lifecycle.ts',owner+'/scripts/test-auth-lifecycle.mjs',owner+'/src/auth-entry.ts',owner+'/src/email-auth.ts',owner+'/src/EmailCodeEntry.tsx',owner+'/src/LocalEntryRoute.tsx',owner+'/tests/auth-fixture/email-code.tsx',owner+'/tests/auth-fixture/local-entry.tsx',owner+'/tests/auth-fixture/legacy-entry.tsx',owner+'/src/AuthEntry.tsx',owner+'/src/EntryScreen.tsx',owner+'/src/entry-screen.css',owner+'/src/styles.d.ts',owner+'/tests/auth-fixture/main.tsx',owner+'/tests/auth-fixture/index.html',owner+'/src/entry.ts',owner+'/package.json',owner+'/tsconfig.auth.json',owner+'/tests/auth-entry.test.mjs',owner+'/tests/local-public-config.test.mjs',owner+'/tests/auth-proof.mjs','apps/kdg-capture/contracts/generated/types.gen.ts'];
const captured=Object.fromEntries(sources.map(path=>{const data=readFileSync(join(root,path)),destination=join(capsule,path);mkdirSync(resolve(destination,'..'),{recursive:true});writeFileSync(destination,data);return[path,hash(data)];}));
const selected_mode=process.argv.includes('--create-only')?'create-only':process.argv.includes('--edit-entry-only')?'edit-entry-only':process.argv.includes('--acceptance-only')?'acceptance-only':process.argv.includes('--unit-only')?'unit-only':'browser';
const selected_test_files=(selected_mode==='create-only'?['tests/create.test.mjs','tests/create-entry.test.mjs']:selected_mode==='edit-entry-only'?['tests/edit-entry.test.mjs']:[ 'tests/history.test.mjs','tests/history-entry.test.mjs','tests/read.test.mjs','tests/read-entry.test.mjs','tests/create.test.mjs','tests/create-entry.test.mjs','tests/edit-entry.test.mjs','tests/recovery-entry.test.mjs','tests/local-public-config.test.mjs','tests/auth-entry.test.mjs','scripts/test-auth-lifecycle.mjs']).map(path=>owner+'/'+path);
let test_counts=null;
let passed=false,browser,server;const sockets=new Set(),checks=[],requests=[],issues=[],failedResponses=[];let stopped=true;
try{
 const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,owner,'tsconfig.auth.json'),'--noEmit','false','--rootDir',join(capsule,'apps/kdg-capture'),'--outDir',join(capsule,'compiled')],{encoding:'utf8',timeout:30000});
 writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0,'types_failed');checks.push('strict_ts7_own_source');
 const invalid=join(capsule,'invalid-own-source.ts');writeFileSync(invalid,'const invalid: string = 17;\n');
 const negativeConfig=join(capsule,'negative-types.json');writeFileSync(negativeConfig,JSON.stringify({extends:join(capsule,owner,'tsconfig.auth.json'),files:[invalid]}));
 const negative=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',negativeConfig,'--noEmit'],{encoding:'utf8',timeout:30000});
 writeFileSync(join(proof,'types-negative.log'),negative.stdout+negative.stderr);assert.ifError(negative.error);assert.ok(negative.status!==0&&negative.stdout.includes('TS2322'),'own_source_negative_control_failed');checks.push('strict_own_source_negative_control');
 const args=['--test','--test-isolation=none','--test-reporter=tap'];if(selected_mode==='acceptance-only')args.push('--test-name-pattern','current SDK session admits');args.push(...selected_test_files.map(path=>join(capsule,path)));
 const unit=spawnSync(process.execPath,args,{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'unit.log'),unit.stdout+unit.stderr);assert.ifError(unit.error);
 const count=name=>{const match=unit.stdout.match(new RegExp('^# '+name+' (\\d+)$','m'));return match?Number(match[1]):null;};
 const total=count('tests'),skipped=count('skipped');test_counts={total,executed:total===null||skipped===null?null:total-skipped,passed:count('pass'),failed:count('fail'),cancelled:count('cancelled'),skipped,todo:count('todo')};
 assert.equal(unit.status,0,'unit_failed');assert.ok(test_counts.executed>0,'no_selected_tests_executed');checks.push('sdk_session_tests');
 if(selected_mode==='browser'){
  const scaffold=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root');
  const modules=join(scaffold,'apps/bootstrap-application/web/node_modules');
  for(const [name,version] of [['vite','8.3.4'],['@vitejs/plugin-react','6.1.2']])assert.equal(JSON.parse(readFileSync(join(modules,name,'package.json'))).version,version);
  const config={configFile:false,tsconfig:join(capsule,owner,'tsconfig.auth.json'),root:join(capsule,owner,'tests/auth-fixture'),logLevel:'warn',build:{outDir:join(proof,'dist'),emptyOutDir:false}};
  writeFileSync(join(proof,'build.mjs'),`import {build} from ${JSON.stringify(pathToFileURL(join(modules,'vite/dist/node/index.js')).href)};import react from ${JSON.stringify(pathToFileURL(join(modules,'@vitejs/plugin-react/dist/index.js')).href)};await build({...${JSON.stringify(config)},plugins:[react()]});`);
  const built=spawnSync(process.execPath,[join(proof,'build.mjs')],{cwd:config.root,encoding:'utf8',timeout:30000});writeFileSync(join(proof,'build.log'),built.stdout+built.stderr);assert.equal(built.status,0,'vite_build_failed');checks.push('vite8_react19');
  const startupConfig={...config,root:join(capsule,owner),build:{outDir:join(proof,'dist-startup'),emptyOutDir:false}};
  writeFileSync(join(proof,'build-startup.mjs'),`import {build} from ${JSON.stringify(pathToFileURL(join(modules,'vite/dist/node/index.js')).href)};import react from ${JSON.stringify(pathToFileURL(join(modules,'@vitejs/plugin-react/dist/index.js')).href)};await build({...${JSON.stringify(startupConfig)},plugins:[react()]});`);
  const startupBuilt=spawnSync(process.execPath,[join(proof,'build-startup.mjs')],{cwd:startupConfig.root,encoding:'utf8',timeout:30000});writeFileSync(join(proof,'build-startup.log'),startupBuilt.stdout+startupBuilt.stderr);assert.equal(startupBuilt.status,0,'actual_app_build_failed');checks.push('actual_app_index_main_build');
  const require=createRequire(join(scaffold,'package.json'));assert.equal(require('@playwright/test/package.json').version,'1.64.0');const {chromium}=require('@playwright/test');
  const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';let mode='success',contextArrived=()=>{};const heldContexts=[];let servingStartup=false,startupScenario='default';const startupAuthPaths=[];
  function startupHtml(raw){
   if(startupScenario==='default')return raw;
   const value={schema_version:1,environment_kind:'local_disposable',org_id:ORG,auth_url:origin,auth_public_key:'sb_publishable_synthetic_public_123456'};
   if(startupScenario==='bad-org')value.org_id='PRIVATE';if(startupScenario==='remote-auth')value.auth_url='https://remote-auth.invalid';if(startupScenario==='private-key')value.auth_public_key='sb_secret_PRIVATE';if(startupScenario==='extra')value.service_key='PRIVATE';
   let content=startupScenario==='malformed'?'PRIVATE':startupScenario==='oversized'?JSON.stringify('x'.repeat(8193)):JSON.stringify(value).replace(/</g,'\\u003c');
   const expression=/(<script\b[^>]*\bid="kdg-local-config"[^>]*>)[\s\S]*?(<\/script>)/;
   assert.ok(expression.test(raw),'actual_config_element_missing');let html=raw.replace(expression,(_all,start,end)=>start+content+end);
   if(startupScenario==='missing')html=html.replace(expression,'');
   if(startupScenario==='duplicate')html=html.replace(expression,match=>match+match);
   if(startupScenario==='wrong-type')html=html.replace('type="application/json"','type="text/plain"');
   if(startupScenario==='src')html=html.replace('id="kdg-local-config"','id="kdg-local-config" src="https://PRIVATE.invalid/config"');
   if(startupScenario.startsWith('missing-root'))html=html.replace('id="root"','id="not-root"');
   if(startupScenario.startsWith('duplicate-root'))html=html.replace('id="root"','id="root"').replace('</body>','<div id="root"></div></body>');
   return html;
  }
  server=createServer((request,response)=>{
   response.setHeader('Cache-Control','private, no-store');
   if(servingStartup&&['/auth/v1/otp','/auth/v1/verify'].includes(request.url)){
    assert.equal(request.method,'POST');startupAuthPaths.push(request.url);let raw='';
    request.on('data',chunk=>{raw+=chunk;assert.ok(raw.length<=2048,'synthetic_auth_body_limit');});request.on('end',()=>{
     const body=JSON.parse(raw);assert.equal(request.headers.apikey,'sb_publishable_synthetic_public_123456');response.setHeader('Content-Type','application/json');
     if(request.url==='/auth/v1/otp'){assert.equal(body.create_user,false);response.end('{}');return;}
     assert.equal(body.type,'email');assert.equal(body.email,'facilitator@example.invalid');assert.equal(body.token,'123456');
     const token=Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:A,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})).toString('base64url')+'.c3ludGhldGlj';
     response.end(JSON.stringify({access_token:token,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}));
    });return;
   }
   if(servingStartup&&request.url==='/__parked'){response.setHeader('Content-Type','text/html');response.end('<!doctype html><html><body><h1>Paused</h1></body></html>');return;}
   if(request.url==='/api/v1/context'){
    assert.equal(request.method,'GET');assert.equal(request.headers['x-service-key'],undefined);
    const payload=JSON.parse(Buffer.from(request.headers.authorization.split('.')[1],'base64url').toString());const account=payload.sub,selected=mode;
    requests.push({path:request.url,method:request.method,account});
    const send=()=>{response.setHeader('Content-Type','application/json');
     if(selected==='denied'){response.writeHead(403).end(JSON.stringify({error_id:'access_denied',error:'SENSITIVE'}));return;}
     if(selected==='auth'){response.writeHead(401).end(JSON.stringify({error_id:'authentication_required',error:'SENSITIVE'}));return;}
     response.end(JSON.stringify({account_id:account,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:account},permission:'kdg_capture.capture.read.own',decision_id:randomUUID(),checked_at:new Date().toISOString()}));};
    if(selected==='hold'){heldContexts.push(send);contextArrived();}else if(selected==='delay')setTimeout(send,200);else send();return;
   }
   if(request.url==='/favicon.ico'){response.writeHead(204).end();return;}
   const staticRoot=join(proof,servingStartup?'dist-startup':'dist');const path=resolve(staticRoot,'.'+new URL(request.url,'http://local').pathname);let file=path===staticRoot?join(path,'index.html'):path;
   if(servingStartup&&path.startsWith(staticRoot+sep)&&!existsSync(file)&&!extname(file)&&request.headers.accept?.includes('text/html'))file=join(staticRoot,'index.html');
   if((!file.startsWith(staticRoot+sep))||!existsSync(file)||!statSync(file).isFile()){response.writeHead(404).end();return;}
   response.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[extname(file)]??'application/octet-stream');if(servingStartup&&extname(file)==='.html')response.setHeader('Cache-Control','private, max-age=0, must-revalidate');response.end(servingStartup&&extname(file)==='.html'?startupHtml(readFileSync(file,'utf8')):readFileSync(file));
  });
  server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});server.listen(0,'127.0.0.1');await once(server,'listening');stopped=false;
  const executable=join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell');
  browser=await chromium.launch({executablePath:executable,headless:true,ignoreDefaultArgs:['--disable-back-forward-cache']});const page=await browser.newPage({viewport:{width:390,height:844}}),origin='http://127.0.0.1:'+server.address().port;
  await page.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  page.on('pageerror',()=>issues.push({event:'page_error'}));page.on('console',message=>{if(message.type()==='error'){let path='<unknown>';try{path=new URL(message.location().url).pathname;}catch{}issues.push({event:'console_error',path});}});
  page.on('response',response=>{if(!response.ok())failedResponses.push({path:new URL(response.url()).pathname,status:response.status()});});
  await page.goto(origin);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('sdk_bootstrap_strict_react');
  assert.equal(await page.evaluate(()=>window.fixture.captureReturn('/')),true);
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'restored',path:'/'});
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});checks.push('return_same_account_fresh_context_once');
  assert.equal(await page.evaluate(()=>window.fixture.captureReturn('https://evil.invalid/')),false);
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});checks.push('return_external_target_refused');
  await page.evaluate(()=>window.fixture.captureReturn('/'));await page.evaluate(account=>window.fixture.switchAccount(account),B);
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});
  await page.evaluate(account=>window.fixture.switchAccount(account),A);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('return_different_sdk_account_safe');
  await page.evaluate(()=>window.fixture.captureReturn('/'));mode='denied';
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});mode='success';checks.push('return_current_denial_safe');
  await page.evaluate(()=>window.fixture.captureReturn('/'));mode='denied';
  assert.equal(await page.evaluate(()=>window.fixture.captureReturn('/')),false);mode='success';
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});checks.push('failed_capture_discards_prior_return');
  await page.evaluate(()=>window.fixture.captureReturn('/'));await page.evaluate(()=>window.fixture.replaceOrg('66666666-6666-4666-8666-666666666666'));
  assert.deepEqual(await page.evaluate(()=>window.fixture.restoreReturn()),{kind:'safe',path:'/'});
  await page.getByRole('heading',{name:'Could not verify access',exact:true}).waitFor();
  await page.evaluate(org=>window.fixture.replaceOrg(org),ORG);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('return_owner_org_replacement_discards_intent');
  mode='delay';const refreshed=page.evaluate(()=>window.fixture.refresh());await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();await refreshed;
  await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('sdk_token_refresh');
  mode='denied';await page.getByRole('button').click();await page.getByRole('heading',{name:'Access denied',exact:true}).waitFor();mode='success';await page.getByRole('button').click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('current_access_recheck');
  mode='auth';await page.getByRole('button').click();await page.getByRole('heading',{name:'Sign in again',exact:true}).waitFor();mode='success';await page.getByRole('button').click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.equal(await page.evaluate(()=>window.fixture.snapshot().interactive),0);checks.push('explicit_auth_refresh_before_interactive');
  await page.evaluate(async account=>{await window.fixture.switchAccount(account);},B);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.equal(requests.at(-1).account,B);checks.push('sdk_account_change');
  await page.evaluate(()=>window.fixture.online(false));await page.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();const count=requests.length;
  await page.evaluate(()=>window.fixture.refresh());await page.waitForTimeout(50);assert.equal(requests.length,count);
  await page.evaluate(()=>window.fixture.online(true));await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(requests.length>count);checks.push('offline_reconnect_rechecks');
  await page.evaluate(()=>window.fixture.logout());await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.getByRole('button').click();await page.getByRole('heading',{name:'Sign in again',exact:true}).waitFor();assert.equal(await page.evaluate(()=>window.fixture.snapshot().interactive),1);checks.push('local_logout_then_owner_launch_only');
  await page.evaluate(async account=>{await window.fixture.switchAccount(account);},A);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  mode='delay';await page.evaluate(()=>window.fixture.refresh());await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();await page.evaluate(()=>window.fixture.mount(false));await page.waitForTimeout(250);await page.getByText('Entry unmounted',{exact:true}).waitFor();
  mode='success';await page.evaluate(()=>window.fixture.mount(true));await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('unmount_and_strict_replay');
  mode='delay';await page.evaluate(()=>window.fixture.refresh());await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();
  mode='success';await page.evaluate(account=>window.fixture.replaceOwner(account),B);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  assert.deepEqual(await page.evaluate(()=>window.fixture.snapshot().oldActive),[0]);assert.equal(requests.at(-1).account,B);
  await page.evaluate(()=>window.fixture.oldRefresh());await page.waitForTimeout(250);assert.equal(requests.at(-1).account,B);checks.push('auth_owner_replacement_detaches_old');
  mode='delay';await page.evaluate(()=>window.fixture.refresh());await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();
  mode='success';await page.evaluate(()=>window.fixture.replaceOrg('66666666-6666-4666-8666-666666666666'));await page.getByRole('heading',{name:'Could not verify access',exact:true}).waitFor();await page.waitForTimeout(250);
  assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);
  await page.evaluate(org=>window.fixture.replaceOrg(org),ORG);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('configured_org_replacement_clears_admission');
  assert.deepEqual(await page.evaluate(()=>window.fixture.oauthLaunch()),{kind:'launched'});
  await page.getByText('Entry unmounted',{exact:true}).waitFor();assert.equal(await page.evaluate(()=>window.fixture.snapshot().active),0);
  assert.equal(await page.evaluate(()=>window.fixture.oauthCallback('?code=synthetic-code')),'authorized');
  await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.equal(new URL(page.url()).pathname,'/');assert.equal(new URL(page.url()).search,'');checks.push('pkce_launch_callback_scrubs_and_rechecks');
  await page.evaluate(()=>window.fixture.oauthLaunch());mode='denied';assert.equal(await page.evaluate(()=>window.fixture.oauthCallback('?code=synthetic-denied')),'access_denied');
  await page.getByText('Entry unmounted',{exact:true}).waitFor();assert.equal(new URL(page.url()).search,'');assert.equal(await page.evaluate(()=>window.fixture.snapshot().oauthPending),false);mode='success';
  await page.evaluate(()=>window.fixture.mount(true));await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('pkce_callback_current_denial_no_admission');
  const oauthChecks=await page.evaluate(()=>window.fixture.snapshot().oauthChecks);assert.deepEqual(oauthChecks,['validated_launch','scrubbed','scrubbed_before_exchange','validated_launch','scrubbed','scrubbed_before_exchange']);
  for(const query of ['?code=one&code=two','?error=access_denied&error_description=PRIVATE','#access_token=PRIVATE']){
   await page.evaluate(()=>window.fixture.oauthLaunch());const before=await page.evaluate(()=>window.fixture.snapshot().oauthChecks.filter(v=>v==='scrubbed_before_exchange').length);
   assert.equal(await page.evaluate(query=>window.fixture.oauthCallback(query),query),'invalid_callback');
   assert.equal(new URL(page.url()).search,'');assert.equal(new URL(page.url()).hash,'');assert.equal(await page.evaluate(()=>window.fixture.snapshot().oauthPending),false);
   assert.equal(await page.evaluate(()=>window.fixture.snapshot().oauthChecks.filter(v=>v==='scrubbed_before_exchange').length),before);await page.getByText('Entry unmounted',{exact:true}).waitFor();
  }checks.push('malformed_callback_scrubs_without_exchange');
  await page.evaluate(()=>window.fixture.oauthLaunch());await page.evaluate(account=>window.fixture.replaceOwner(account),A);
  assert.equal(await page.evaluate(()=>window.fixture.oauthCallback('?code=old-owner')),'invalid_callback');assert.equal(await page.evaluate(()=>window.fixture.snapshot().oauthPending),false);checks.push('pending_launch_owner_replacement_clears_attempt');
  for(const replacement of ['owner','org']){
   await page.evaluate(()=>window.fixture.oauthLaunch());await page.evaluate(()=>window.fixture.holdOAuth());const pending=page.evaluate(()=>window.fixture.oauthCallback('?code=synthetic-delayed'));
   await page.waitForFunction(()=>window.fixture.snapshot().oauthInFlight===1);
   if(replacement==='owner')await page.evaluate(account=>window.fixture.replaceOwner(account),B);else await page.evaluate(()=>window.fixture.replaceOrg('66666666-6666-4666-8666-666666666666'));
   assert.equal(await pending,'cancelled');await page.evaluate(()=>window.fixture.releaseOAuth());await page.waitForFunction(()=>window.fixture.snapshot().oauthInFlight===0);await page.waitForTimeout(30);
   await page.getByText('Entry unmounted',{exact:true}).waitFor();assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);
   if(replacement==='org')await page.evaluate(org=>window.fixture.replaceOrg(org),ORG);
   await page.evaluate(()=>window.fixture.mount(true));await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('pending_exchange_'+replacement+'_replacement_stays_closed');
  }

  assert.deepEqual(await page.evaluate(()=>[localStorage.length,sessionStorage.length]),[0,0]);assert.ok(!(await page.locator('body').textContent()).includes('SENSITIVE'));
  assert.deepEqual(failedResponses,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:401},{path:'/api/v1/context',status:403}]);assert.ok(issues.length===5&&issues.every(e=>e.event==='console_error'&&e.path==='/api/v1/context'),'unexpected_browser_error');
  const snapshot=await page.evaluate(()=>window.fixture.snapshot());assert.ok(snapshot.paths.every(path=>['/auth/v1/user','/auth/v1/token','/auth/v1/logout'].includes(path)));checks.push('synthetic_auth_fetch_no_storage_or_raw_errors');
  writeFileSync(join(proof,'sdk-browser.json'),JSON.stringify(snapshot,null,2)+'\n');
  await page.goto(origin+'/?email-code=1');await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.getByRole('button',{name:'Sign in',exact:true}).click();
  assert.equal(await page.getByLabel('Email address',{exact:true}).count(),1,'email_form_missing');
  async function emailLayout(){
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   for(const field of await page.locator('input').all())assert.ok(await field.getAttribute('id'));
   for(const button of await page.getByRole('button').all())assert.ok((await button.boundingBox()).height>=44);
  }
  await page.getByLabel('Email address',{exact:true}).focus();assert.equal(await page.getByLabel('Email address',{exact:true}).evaluate(e=>document.activeElement===e),true);
  await page.setViewportSize({width:320,height:844});await page.addStyleTag({content:'html{font-size:200%}'});await emailLayout();
  await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();await emailLayout();checks.push('email_keyboard_labels_narrow_200_percent');

  await page.getByText('If this account can sign in, a code has been sent. Check your email.',{exact:true}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Resend code',exact:true}).getAttribute('aria-disabled'),'true');assert.deepEqual(await page.evaluate(()=>window.emailFixture.snapshot().storageKeys),[]);checks.push('email_existing_account_send_no_persisted_input');
  await page.evaluate(()=>window.emailFixture.online(false));await page.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();
  await page.evaluate(()=>window.emailFixture.online(true));await page.getByLabel('One-time code',{exact:true}).waitFor({timeout:1000});
  assert.equal(await page.getByRole('button',{name:'Resend code',exact:true}).getAttribute('aria-disabled'),'true');checks.push('email_reconnect_preserves_attempt_and_cooldown');
  assert.equal(await page.getByLabel('One-time code',{exact:true}).evaluate(e=>document.activeElement===e),true);
  const beforeResend=await page.evaluate(()=>window.emailFixture.snapshot().paths.length);await page.getByRole('button',{name:'Resend code',exact:true}).focus();await page.getByRole('button',{name:'Resend code',exact:true}).press('Enter');assert.equal(await page.evaluate(()=>window.emailFixture.snapshot().paths.length),beforeResend);
  await page.getByRole('button',{name:'Use another email',exact:true}).click();await page.getByText('Please wait before requesting another code.',{exact:true}).waitFor();
  await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');assert.equal(await page.evaluate(()=>window.emailFixture.snapshot().paths.length),beforeResend);checks.push('email_restart_explains_cooldown_disabled_keyboard');
  await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();
  await page.getByLabel('One-time code',{exact:true}).fill('000000');await page.getByRole('button',{name:'Verify code',exact:true}).click();await page.getByText('That code is invalid or has expired. Try again.',{exact:true}).waitFor();
  assert.equal(await page.getByLabel('One-time code',{exact:true}).inputValue(),'');assert.equal(await page.getByLabel('One-time code',{exact:true}).evaluate(e=>document.activeElement===e),true);assert.ok(!(await page.locator('body').textContent()).includes('PRIVATE'));checks.push('email_invalid_code_safe_retry');
  await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByRole('button',{name:'Verify code',exact:true}).click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  assert.deepEqual(await page.evaluate(()=>window.emailFixture.snapshot().storageKeys),['kdg-capture-auth']);assert.ok(!page.url().includes('123456'));checks.push('email_verify_then_current_admission');
  await page.reload();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('email_persisted_session_reload_rechecks');
  mode='denied';await page.reload();await page.getByRole('heading',{name:'Access denied',exact:true}).waitFor();mode='success';await page.getByRole('button',{name:'Check access again',exact:true}).click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('email_persistence_never_caches_grants');
  await page.evaluate(()=>window.emailFixture.logout());await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();assert.deepEqual(await page.evaluate(()=>window.emailFixture.snapshot().storageKeys),[]);
  await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();checks.push('email_local_logout_removes_persisted_session');
  await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByRole('button',{name:'Send code',exact:true}).click();await page.getByLabel('One-time code',{exact:true}).waitFor();
  await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.getByRole('button',{name:'Sign in',exact:true}).click();assert.equal(await page.getByLabel('Email address',{exact:true}).inputValue(),'');checks.push('email_unfinished_entry_resets_on_reload');
  await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();checks.push('email_cancel_returns_closed_entry');
  await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByRole('button',{name:'Send code',exact:true}).click();await page.getByLabel('One-time code',{exact:true}).waitFor();
  await page.evaluate(()=>window.emailFixture.holdVerify());await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByRole('button',{name:'Verify code',exact:true}).click();await page.waitForFunction(()=>window.emailFixture.snapshot().inFlight===1);
  await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.evaluate(()=>window.emailFixture.releaseVerify());await page.waitForFunction(async()=>await window.emailFixture.session()!==null);
  await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);checks.push('email_cancel_late_sdk_session_cannot_admit');

  for(const replacement of ['org','owner']){
   await page.evaluate(()=>localStorage.removeItem('kdg-capture-auth'));await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();
   await page.evaluate(()=>window.emailFixture.holdVerify());await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.waitForFunction(()=>window.emailFixture.snapshot().inFlight===1);
   if(replacement==='owner')await page.evaluate(()=>window.emailFixture.replaceOwner());else await page.evaluate(()=>window.emailFixture.replaceOrg('66666666-6666-4666-8666-666666666666'));
   await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();
   if(replacement==='owner'){
    await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.equal(requests.at(-1).account,B);
   }
   const before=requests.length;await page.evaluate(()=>window.emailFixture.releaseVerify());await page.waitForFunction(()=>window.emailFixture.snapshot().inFlight===0);await page.waitForTimeout(50);assert.equal(requests.length,before);
   await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);if(replacement==='owner')assert.equal(await page.evaluate(()=>window.emailFixture.session()),B);
   checks.push('email_pending_'+replacement+'_replacement_blocks_old_A');
  }
  assert.ok(!(await page.locator('body').textContent()).includes('PRIVATE'));
  assert.deepEqual(failedResponses,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:401},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403}]);
  assert.ok(issues.length===6&&issues.every(e=>e.event==='console_error'&&e.path==='/api/v1/context'),'unexpected_complete_browser_error');checks.push('email_complete_journey_browser_errors_checked');
  writeFileSync(join(proof,'email-browser.json'),JSON.stringify(await page.evaluate(()=>window.emailFixture.snapshot()),null,2)+'\n');await page.screenshot({path:join(proof,'email-entry.png'),fullPage:true});

  for(const scenario of ['callback','bad-org','bad-url','bad-key','storage']){
   const before=requests.length;await page.goto(origin+'/?local-entry=1&scenario='+scenario);
   await page.getByRole('heading',{name:scenario==='callback'?'Page unavailable':'Could not open KDG Capture',exact:true}).waitFor();
   const snap=await page.evaluate(()=>window.localEntryFixture.snapshot());assert.deepEqual(snap.paths,[]);assert.equal(requests.length,before);
   if(scenario!=='storage')assert.deepEqual([snap.reads,snap.writes],[0,0]);
   assert.equal(new URL(page.url()).search,'');assert.equal(new URL(page.url()).hash,'');assert.ok(!(await page.locator('body').textContent()).includes('PRIVATE'));
  }checks.push('local_route_org_storage_preflight_no_sdk_io');
  const offlineRequests=requests.length;await page.goto(origin+'/?local-entry=1&scenario=offline');await page.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();const cold=await page.evaluate(()=>window.localEntryFixture.snapshot());assert.deepEqual([cold.reads,cold.writes,cold.paths.length],[0,0,0]);assert.equal(requests.length,offlineRequests);
  await page.evaluate(()=>{delete navigator.onLine;dispatchEvent(new Event('online'));});await page.waitForFunction(()=>window.localEntryFixture.snapshot().reads>0);checks.push('local_cold_offline_no_sdk_until_reconnect');
  await page.evaluate(()=>localStorage.removeItem('kdg-capture-auth'));await page.goto(origin+'/?local-entry=1');await page.getByRole('button',{name:'Sign in',exact:true}).waitFor({timeout:1000});checks.push('local_entry_route_mount');
  await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();await page.getByLabel('One-time code',{exact:true}).fill('123');
  const sent=await page.evaluate(()=>window.localEntryFixture.snapshot().paths.length);
  await page.context().setOffline(true);await page.evaluate(()=>window.dispatchEvent(new Event('offline')));await page.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();
  await page.context().setOffline(false);await page.evaluate(()=>window.dispatchEvent(new Event('online')));await page.getByLabel('One-time code',{exact:true}).waitFor();assert.equal(await page.getByLabel('One-time code',{exact:true}).inputValue(),'123');assert.equal(await page.getByRole('button',{name:'Resend code',exact:true}).getAttribute('aria-disabled'),'true');assert.equal(await page.evaluate(()=>window.localEntryFixture.snapshot().paths.length),sent);checks.push('local_browser_connectivity_preserves_code_and_cooldown');
  await page.getByRole('link',{name:'Skip to content',exact:true}).focus();await page.getByRole('link',{name:'Skip to content',exact:true}).press('Enter');assert.equal(new URL(page.url()).hash,'#kdg-entry-content');assert.equal(await page.getByLabel('One-time code',{exact:true}).inputValue(),'123');checks.push('local_skip_anchor_preserves_entry');
  await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  const beforeReload=requests.length;await page.reload();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(requests.length>beforeReload);checks.push('local_owner_bootstrap_reload_rechecks');
  mode='denied';await page.reload();await page.getByRole('heading',{name:'Access denied',exact:true}).waitFor();mode='success';await page.getByRole('button',{name:'Check access again',exact:true}).click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('local_current_denial_no_cached_grant');
  const heldReady=new Promise(resolve=>{contextArrived=resolve;});mode='hold';await page.getByRole('button',{name:'Check access again',exact:true}).click();await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();await heldReady;
  await page.evaluate(()=>{history.pushState(null,'','/?code=PRIVATE');dispatchEvent(new PopStateEvent('popstate'));});await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();const heldCount=requests.length;mode='success';heldContexts.splice(0).forEach(send=>send());await page.waitForTimeout(50);await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();assert.equal(requests.length,heldCount);checks.push('local_route_refuses_pending_context_response');
  await page.getByRole('link',{name:'Go to start',exact:true}).click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  await page.evaluate(()=>{history.replaceState({synthetic_step:'clean'},'','/');history.pushState({synthetic_step:'unsafe'},'','/#access_token=PRIVATE');history.pushState({synthetic_step:'skip'},'','/#kdg-entry-content');});const traversalCount=requests.length;
  await page.goBack();await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();await page.waitForTimeout(50);assert.equal(requests.length,traversalCount);assert.equal(new URL(page.url()).hash,'');const traversal=await page.evaluate(()=>window.localEntryFixture.snapshot().events);assert.ok(traversal.includes('popstate')&&traversal.includes('hashchange'));
  await page.goBack();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(requests.length>traversalCount);checks.push('local_real_history_pair_refuses_then_clean_back_rechecks');
  await page.evaluate(()=>localStorage.removeItem('kdg-capture-auth'));await page.goto(origin+'/?local-entry=1');await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();
  await page.evaluate(()=>window.localEntryFixture.hold());await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.waitForFunction(()=>window.localEntryFixture.snapshot().inFlight===1);
  await page.evaluate(()=>{history.pushState({token:'PRIVATE'},'','/auth/callback?code=PRIVATE#access_token=PRIVATE');dispatchEvent(new PopStateEvent('popstate'));});await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();
  assert.equal(new URL(page.url()).pathname,'/');assert.equal(new URL(page.url()).search,'');assert.equal(new URL(page.url()).hash,'');assert.equal(await page.evaluate(()=>history.state),null);
  const closed=requests.length;await page.evaluate(()=>window.localEntryFixture.release());await page.waitForFunction(()=>window.localEntryFixture.snapshot().inFlight===0);await page.waitForTimeout(50);
  await page.evaluate(()=>window.dispatchEvent(new Event('online')));await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();assert.equal(requests.length,closed);assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);checks.push('local_history_callback_scrubs_and_cancels_late_entry');
  await page.getByRole('link',{name:'Go to start',exact:true}).click();await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(requests.length>closed);checks.push('local_explicit_start_rechecks_late_sdk_session');
  await page.evaluate(()=>{location.hash='access_token=PRIVATE';});await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();assert.equal(new URL(page.url()).hash,'');await page.evaluate(()=>{location.hash='code=PRIVATE2';});await page.waitForFunction(()=>location.hash==='');await page.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();checks.push('local_hash_callback_refused');
  assert.equal(await page.evaluate(()=>window.localEntryFixture.snapshot().listeners),4);const beforeDispose=requests.length;await page.evaluate(()=>window.localEntryFixture.dispose());assert.equal(await page.evaluate(()=>window.localEntryFixture.snapshot().listeners),0);await page.evaluate(()=>dispatchEvent(new PopStateEvent('popstate')));assert.equal(await page.locator('#root').textContent(),'');assert.equal(requests.length,beforeDispose);checks.push('local_root_disposal_detaches_browser');
  await page.evaluate(()=>localStorage.removeItem('kdg-capture-auth'));await page.goto(origin+'/?local-entry=1');await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).waitFor();await page.evaluate(()=>window.localEntryFixture.hold());await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.waitForFunction(()=>window.localEntryFixture.snapshot().inFlight===1);
  const disposeCount=requests.length,refreshCount=await page.evaluate(()=>window.localEntryFixture.snapshot().refreshCalls.length);
  await page.evaluate(()=>{Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});dispatchEvent(new Event('offline'));Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>true});dispatchEvent(new Event('online'));window.localEntryFixture.dispose();});
  assert.deepEqual((await page.evaluate(()=>window.localEntryFixture.snapshot().refreshCalls)).slice(refreshCount),['stopAutoRefresh','startAutoRefresh','stopAutoRefresh']);assert.equal(await page.evaluate(()=>window.localEntryFixture.snapshot().listeners),0);
  await page.evaluate(()=>window.localEntryFixture.release());await page.waitForFunction(()=>window.localEntryFixture.snapshot().inFlight===0);await page.waitForTimeout(50);assert.equal(await page.locator('#root').textContent(),'');assert.equal(requests.length,disposeCount);checks.push('local_direct_pending_disposal_refresh_order');
  writeFileSync(join(proof,'local-entry-browser.json'),JSON.stringify(await page.evaluate(()=>window.localEntryFixture.snapshot()),null,2)+'\n');
  await page.goto(origin+'/?email-code=1');await page.waitForFunction(()=>!!window.emailFixture);assert.equal(await page.evaluate(()=>typeof window.localEntryFixture),'undefined');checks.push('explicit_email_selector_overrides_local_reload_fallback');await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
  assert.deepEqual(failedResponses,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:401},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403}]);assert.ok(issues.length===7&&issues.every(e=>e.event==='console_error'&&e.path==='/api/v1/context'),'unexpected_local_entry_browser_error');checks.push('complete_local_route_browser_errors_checked');


  servingStartup=true;
  const pendingChunks=new Map();let rejectedChunks=0;
  async function actualPage(scenario,routeTraffic=true){
   startupScenario=scenario;const actual=await browser.newPage({viewport:{width:390,height:844}});
   await actual.addInitScript(({scenario})=>{
    const probe={reads:0,writes:0,removes:0,ownerCalls:0,restores:[],admittedAfterRestore:0};Object.assign(window,{startupProbe:probe});
    for(const method of ['getItem','setItem','removeItem']){const original=Storage.prototype[method];Storage.prototype[method]=function(...args){probe[method==='getItem'?'reads':method==='setItem'?'writes':'removes']++;if(String(args[0]).startsWith('kdg-capture-auth'))probe.ownerCalls++;if(scenario==='storage')throw Error('PRIVATE');return original.apply(this,args);};}
    let restored=false;addEventListener('pageshow',event=>{if(event.persisted){restored=true;probe.restores.push({persisted:event.persisted,trusted:event.isTrusted,admitted:!!document.querySelector('h2')?.textContent?.includes('Setup not completed')});}});new MutationObserver(()=>{if(restored&&document.querySelector('h2')?.textContent?.includes('Setup not completed'))probe.admittedAfterRestore++;}).observe(document,{childList:true,subtree:true});
    if(scenario==='offline')Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});
   },{scenario});
   let intercepted=false;
   if(routeTraffic)await actual.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.origin===origin){
     if(url.pathname.includes('/assets/LocalEntryRoute-')&&!intercepted&&(scenario.startsWith('hold-')||scenario==='reject-import')){intercepted=true;if(scenario==='reject-import'){rejectedChunks++;return route.fulfill({status:503,contentType:'text/javascript',body:'Unavailable'});}return new Promise(resolve=>pendingChunks.set(scenario,{url:url.href,release:()=>{void route.continue().then(resolve);}}));}
     return route.continue();
    }
    if(scenario==='remote-host'&&url.origin==='http://remote.invalid'){
     if(url.pathname==='/favicon.ico')return route.fulfill({status:204});
     const base=join(proof,'dist-startup'),file=url.pathname==='/'?join(base,'index.html'):resolve(base,'.'+url.pathname);assert.ok(file.startsWith(base+sep)&&existsSync(file));
     return route.fulfill({status:200,contentType:extname(file)==='.html'?'text/html':extname(file)==='.js'?'text/javascript':'text/css',body:extname(file)==='.html'?startupHtml(readFileSync(file,'utf8')):readFileSync(file)});
    }
    throw Error('startup_external_network_refused');
   });
   if(!routeTraffic)actual.on('request',request=>assert.equal(new URL(request.url()).origin,origin,'startup_external_request_refused'));
   actual.on('pageerror',()=>issues.push({event:'page_error'}));actual.on('console',message=>{if(message.type()==='error'){let path='<unknown>';try{path=new URL(message.location().url).pathname;}catch{}issues.push({event:'console_error',path});}});actual.on('response',response=>{if(!response.ok())failedResponses.push({path:new URL(response.url()).pathname,status:response.status()});});
   return actual;
  }
  for(const scenario of ['default','missing','malformed','oversized','duplicate','wrong-type','src','extra','bad-org','remote-auth','private-key','remote-host','storage','callback','query','fragment','missing-root','duplicate-root','missing-root-callback','duplicate-root-callback','offline']){
   const actual=await actualPage(scenario),beforeAuth=startupAuthPaths.length,beforeApi=requests.length;
   const route=scenario.endsWith('callback')?'/auth/callback?code=PRIVATE#access_token=PRIVATE':scenario==='query'?'/?org_id=PRIVATE':scenario==='fragment'?'/#access_token=PRIVATE':'/';
   await actual.goto((scenario==='remote-host'?'http://remote.invalid':origin)+route);
   if(!scenario.startsWith('missing-root')&&!scenario.startsWith('duplicate-root'))await actual.getByRole('heading',{name:['callback','query','fragment'].includes(scenario)?'Page unavailable':scenario==='offline'?'Connect to the internet':'Could not open KDG Capture',exact:true}).waitFor();
   const snapshot=await actual.evaluate(()=>window.startupProbe);if(scenario!=='storage')assert.deepEqual(snapshot,{reads:0,writes:0,removes:0,ownerCalls:0,restores:[],admittedAfterRestore:0});assert.equal(startupAuthPaths.length,beforeAuth);assert.equal(requests.length,beforeApi);
   if(scenario.endsWith('callback')||['query','fragment'].includes(scenario)){assert.equal(new URL(actual.url()).pathname,'/');assert.equal(new URL(actual.url()).search,'');assert.equal(new URL(actual.url()).hash,'');}
   assert.ok(!(await actual.locator('body').innerText()).includes('PRIVATE'));
   if(scenario==='offline'){await actual.evaluate(()=>{delete navigator.onLine;dispatchEvent(new Event('online'));});await actual.getByRole('button',{name:'Sign in',exact:true}).waitFor();assert.ok((await actual.evaluate(()=>window.startupProbe)).reads>0);}
   await actual.close();
  }checks.push('actual_startup_invalid_config_origin_route_zero_io','actual_startup_cold_offline_reconnect','actual_startup_unconfigured_closed');
  const actual=await actualPage('valid',false);await actual.goto(origin);await actual.getByRole('button',{name:'Sign in',exact:true}).click();await actual.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await actual.getByLabel('Email address',{exact:true}).press('Enter');await actual.getByLabel('One-time code',{exact:true}).waitFor();await actual.getByLabel('One-time code',{exact:true}).fill('123456');await actual.getByLabel('One-time code',{exact:true}).press('Enter');await actual.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.deepEqual(startupAuthPaths,['/auth/v1/otp','/auth/v1/verify']);checks.push('actual_index_main_config_sdk_http_sign_in');
  const beforeActualReload=requests.length;await actual.reload();await actual.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(requests.length>beforeActualReload);checks.push('actual_startup_reload_fresh_context');
  mode='denied';await actual.reload();await actual.getByRole('heading',{name:'Access denied',exact:true}).waitFor();mode='success';await actual.getByRole('button',{name:'Check access again',exact:true}).click();await actual.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();checks.push('actual_startup_current_denial');
  const cdp=await actual.context().newCDPSession(actual);await cdp.send('Page.enable');cdp.on('Page.backForwardCacheNotUsed',event=>writeFileSync(join(proof,'bfcache-diagnostic.json'),JSON.stringify(event,null,2)));await actual.goto(origin+'/__parked');await actual.getByRole('heading',{name:'Paused',exact:true}).waitFor();mode='denied';const beforeRestore=requests.length;await actual.goBack();await actual.getByRole('heading',{name:'Access denied',exact:true}).waitFor();assert.ok(requests.length>beforeRestore);const restored=await actual.evaluate(()=>window.startupProbe);writeFileSync(join(proof,'restore-diagnostic.json'),JSON.stringify(await actual.evaluate(()=>performance.getEntriesByType('navigation').map(x=>x.toJSON())),null,2));assert.deepEqual(restored.restores,[]);const cacheDiagnostic=JSON.parse(readFileSync(join(proof,'bfcache-diagnostic.json')));assert.ok(cacheDiagnostic.notRestoredExplanations.some(item=>item.reason==='BackForwardCacheDisabledForDelegate'));checks.push('actual_back_reload_current_denial_cache_unavailable');
  mode='success';await actual.getByRole('button',{name:'Check access again',exact:true}).click();await actual.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();mode='denied';const beforePersisted=requests.length;
  await actual.evaluate(()=>{dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}));if(document.querySelector('#root').textContent!=='')throw Error('old_admission_retained');dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));});await actual.getByRole('heading',{name:'Access denied',exact:true}).waitFor();assert.ok(requests.length>beforePersisted);const simulated=await actual.evaluate(()=>window.startupProbe);assert.deepEqual(simulated.restores,[{persisted:true,trusted:false,admitted:false}]);assert.equal(simulated.admittedAfterRestore,0);mode='success';checks.push('simulated_persisted_restore_current_denial_no_old_admission');
  await actual.screenshot({path:join(proof,'actual-startup.png'),fullPage:true});writeFileSync(join(proof,'actual-startup-browser.json'),JSON.stringify({auth_paths:startupAuthPaths,storage:await actual.evaluate(()=>window.startupProbe)},null,2)+'\n');await actual.close();
  async function waitChunk(scenario){for(let i=0;i<300&&!pendingChunks.has(scenario);i++)await new Promise(resolve=>setTimeout(resolve,10));assert.ok(pendingChunks.has(scenario),'lazy_chunk_not_held');}
  for(const scenario of ['hold-dispose','hold-offline','hold-route','reject-import']){
   const loading=await actualPage(scenario),beforeAuth=startupAuthPaths.length,beforeApi=requests.length;await loading.goto(origin,{waitUntil:'domcontentloaded'});
   if(scenario==='reject-import'){
    await loading.getByRole('heading',{name:'Could not open KDG Capture',exact:true}).waitFor();assert.equal((await loading.evaluate(()=>window.startupProbe)).ownerCalls,0);await loading.evaluate(()=>dispatchEvent(new PageTransitionEvent('pagehide')));assert.equal(await loading.locator('#root').textContent(),'');
   }else{
    await waitChunk(scenario);
    if(scenario==='hold-dispose')await loading.evaluate(()=>dispatchEvent(new PageTransitionEvent('pagehide')));
    if(scenario==='hold-offline')await loading.evaluate(()=>{Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});dispatchEvent(new Event('offline'));});
    if(scenario==='hold-route')await loading.evaluate(()=>{history.pushState(null,'','/auth/callback?code=PRIVATE#access_token=PRIVATE');dispatchEvent(new PopStateEvent('popstate'));});
    const chunk=pendingChunks.get(scenario);chunk.release();await loading.evaluate(async url=>{await import(url);await new Promise(resolve=>setTimeout(resolve,0));},chunk.url);assert.equal((await loading.evaluate(()=>window.startupProbe)).ownerCalls,0);
    if(scenario==='hold-dispose')assert.equal(await loading.locator('#root').textContent(),'');
    if(scenario==='hold-offline'){await loading.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();await loading.evaluate(()=>{delete navigator.onLine;dispatchEvent(new Event('online'));});await loading.getByRole('button',{name:'Sign in',exact:true}).waitFor();}
    if(scenario==='hold-route'){await loading.getByRole('heading',{name:'Page unavailable',exact:true}).waitFor();assert.equal(new URL(loading.url()).search,'');assert.equal(new URL(loading.url()).hash,'');await loading.getByRole('link',{name:'Go to start',exact:true}).click();await loading.getByRole('button',{name:'Sign in',exact:true}).waitFor();}
   }
   assert.equal(startupAuthPaths.length,beforeAuth);assert.equal(requests.length,beforeApi);await loading.close();
  }checks.push('actual_pending_import_disposal_no_owner','actual_pending_import_offline_and_route_recovery','actual_import_rejection_safe_disposal');
  assert.ok(issues.filter(e=>e.path==='/api/v1/context').length===10&&issues.filter(e=>e.path!=='/api/v1/context').length===rejectedChunks&&issues.every(e=>e.event==='console_error'&&(e.path==='/api/v1/context'||e.path.startsWith('/assets/LocalEntryRoute-'))),'unexpected_complete_actual_startup_error');assert.equal(failedResponses.length,10+rejectedChunks);assert.ok(failedResponses.filter(e=>e.path!=='/api/v1/context').every(e=>e.status===503&&e.path.startsWith('/assets/LocalEntryRoute-')));checks.push('complete_actual_startup_errors_checked');

await page.screenshot({path:join(proof,'auth-entry.png'),fullPage:true});
 }
 passed=true;
}finally{
 try{if(browser)await browser.close();}finally{if(server){const closed=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await closed;stopped=!server.listening;}}
 const unchanged=sources.every(path=>hash(readFileSync(join(root,path)))===captured[path]);
 const result={passed:passed&&unchanged,selected_mode,selected_test_files,test_counts,requested_flags:process.argv.slice(2),checks,source_sha256:captured,source_unchanged:unchanged,server_stopped:stopped,requests,issues,failed_responses:failedResponses,node:process.version,typescript:'7.0.2',sdk:'2.117.3',proof,limitations:['synthetic SDK/Auth data; no real provider/account/access','skipLibCheck for known upstream WebAuthn declaration incompatibility; own source strict']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');if(!result.passed)process.exitCode=1;process.stdout.write(JSON.stringify({passed:result.passed,proof})+'\n');
}
