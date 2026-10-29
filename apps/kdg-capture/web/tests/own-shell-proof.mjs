/** Actual index/main production build + real Chromium service-worker/cache proof. */
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync,existsSync,statSync} from 'node:fs';
import {join,resolve,sep,extname} from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {randomUUID,createHash} from 'node:crypto';
import {createLocalShellServer} from '../scripts/serve-local-shell.mjs';
const root=process.cwd(),owner='apps/kdg-capture/web';
const pinned=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules');
const viteModules=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/apps/bootstrap-application/web/node_modules');
const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));
assert.equal(process.version,'v26.11.1');assert.equal(JSON.parse(readFileSync(join(pinned,'typescript/package.json'))).version,'7.0.2');
assert.equal(JSON.parse(readFileSync(join(viteModules,'vite/package.json'))).version,'8.3.4');
const {chromium}=require('@playwright/test');
const proof=join(root,'platform/deployment/.local/kdg-own-shell-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{}');symlinkSync(pinned,join(capsule,'node_modules'),'dir');
// Enumerate only selected web/contract roots. Never traverse or copy the application tree.
const enumerated=spawnSync('rg',['--files',owner+'/src',owner+'/offline-tools',owner+'/local-host-tools','apps/kdg-capture/contracts'],{cwd:root,encoding:'utf8'});assert.equal(enumerated.status,0);
const sources=[...enumerated.stdout.trim().split('\n'),owner+'/index.html',owner+'/package.json',owner+'/tsconfig.auth.json',owner+'/shell-build.config.ts',owner+'/scripts/own-shell-build.mjs',owner+'/scripts/serve-local-shell.mjs',owner+'/local-api-routes.mjs',owner+'/tests/own-shell-proof.mjs'];
const sha=value=>createHash('sha256').update(value).digest('hex');
const captured={};for(const path of sources){const data=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(resolve(dest,'..'),{recursive:true});writeFileSync(dest,data);captured[path]=sha(data);}
// Resolve build-only packages without touching installed application dependencies.
const web=join(capsule,owner);mkdirSync(join(web,'node_modules'));for(const name of ['vite','@vitejs/plugin-react']){const dest=join(web,'node_modules',name);mkdirSync(resolve(dest,'..'),{recursive:true});symlinkSync(join(viteModules,name),dest,'dir');}
const buildOnly=process.argv.includes('--build-only'),config=buildOnly?process.env.KDG_LOCAL_WEB_CONFIG:join(proof,'public.json');
assert.ok(config&&config.startsWith('/'),'build-only requires explicit absolute KDG_LOCAL_WEB_CONFIG');if(!buildOnly)writeFileSync(config,JSON.stringify({schema_version:1,environment_kind:'ci_disposable',org_id:'33333333-3333-4333-8333-333333333333',auth_url:'http://127.0.0.1:59699',auth_public_key:'sb_publishable_synthetic_shell_only',api_origin:'http://127.0.0.1:59698'}));
const buildScript=join(proof,'build.mjs');writeFileSync(buildScript,`import {build} from ${JSON.stringify(pathToFileURL(join(viteModules,'vite/dist/node/index.js')).href)};await build({configFile:${JSON.stringify(join(web,'shell-build.config.ts'))},build:{outDir:process.argv[2],emptyOutDir:false},logLevel:'warn'});`);
const checks=[],sockets=new Set();let browser,server,upstream,passed=false,selectedDist;
function build(label){const dist=join(proof,label),result=spawnSync(process.execPath,[buildScript,dist],{cwd:web,env:{...process.env,KDG_LOCAL_WEB_CONFIG:config},encoding:'utf8',timeout:60000});writeFileSync(join(proof,label+'.log'),result.stdout+result.stderr);assert.equal(result.status,0,'actual_build_failed: '+result.stderr);return dist;}
if(buildOnly){const dist=build('dist1');const result={passed:true,checks:['actual_index_main_vite8_build'],source_sha256:captured,proof,dist};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify({passed:true,proof,dist})+'\n');process.exit(0);}
try{
 selectedDist=build('dist1');checks.push('actual_index_main_vite8_build');
 const typeconfig=join(proof,'tsconfig.shell.json');writeFileSync(typeconfig,JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',lib:['ES2022','DOM'],types:[],skipLibCheck:true,rootDir:join(capsule,owner,'src'),outDir:join(proof,'compiled')},files:[join(capsule,owner,'src/own-shell.ts')]}));
 const typed=spawnSync(process.execPath,[join(pinned,'typescript/bin/tsc'),'--project',typeconfig],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'type-check.log'),typed.stdout+typed.stderr);assert.equal(typed.status,0,'strict_shell_types_failed: '+typed.stdout+typed.stderr);checks.push('strict_shell_ts7');
 const module=readFileSync(join(proof,'compiled/own-shell.js'),'utf8');
 const importShell=page=>page.evaluate(async code=>{window.shell=await import('data:text/javascript;base64,'+btoa(code));},module);
 upstream=createServer((req,res)=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify({business:'must-never-cache'}));});upstream.listen(0,'127.0.0.1');await once(upstream,'listening');
 const configData=JSON.parse(readFileSync(config));configData.api_origin='http://127.0.0.1:'+upstream.address().port;writeFileSync(config,JSON.stringify(configData));
 const startStatic=async(dist,port=0)=>{const host=createLocalShellServer({dist,configFile:config});host.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});host.listen(port,'127.0.0.1');await once(host,'listening');return host;};
 server=await startStatic(selectedDist);
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({headless:true,executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell')});
 const context=await browser.newContext(),page=await context.newPage();
 await page.goto(origin);await importShell(page);assert.equal(await page.evaluate(()=>window.shell.prepareOwnShell()),true);
 await page.waitForFunction(()=>Boolean(navigator.serviceWorker.controller));
 const firstState=await page.evaluate(()=>window.shell.shellState());assert.equal(firstState.ready,true);checks.push('confirmed_complete_active_shell_cache');
 // Only public emitted resources may be retained, despite successful protected network reads.
 await page.evaluate(async()=>{for(const path of ['/api/v1/context','/auth/v1/user','/provider/callback'])await fetch(path);});
 const entries=await page.evaluate(async()=>{const all=[];for(const name of await caches.keys())for(const request of await (await caches.open(name)).keys())all.push({name,path:new URL(request.url).pathname});return all;});
 assert.ok(entries.length>3);assert.ok(entries.every(({path})=>path==='/'||path==='/manifest.webmanifest'||path==='/icon.svg'||/^\/assets\/.*\.(js|css)$/.test(path)));checks.push('protected_api_auth_provider_never_cached');
 await context.setOffline(true);await page.reload();await importShell(page);assert.equal(await page.evaluate(()=>window.shell.prepareOwnShell()),true);assert.equal(await page.title(),'KDG Capture');assert.equal(await page.locator('script[src^="/assets/"]').count(),1);
 for(const path of ['/api/v1/context','/auth/v1/user','/provider/callback'])assert.equal(await page.evaluate(async path=>{try{await fetch(path);return true;}catch{return false;}},path),false);
 const admin=await context.newPage();let adminFailed=false;try{await admin.goto(origin+'/admin');}catch{adminFailed=true;}assert.equal(adminFailed,true);await admin.close();checks.push('offline_actual_own_root_only_no_admin_fallback');
 await context.setOffline(false);await page.reload();await importShell(page);await page.evaluate(()=>window.shell.prepareOwnShell());
 // A durable schema4-like IDB sentinel plus pending/conflict data is outside the shell owner.
 await page.evaluate(async()=>{await new Promise((resolve,reject)=>{const request=indexedDB.open('retained-schema4',4);request.onupgradeneeded=()=>request.result.createObjectStore('work');request.onerror=()=>reject(Error());request.onsuccess=()=>{const db=request.result,tx=db.transaction('work','readwrite');tx.objectStore('work').put({pending:'original-operation',conflict:'retained'},'sentinel');tx.oncomplete=()=>{db.close();resolve();};};});});
 // Build a genuine second revision from changed public shell bytes, without touching source work.
 const copiedIndex=join(web,'index.html');writeFileSync(copiedIndex,readFileSync(copiedIndex,'utf8').replace('<title>KDG Capture</title>','<title>KDG Capture updated</title>'));
 const copiedMain=join(web,'src/main.ts');writeFileSync(copiedMain,readFileSync(copiedMain,'utf8')+"\ndocument.documentElement.dataset.shellProofRevision='second';\n");
 selectedDist=build('dist2');const previousPort=server.address().port;const stopped=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await stopped;server=await startStatic(selectedDist,previousPort);await page.evaluate(async()=>{const registration=await navigator.serviceWorker.getRegistration('/');await registration.update();});
 await page.waitForFunction(async()=>Boolean((await navigator.serviceWorker.getRegistration('/'))?.waiting));
 await page.waitForFunction(()=>window.shell.shellState().updateAvailable);
 assert.equal(await page.title(),'KDG Capture');
 assert.equal(await page.evaluate(()=>window.shell.applyShellUpdate(()=>({hasUnsavedInput:true,activeWork:false}))),false);
 assert.equal(await page.evaluate(()=>window.shell.applyShellUpdate(()=>({hasUnsavedInput:false,activeWork:true}))),false);
 // Safety can change while readiness responds: current safety is rechecked after the await.
 assert.equal(await page.evaluate(()=>{let count=0;return window.shell.applyShellUpdate(()=>({hasUnsavedInput:++count>1,activeWork:false}));}),false);
 assert.equal(await page.title(),'KDG Capture');checks.push('typing_and_bounded_work_defer_update_and_recheck');
 const other=await context.newPage();await other.goto(origin);await other.evaluate(()=>{window.unsavedSentinel='still typing';});
 await page.evaluate(()=>{let calls=0;return window.shell.applyShellUpdate(()=>({hasUnsavedInput:++calls>=3,activeWork:false}));});
 await page.waitForFunction(()=>window.shell.shellState().updateAvailable);await page.waitForTimeout(150);
 assert.equal(await page.title(),'KDG Capture','typing begun during activation must defer reload');
 await page.evaluate(()=>window.shell.applyShellUpdate(()=>({hasUnsavedInput:false,activeWork:false})));
 await page.waitForFunction(()=>document.title==='KDG Capture updated');
 assert.equal(await other.evaluate(()=>window.unsavedSentinel),'still typing');
 const retained=await page.evaluate(async()=>{const request=indexedDB.open('retained-schema4');return new Promise(resolve=>{request.onsuccess=()=>{const db=request.result,read=db.transaction('work').objectStore('work').get('sentinel');read.onsuccess=()=>{resolve({version:db.version,value:read.result});db.close();};};});});
 assert.deepEqual(retained,{version:4,value:{pending:'original-operation',conflict:'retained'}});
 assert.equal((await page.evaluate(()=>caches.keys())).length,2);
 const oldAsset=entries.find(({path})=>/^\/assets\/index-.*\.js$/.test(path))?.path;assert.ok(oldAsset);
 await context.setOffline(true);assert.equal(await other.evaluate(async path=>(await fetch(path)).ok,oldAsset),true);await context.setOffline(false);
 checks.push('explicit_reload_retains_schema4_work_old_caches_and_other_tab_input');
 // A failed emitted-resource download cannot claim shell readiness, even if registration exists.
 const broken=join(proof,'dist-broken');mkdirSync(broken);const emitted=spawnSync('rg',['--files','--hidden',selectedDist],{encoding:'utf8'});assert.equal(emitted.status,0);for(const file of emitted.stdout.trim().split('\n')){const dest=join(broken,file.slice(selectedDist.length+1));mkdirSync(resolve(dest,'..'),{recursive:true});writeFileSync(dest,readFileSync(file));}
 const brokenSw=join(broken,'sw.js');writeFileSync(brokenSw,readFileSync(brokenSw,'utf8').replace('/manifest.webmanifest','/missing.webmanifest'));
 const brokenServer=await startStatic(broken),brokenContext=await browser.newContext();try{const brokenPage=await brokenContext.newPage();await brokenPage.goto('http://127.0.0.1:'+brokenServer.address().port);await importShell(brokenPage);assert.equal(await brokenPage.evaluate(()=>window.shell.prepareOwnShell()),false);assert.equal(await brokenPage.evaluate(()=>window.shell.shellState().ready),false);}finally{await brokenContext.close();const done=new Promise(resolve=>brokenServer.close(resolve));for(const socket of sockets)if(socket.localPort===brokenServer.address()?.port)socket.destroy();await done;}
 checks.push('incomplete_asset_install_never_acknowledges_shell_readiness');
 passed=true;
}finally{
 if(browser)await browser.close();if(server){const done=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await done;}if(upstream)await new Promise(resolve=>upstream.close(resolve));
 const result={passed,checks,proof,source_sha256:captured,limitations:['Synthetic public config; no provider/current authorization or business API proof','IndexedDB sentinel demonstrates shell does not touch schema4 bytes; actual history schema4 compatibility is tested by the store owner','Loopback Chromium service worker; no installed Android/iPhone/assistive technology qualification']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify({passed,checks,proof})+'\n');
}
