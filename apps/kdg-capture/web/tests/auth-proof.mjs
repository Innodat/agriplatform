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
const sources=[owner+'/.generated-files.json',owner+'/src/auth/lifecycle.ts',owner+'/src/auth/use-lifecycle.ts',owner+'/scripts/test-auth-lifecycle.mjs',owner+'/src/auth-entry.ts',owner+'/src/AuthEntry.tsx',owner+'/src/EntryScreen.tsx',owner+'/src/entry-screen.css',owner+'/src/styles.d.ts',owner+'/tests/auth-fixture/main.tsx',owner+'/tests/auth-fixture/index.html',owner+'/src/entry.ts',owner+'/package.json',owner+'/tsconfig.auth.json',owner+'/tests/auth-entry.test.mjs',owner+'/tests/auth-proof.mjs','apps/kdg-capture/contracts/generated/types.gen.ts'];
const captured=Object.fromEntries(sources.map(path=>{const data=readFileSync(join(root,path)),destination=join(capsule,path);mkdirSync(resolve(destination,'..'),{recursive:true});writeFileSync(destination,data);return[path,hash(data)];}));
let passed=false,browser,server;const sockets=new Set(),checks=[],requests=[],issues=[],failedResponses=[];let stopped=true;
try{
 const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,owner,'tsconfig.auth.json'),'--noEmit','false','--rootDir',join(capsule,'apps/kdg-capture'),'--outDir',join(capsule,'compiled')],{encoding:'utf8',timeout:30000});
 writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.equal(types.status,0,'types_failed');checks.push('strict_ts7_own_source');
 const invalid=join(capsule,'invalid-own-source.ts');writeFileSync(invalid,'const invalid: string = 17;\n');
 const negativeConfig=join(capsule,'negative-types.json');writeFileSync(negativeConfig,JSON.stringify({extends:join(capsule,owner,'tsconfig.auth.json'),files:[invalid]}));
 const negative=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',negativeConfig,'--noEmit'],{encoding:'utf8',timeout:30000});
 writeFileSync(join(proof,'types-negative.log'),negative.stdout+negative.stderr);assert.ok(negative.status!==0&&negative.stdout.includes('TS2322'),'own_source_negative_control_failed');checks.push('strict_own_source_negative_control');
 const args=['--test'];if(process.argv.includes('--acceptance-only'))args.push('--test-name-pattern','current SDK session admits');args.push(join(capsule,owner,'tests/auth-entry.test.mjs'),join(capsule,owner,'scripts/test-auth-lifecycle.mjs'));
 const unit=spawnSync(process.execPath,args,{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'unit.log'),unit.stdout+unit.stderr);assert.equal(unit.status,0,'unit_failed');checks.push('sdk_session_tests');
 if(!process.argv.includes('--unit-only')&&!process.argv.includes('--acceptance-only')){
  const scaffold=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root');
  const modules=join(scaffold,'apps/bootstrap-application/web/node_modules');
  for(const [name,version] of [['vite','8.3.4'],['@vitejs/plugin-react','6.1.2']])assert.equal(JSON.parse(readFileSync(join(modules,name,'package.json'))).version,version);
  const config={configFile:false,tsconfig:join(capsule,owner,'tsconfig.auth.json'),root:join(capsule,owner,'tests/auth-fixture'),logLevel:'warn',build:{outDir:join(proof,'dist'),emptyOutDir:false}};
  writeFileSync(join(proof,'build.mjs'),`import {build} from ${JSON.stringify(pathToFileURL(join(modules,'vite/dist/node/index.js')).href)};import react from ${JSON.stringify(pathToFileURL(join(modules,'@vitejs/plugin-react/dist/index.js')).href)};await build({...${JSON.stringify(config)},plugins:[react()]});`);
  const built=spawnSync(process.execPath,[join(proof,'build.mjs')],{cwd:config.root,encoding:'utf8',timeout:30000});writeFileSync(join(proof,'build.log'),built.stdout+built.stderr);assert.equal(built.status,0,'vite_build_failed');checks.push('vite8_react19');
  const require=createRequire(join(scaffold,'package.json'));assert.equal(require('@playwright/test/package.json').version,'1.64.0');const {chromium}=require('@playwright/test');
  const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';let mode='success';
  server=createServer((request,response)=>{
   response.setHeader('Cache-Control','private, no-store');
   if(request.url==='/api/v1/context'){
    assert.equal(request.method,'GET');assert.equal(request.headers['x-service-key'],undefined);
    const payload=JSON.parse(Buffer.from(request.headers.authorization.split('.')[1],'base64url').toString());const account=payload.sub,selected=mode;
    requests.push({path:request.url,method:request.method,account});
    const send=()=>{response.setHeader('Content-Type','application/json');
     if(selected==='denied'){response.writeHead(403).end(JSON.stringify({error_id:'access_denied',error:'SENSITIVE'}));return;}
     if(selected==='auth'){response.writeHead(401).end(JSON.stringify({error_id:'authentication_required',error:'SENSITIVE'}));return;}
     response.end(JSON.stringify({account_id:account,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:account},permission:'kdg_capture.capture.read.own',decision_id:randomUUID(),checked_at:new Date().toISOString()}));};
    if(selected==='delay')setTimeout(send,200);else send();return;
   }
   if(request.url==='/favicon.ico'){response.writeHead(204).end();return;}
   const path=resolve(proof,'dist','.'+new URL(request.url,'http://local').pathname),file=path===join(proof,'dist')?join(path,'index.html'):path;
   if((!file.startsWith(join(proof,'dist')+sep))||!existsSync(file)||!statSync(file).isFile()){response.writeHead(404).end();return;}
   response.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[extname(file)]??'application/octet-stream');response.end(readFileSync(file));
  });
  server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});server.listen(0,'127.0.0.1');await once(server,'listening');stopped=false;
  const executable=join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell');
  browser=await chromium.launch({executablePath:executable,headless:true});const page=await browser.newPage({viewport:{width:390,height:844}}),origin='http://127.0.0.1:'+server.address().port;
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
  assert.deepEqual(await page.evaluate(()=>[localStorage.length,sessionStorage.length]),[0,0]);assert.ok(!(await page.locator('body').textContent()).includes('SENSITIVE'));
  assert.deepEqual(failedResponses,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:401}]);assert.ok(issues.length===4&&issues.every(e=>e.event==='console_error'&&e.path==='/api/v1/context'),'unexpected_browser_error');
  const snapshot=await page.evaluate(()=>window.fixture.snapshot());assert.ok(snapshot.paths.every(path=>['/auth/v1/user','/auth/v1/token','/auth/v1/logout'].includes(path)));checks.push('synthetic_auth_fetch_no_storage_or_raw_errors');
  writeFileSync(join(proof,'sdk-browser.json'),JSON.stringify(snapshot,null,2)+'\n');await page.screenshot({path:join(proof,'auth-entry.png'),fullPage:true});
 }
 passed=true;
}finally{
 try{if(browser)await browser.close();}finally{if(server){const closed=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await closed;stopped=!server.listening;}}
 const unchanged=sources.every(path=>hash(readFileSync(join(root,path)))===captured[path]);
 const result={passed:passed&&unchanged,checks,source_sha256:captured,source_unchanged:unchanged,server_stopped:stopped,requests,issues,failed_responses:failedResponses,node:process.version,typescript:'7.0.2',sdk:'2.117.3',proof,limitations:['synthetic SDK/Auth data; no real provider/account/access','skipLibCheck for known upstream WebAuthn declaration incompatibility; own source strict']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');if(!result.passed)process.exitCode=1;process.stdout.write(JSON.stringify({passed:result.passed,proof})+'\n');
}
