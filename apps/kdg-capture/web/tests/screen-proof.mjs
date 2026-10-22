// Built React screen + actual current-context boundary; synthetic Auth/API only.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createRequire} from 'node:module';
import {readFileSync,mkdirSync,writeFileSync,symlinkSync,existsSync,statSync} from 'node:fs';
import {resolve,join,sep,extname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
const root=process.cwd(),hash=value=>createHash('sha256').update(value).digest('hex');
const retained=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root');
const require=createRequire(join(retained,'package.json'));
assert.equal(process.version,'v26.11.1');
for(const [name,version] of [['react','19.3.0'],['react-dom','19.3.0'],['@types/react','19.3.0'],['@types/react-dom','19.3.0'],['typescript','7.0.2'],['@playwright/test','1.64.0']])assert.equal(require(name+'/package.json').version,version);
const localModules=join(retained,'apps/bootstrap-application/web/node_modules');
for(const [name,version] of [['vite','8.3.4'],['@vitejs/plugin-react','6.1.2']])assert.equal(JSON.parse(readFileSync(join(localModules,name,'package.json'))).version,version);
const {chromium}=require('@playwright/test');
const executable=join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell');
const directory=join(root,'platform/deployment/.local/kdg-entry-screen-20261022');mkdirSync(directory,{recursive:true,mode:0o700});
const proof=join(directory,'screen-'+randomUUID());mkdirSync(proof,{mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),JSON.stringify({private:true,type:'module'}));symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
const owner='apps/kdg-capture/web';
const sources=[owner+'/src/EntryScreen.tsx',owner+'/src/styles.d.ts',owner+'/src/entry-screen.css',owner+'/src/entry.ts',owner+'/package.json',
 owner+'/tsconfig.json',owner+'/tsconfig.screen.json',owner+'/tests/screen-proof.mjs',owner+'/tests/screen.test.mjs',
 owner+'/tests/screen-fixture/main.tsx',owner+'/tests/screen-fixture/index.html','apps/kdg-capture/contracts/generated/types.gen.ts'];
const captured=Object.fromEntries(sources.map(path=>{
 const data=readFileSync(join(root,path)),destination=join(capsule,path);mkdirSync(resolve(destination,'..'),{recursive:true});writeFileSync(destination,data);return[path,hash(data)];
}));
const checks=[],issues=[],failedResponses=[],requests=[],measurements={};let browser,server,passed=false;
const sockets=new Set();let stopped=false;
try {
 const compiler=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,owner,'tsconfig.screen.json'),
  '--noEmit','false','--rootDir',join(capsule,'apps/kdg-capture'),'--outDir',join(capsule,'compiled')],{encoding:'utf8',timeout:30000});
 writeFileSync(join(proof,'type-check.log'),compiler.stdout+compiler.stderr);assert.equal(compiler.status,0,'type_check_failed');checks.push('strict_ts7');
 if(process.argv.includes('--unit-only')){
  const unit=spawnSync(process.execPath,['--test',join(capsule,owner,'tests/screen.test.mjs')],{encoding:'utf8',timeout:30000});
  writeFileSync(join(proof,'unit.log'),unit.stdout+unit.stderr);assert.equal(unit.status,0,'unit_failed');checks.push('presentation_unit');passed=true;
 }else{
  const config={configFile:false,tsconfig:join(capsule,owner,'tsconfig.screen.json'),root:join(capsule,owner,'tests/screen-fixture'),logLevel:'warn',build:{outDir:join(proof,'dist'),emptyOutDir:false}};
  const buildSource=`import {build} from ${JSON.stringify(pathToFileURL(join(localModules,'vite/dist/node/index.js')).href)};import react from ${JSON.stringify(pathToFileURL(join(localModules,'@vitejs/plugin-react/dist/index.js')).href)};await build({...${JSON.stringify(config)},plugins:[react()]});`;
  writeFileSync(join(proof,'build.mjs'),buildSource);
  const built=spawnSync(process.execPath,[join(proof,'build.mjs')],{cwd:join(capsule,owner,'tests/screen-fixture'),encoding:'utf8',timeout:30000});
  writeFileSync(join(proof,'build.log'),built.stdout+built.stderr);assert.equal(built.status,0,'vite_build_failed');checks.push('vite8_build');
  const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';
  let mode='success';
  server=createServer((request,response)=>{
   response.setHeader('Cache-Control','private, no-store');
   if(request.url==='/api/v1/context'){
    requests.push({path:request.url,method:request.method,service_key_present:request.headers['x-service-key']!==undefined});
    const account=request.headers.authorization==='Bearer synthetic-'+B?B:A,selected=mode;
    const send=()=>{
     response.setHeader('Content-Type','application/json');
     const failure={denied:[403,'access_denied'],outage:[503,'authorization_unavailable'],actor:[409,'identity.actor_setup_required'],auth:[401,'authentication_required'] }[selected];
     if(failure){response.writeHead(failure[0]).end(JSON.stringify({error_id:failure[1],error:'SENSITIVE'}));return;}
     if(selected==='invalid'){response.end(JSON.stringify({secret:'SENSITIVE'}));return;}
     response.end(JSON.stringify({account_id:account,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'1',permission:'kdg_capture.capture.read.own',
      authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:account},decision_id:randomUUID(),checked_at:new Date().toISOString()}));
    };
    if(selected==='delay')setTimeout(send,200);else send();return;
   }
   if(request.url==='/favicon.ico'){response.writeHead(204).end();return;}
   const path=resolve(proof,'dist','.'+new URL(request.url,'http://local').pathname);
   if(!path.startsWith(join(proof,'dist')+sep)&&path!==join(proof,'dist')){response.writeHead(404).end();return;}
   const file=path===join(proof,'dist')?join(path,'index.html'):path;
   if(!existsSync(file)||!statSync(file).isFile()){response.writeHead(404).end();return;}
   response.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[extname(file)]??'application/octet-stream');response.end(readFileSync(file));
  });
  server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});server.listen(0,'127.0.0.1');await once(server,'listening');
  browser=await chromium.launch({executablePath:executable,headless:true});const page=await browser.newPage({viewport:{width:390,height:844}});
  const origin='http://127.0.0.1:'+server.address().port;
  await page.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  page.on('pageerror',()=>issues.push({event:'page_error'}));
  page.on('console',message=>{if(message.type()==='error'){let path='<unknown>';try{path=new URL(message.location().url).pathname;}catch{}issues.push({event:'console_error',path});}});
  page.on('response',response=>{if(!response.ok())failedResponses.push({path:new URL(response.url()).pathname,status:response.status()});});
  await page.goto(origin);await page.waitForFunction(()=>Boolean(window.fixture));
  // Outer behavior first: an admitted account sees honest incomplete setup, not sign-in.
  await page.evaluate(async account=>{await window.fixture.check(account);},A);
  await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor({timeout:3000});
  assert.equal(await page.getByRole('heading',{name:'KDG Capture',exact:true}).count(),1);
  await page.getByText('Khula Development Group',{exact:true}).waitFor();
  checks.push('KDG-A01.entry-allowed.presentation');
  if(!process.argv.includes('--acceptance-only')){
   await page.evaluate(()=>window.fixture.clear());
   const action=page.getByRole('button');await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();
   mode='delay';const requestStarted=once(server,'request');await action.focus();await page.keyboard.press('Enter');await requestStarted;
   await page.getByRole('heading',{name:'Checking access',exact:true}).waitFor();assert.equal(await action.isDisabled(),true);
   assert.equal(await page.getByRole('status').evaluate(el=>el.closest('[aria-busy="true"]')===null),true,'checking status must not defer its own live announcement');
   assert.equal(await action.evaluate(el=>el===document.activeElement),true);
   const checkingBefore=await page.evaluate(()=>window.fixture.snapshot()),checkingRequests=requests.length;
   await page.keyboard.press('Enter');assert.deepEqual(await page.evaluate(()=>window.fixture.snapshot()),checkingBefore);assert.equal(requests.length,checkingRequests);
   await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.equal(await action.evaluate(el=>el===document.activeElement),true);
   assert.equal(await page.evaluate(()=>window.fixture.snapshot().signIns),1);checks.push('keyboard_sign_in_checking_focus');
   mode='denied';await action.click();await page.getByRole('heading',{name:'Access denied',exact:true}).waitFor();checks.push('KDG-A01.entry-denied.presentation');
   mode='outage';await action.click();await page.getByRole('heading',{name:'Could not check access',exact:true}).waitFor();assert.equal(await action.textContent(),'Retry');
   const before=await page.evaluate(()=>window.fixture.snapshot().retries);await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>window.fixture.snapshot().retries),before);checks.push('unavailable_explicit_retry');
   mode='actor';await action.click();await page.getByRole('heading',{name:'Account setup not completed',exact:true}).waitFor();
   mode='invalid';await action.click();await page.getByRole('heading',{name:'Could not verify access',exact:true}).waitFor();
   mode='auth';await action.click();await page.getByRole('heading',{name:'Sign in again',exact:true}).waitFor();checks.push('actor_invalid_auth_distinct');
   mode='success';await page.evaluate(async account=>{await window.fixture.check(account);},B);await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();
   await page.evaluate(()=>window.fixture.online(false));await page.getByRole('heading',{name:'Connect to the internet',exact:true}).waitFor();assert.equal(await action.isDisabled(),true);
   const offlineBefore=await page.evaluate(()=>window.fixture.snapshot()),offlineRequests=requests.length;await action.focus();await page.keyboard.press('Enter');assert.deepEqual(await page.evaluate(()=>window.fixture.snapshot()),offlineBefore);assert.equal(requests.length,offlineRequests);
   assert.equal(await page.getByRole('heading',{name:'Setup not completed',exact:true}).count(),0);checks.push('offline_masks_admission');
   await page.evaluate(()=>{window.fixture.clear();window.fixture.online(true);});await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();
   mode='delay';await action.click();await page.evaluate(()=>window.fixture.clear());await page.waitForTimeout(250);
   await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();checks.push('logout_blocks_late_view');
   await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.keyboard.press('Tab');
   assert.equal(await page.getByRole('link',{name:'Skip to content'}).evaluate(el=>el===document.activeElement),true);
   await page.keyboard.press('Enter');assert.equal(await page.locator('main').evaluate(el=>el===document.activeElement),true);
   await page.keyboard.press('Tab');assert.equal(await action.evaluate(el=>el===document.activeElement),true);
   const style=await action.evaluate(el=>({height:el.getBoundingClientRect().height,outline:getComputedStyle(el).outlineStyle}));assert.ok(style.height>=48);assert.notEqual(style.outline,'none');
   assert.equal(await page.getByRole('status').getAttribute('aria-live'),'polite');
   measurements.contrast=await page.evaluate(()=>{
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d');
    const light=color=>{ctx.fillStyle=color;ctx.fillRect(0,0,1,1);const rgb=[...ctx.getImageData(0,0,1,1).data].slice(0,3).map(v=>v/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);return rgb[0]*0.2126+rgb[1]*0.7152+rgb[2]*0.0722;};
    const ratio=(a,b)=>{const x=light(a),y=light(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05);};
    const surface=getComputedStyle(document.querySelector('.kdg-entry')),button=getComputedStyle(document.querySelector('button'));
    return {body:ratio(surface.color,surface.backgroundColor),button:ratio(button.color,button.backgroundColor),control:ratio(button.backgroundColor,surface.backgroundColor),focus:ratio(button.outlineColor,surface.backgroundColor)};
   });
   assert.ok(measurements.contrast.body>=4.5&&measurements.contrast.button>=4.5&&measurements.contrast.control>=3&&measurements.contrast.focus>=3);checks.push('measured_contrast');
   for(const width of [320,1280]){
    await page.setViewportSize({width,height:800});await page.evaluate(()=>document.documentElement.style.fontSize='200%');
    for(const [selected,title] of [['success','Setup not completed'],['actor','Account setup not completed'],['outage','Could not check access'],['denied','Access denied'],['offline','Connect to the internet']]){
     if(selected==='offline')await page.evaluate(()=>window.fixture.online(false));
     else{mode=selected;await page.evaluate(async account=>{await window.fixture.check(account);},B);}
     await page.getByRole('heading',{name:title,exact:true}).waitFor();
     assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),selected+' overflows');
     const box=await action.boundingBox();assert.ok(box.width>=48&&box.height>=48);
     await page.screenshot({path:join(proof,`entry-${width}-${selected}-200percent.png`),fullPage:true});
    }
    await page.evaluate(()=>window.fixture.online(true));
   }
   checks.push('KDG-A19.entry-accessible.fixture');
   assert.deepEqual(await page.evaluate(()=>[localStorage.length,sessionStorage.length]),[0,0]);
   assert.ok(!(await page.locator('body').textContent()).includes('SENSITIVE'));
   assert.ok(requests.every(r=>r.method==='GET'&&r.path==='/api/v1/context'&&!r.service_key_present));
   assert.deepEqual(failedResponses.map(r=>r.status),[403,503,409,401,409,503,403,409,503,403]);
   assert.ok(issues.length===10&&issues.every(i=>i.event==='console_error'&&i.path==='/api/v1/context'),'unexpected_browser_errors');
   checks.push('safe_requests_no_storage');
   const unit=spawnSync(process.execPath,['--test',join(capsule,owner,'tests/screen.test.mjs')],{encoding:'utf8',timeout:30000});
   writeFileSync(join(proof,'unit.log'),unit.stdout+unit.stderr);assert.equal(unit.status,0,'unit_failed');checks.push('presentation_unit');
  }
  passed=true;
 }
}finally{
 try{if(browser)await browser.close();}finally{
  if(server){const closed=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await closed;stopped=!server.listening;}else stopped=true;
  const unchanged=sources.every(path=>hash(readFileSync(join(root,path)))===captured[path]);
  const result={passed:passed&&unchanged,checks,measurements,source_sha256:captured,source_unchanged:unchanged,server_stopped:stopped,requests,issues,failed_responses:failedResponses,
   node:process.version,typescript:'7.0.2',react:'19.3.0',vite:'8.3.4',playwright:'1.64.0',chromium_sha256:hash(readFileSync(executable)),proof,
   limitations:['synthetic Auth sessions and HTTP API; not provider/currentSQL proof','keyboard/DOM/responsive fixture, not screen-reader or installed-device qualification']};
  writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');if(!result.passed)process.exitCode=1;process.stdout.write(JSON.stringify({passed:result.passed,proof})+'\n');
 }
}
