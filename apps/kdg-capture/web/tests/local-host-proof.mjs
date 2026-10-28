// Synthetic local host qualification; fresh source capsule and retained approved tools.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync,existsSync,readdirSync} from 'node:fs';
import {join,resolve,dirname,relative,sep} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createHash,randomUUID} from 'node:crypto';
import {createRequire} from 'node:module';
const root=process.cwd(),owner='apps/kdg-capture',hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v26.11.1');
const proof=join(root,'platform/deployment/.local/kdg-local-host-20261023','proof-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const copy=join(proof,'root'),web=join(copy,owner,'web');mkdirSync(copy);
const snapshots=Object.fromEntries(['web/package.json','web/tsconfig.auth.json','web/local-host.config.ts','web/tsconfig.local-host.json','web/local-host-tools/local-entry-host.mjs','web/local-host-tools/test-local-entry-host.mjs','web/local-host-tools/.generated-files.json','web/src/local-public-config.ts','web/src/auth-public-input.ts','web/index.html','web/src/main.ts','web/src/startup.tsx','web/tests/local-host-proof.mjs','web/tests/local-host-fixture/api.py','api/main.py','api/context.py','api/safe_errors.py'].filter(p=>existsSync(join(root,owner,p))).map(p=>[owner+'/'+p,hash(readFileSync(join(root,owner,p)))]));
// Read only explicit web and contract roots, plus the three context API files.
// Never traverse the application root: it contains separately governed native fixtures.
const sourcePaths=[...Object.keys(snapshots),...readdirSync(join(root,owner,'web/src'),{recursive:true,withFileTypes:true}).filter(e=>e.isFile()).map(e=>join(e.parentPath,e.name)),...readdirSync(join(root,owner,'contracts'),{recursive:true,withFileTypes:true}).filter(e=>e.isFile()).map(e=>join(e.parentPath,e.name))];
for(const source of sourcePaths){const path=source.startsWith(root+sep)?relative(root,source):source,dest=join(copy,path);mkdirSync(dirname(dest),{recursive:true});const bytes=readFileSync(join(root,path));snapshots[path]=hash(bytes);writeFileSync(dest,bytes);}
assert.ok(Object.entries(snapshots).every(([p,v])=>hash(readFileSync(join(copy,p)))===v),'capsule_source_mismatch');
const retained=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root'),modules=join(retained,'apps/bootstrap-application/web/node_modules');
symlinkSync(join(retained,'node_modules'),join(copy,'node_modules'),'dir');symlinkSync(modules,join(web,'node_modules'),'dir');
const runtime=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules');
// The retained scaffold install does not carry Supabase; resolve app dependencies in a capsule.
const localModules=join(proof,'modules');mkdirSync(localModules);for(const name of ['@supabase'])symlinkSync(join(runtime,name),join(localModules,name),'dir');
// Vite resolves package imports from the capsule root; add only the missing selected package namespace.
symlinkSync(localModules,join(copy,owner,'node_modules'),'dir');

const mode=join(proof,'mode');writeFileSync(mode,'success');
const children=[],logs={},checks=[],issuedTokens=new Set();let vite,api,browser,auth,page,passed=false;const browserEvents=[];const stopped={};
async function child(name,exe,args,env){const p=spawn(exe,args,{cwd:web,env:{PATH:'/usr/bin:/bin',LC_ALL:'C.UTF-8',...env},stdio:['ignore','pipe','pipe']});children.push([name,p]);logs[name]='';p.stdout.on('data',x=>logs[name]+=x);p.stderr.on('data',x=>logs[name]+=x);p.on('error',()=>{});return p;}
async function until(check,ms=15000){const end=Date.now()+ms;while(Date.now()<end){if(await check())return;await new Promise(r=>setTimeout(r,30));}throw Error('host_stage_timeout');}
async function stop(name,p){if(p.exitCode===null&&p.signalCode===null){p.kill('SIGTERM');await Promise.race([once(p,'exit'),new Promise(r=>setTimeout(r,4000))]);}stopped[name]={exited:p.exitCode!==null||p.signalCode!==null,forced:false,code:p.exitCode,signal:p.signalCode};if(!stopped[name].exited){p.kill('SIGKILL');await once(p,'exit');stopped[name].forced=true;}}
try{
 const types=spawnSync(process.execPath,[join(runtime,'typescript/bin/tsc'),'--project',join(web,'tsconfig.local-host.json')],{cwd:web,encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.equal(types.status,0,'host_types_failed');checks.push('strict_host_ts7');
 api=await child('api',join(root,'platform/deployment/.local/kdg-context-20261022/owner-env/bin/python'),['-I','-B',join(web,'tests/local-host-fixture/api.py'),mode]);await until(()=>logs.api.includes('\n'));const apiOrigin='http://127.0.0.1:'+JSON.parse(logs.api.split('\n')[0]).port;
 await until(async()=>{try{return(await fetch(apiOrigin+'/api/v1/context')).status===401;}catch{return false;}});checks.push('actual_fastapi_ready');
 const paths=[];auth=createServer((req,res)=>{paths.push(req.url);res.setHeader('Content-Type','application/json');res.setHeader('Access-Control-Allow-Origin','*');res.setHeader('Access-Control-Allow-Headers','authorization,apikey,content-type,x-client-info,x-supabase-api-version');if(req.method==='OPTIONS'){res.end('{}');return;}let raw='';req.on('data',x=>raw+=x);req.on('end',()=>{const body=JSON.parse(raw);if(req.url==='/auth/v1/otp'){assert.equal(body.create_user,false);res.end('{}');return;}assert.equal(req.url,'/auth/v1/verify');assert.equal(body.token,'123456');const account='11111111-1111-4111-8111-111111111111',token=Buffer.from(JSON.stringify({alg:'HS256'})).toString('base64url')+'.'+Buffer.from(JSON.stringify({sub:account,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})).toString('base64url')+'.c3ludGhldGlj';issuedTokens.add(token);res.end(JSON.stringify({access_token:token,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:account,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T00:00:00Z'}}));});});auth.listen(0,'127.0.0.1');await once(auth,'listening');const authOrigin='http://127.0.0.1:'+auth.address().port;
 const config=join(proof,'public.json');writeFileSync(config,JSON.stringify({schema_version:1,environment_kind:'ci_disposable',org_id:'33333333-3333-4333-8333-333333333333',auth_url:authOrigin,auth_public_key:'sb_publishable_synthetic_public_123456',api_origin:apiOrigin}));
 const negative=[];const hostConfig=join(web,'local-host.config.ts');
 const valid=JSON.parse(readFileSync(config));
 for(const scenario of ['missing','malformed','remote-api','bad-org','private-key','extra','large','inside','dependency','symlink','host-override']){
  const dependency=join(copy,owner,'node_modules/private-input.json');const file=scenario==='inside'?join(web,'private-input.json'):scenario==='dependency'?dependency:join(proof,'invalid-'+scenario+'.json');let data={...valid};
  if(scenario==='remote-api')data.api_origin='http://remote.invalid:8188';if(scenario==='bad-org')data.org_id='PRIVATE';if(scenario==='private-key')data.auth_public_key='sb_secret_PRIVATE';if(scenario==='extra')data.service_key='PRIVATE';
  if(scenario==='symlink'){const inside=join(web,'symlink-input.json');writeFileSync(inside,JSON.stringify(data));symlinkSync(inside,file);}else writeFileSync(file,scenario==='malformed'?'PRIVATE':scenario==='large'?'x'.repeat(8193):JSON.stringify(data));
  const run=spawnSync(process.execPath,[join(modules,'vite/bin/vite.js'),'--config',hostConfig,'--port','0',...(scenario==='host-override'?['--host','0.0.0.0']:[])],{cwd:web,env:{PATH:'/usr/bin:/bin',LC_ALL:'C.UTF-8',...(scenario==='missing'?{}:{KDG_LOCAL_WEB_CONFIG:scenario==='host-override'?config:file})},encoding:'utf8',timeout:5000});
  const output=run.stdout+run.stderr;assert.equal(run.status,1,scenario);assert.ok(!output.includes('PRIVATE')&&!output.includes('http://127.0.0.1:'),'unsafe_negative_host_output');negative.push({scenario,status:run.status,safe:true});
 }
 writeFileSync(join(proof,'negative.json'),JSON.stringify(negative,null,2));checks.push('cli_invalid_config_and_override_no_listen');
 if(!existsSync(hostConfig))writeFileSync(hostConfig,"export default {server:{host:'127.0.0.1',port:0}};\n");
 writeFileSync(join(web,'env-check.ts'),'export default import.meta.env;\n');
 vite=await child('vite',process.execPath,[join(modules,'vite/bin/vite.js'),'--config',hostConfig,'--port','0'],{KDG_LOCAL_WEB_CONFIG:config,VITE_SYNTHETIC_PRIVATE:'PRIVATE'});await until(()=>/http:\/\/127\.0\.0\.1:\d+/.test(logs.vite));const origin=logs.vite.match(/http:\/\/127\.0\.0\.1:\d+/)[0];
 const require=createRequire(join(retained,'package.json'));const {chromium}=require('@playwright/test');browser=await chromium.launch({headless:true,executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell')});page=await browser.newPage();page.on('response',r=>{if(r.status()>=400)browserEvents.push({path:new URL(r.url()).pathname,status:r.status()});});page.on('pageerror',()=>browserEvents.push({event:'page_error'}));page.setDefaultTimeout(5000);
 const traffic=[];await page.route('**/*',route=>{const url=new URL(route.request().url());assert.ok([origin,authOrigin].includes(url.origin),'external_browser_request');traffic.push(url.origin+url.pathname);return route.continue();});
 await page.goto(origin);await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();checks.push('actual_vite_cli_configures_real_entry');const environment=await page.evaluate(async()=>{return(await import('/env-check.ts')).default;});assert.equal(environment.VITE_SYNTHETIC_PRIVATE,undefined);
 const privateFile=await fetch(origin+'/@fs'+config);assert.ok([403,404].includes(privateFile.status));assert.ok(!(await privateFile.text()).includes('sb_publishable_synthetic'));const configSource=await fetch(origin+'/local-host.config.ts');assert.ok([403,404].includes(configSource.status));checks.push('private_files_and_ambient_env_not_served');
 await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('facilitator@example.invalid');await page.getByLabel('Email address',{exact:true}).press('Enter');await page.getByLabel('One-time code',{exact:true}).fill('123456');await page.getByLabel('One-time code',{exact:true}).press('Enter');await page.getByRole('heading',{name:'Setup not completed',exact:true}).waitFor();assert.ok(traffic.includes(origin+'/api/v1/context'));assert.ok(!traffic.some(x=>x.startsWith(apiOrigin)));checks.push('same_origin_browser_actual_fastapi_admission');
 writeFileSync(mode,'denied');await page.reload();await page.getByRole('heading',{name:'Access denied',exact:true}).waitFor();checks.push('actual_api_current_denial');
 const selector=await fetch(origin+'/api/v1/context?org_id=PRIVATE',{headers:{Authorization:'Bearer synthetic'}});assert.equal(selector.status,422);assert.equal((await selector.json()).error_id,'validation_failed');
 const unknown=await fetch(origin+'/api/private?token=PRIVATE');assert.equal(unknown.status,404);assert.match(unknown.headers.get('content-type'),/application\/json/);checks.push('selectors_and_unknown_api_refuse');
 await stop('api',api);await page.getByRole('button',{name:'Check access again',exact:true}).click();await page.getByRole('heading',{name:'Could not check access',exact:true}).waitFor();checks.push('actual_api_outage_safe');
 const html=await(await fetch(origin)).text();assert.ok(!html.includes('SYNTHETIC-SERVER-ONLY'));assert.ok(!html.includes('api_origin'));await page.screenshot({path:join(proof,'local-host.png')});writeFileSync(join(proof,'browser.json'),JSON.stringify({traffic,auth_paths:paths},null,2));assert.deepEqual(browserEvents,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:503}]);checks.push('all_browser_errors_accounted');passed=true;
}finally{
 async function attempt(name,work){try{await work();}catch{passed=false;stopped[name]={failed:true};}}
 await attempt('evidence',async()=>{if(page){writeFileSync(join(proof,'browser-events.json'),JSON.stringify(browserEvents,null,2));try{await page.screenshot({path:join(proof,'final-browser.png'),timeout:3000});}catch{passed=false;}}});
 await attempt('browser',async()=>{if(browser)await browser.close();});
 await attempt('auth',async()=>{if(auth){auth.closeAllConnections();await new Promise(r=>auth.close(r));stopped.auth=true;}});
 for(const [name,p]of children)if(!stopped[name])await attempt(name,()=>stop(name,p));
 for(const [name,log]of Object.entries(logs)){writeFileSync(join(proof,name+'.log'),log);if(['SYNTHETIC-SERVER-ONLY','synthetic-refresh','Bearer synthetic','PRIVATE',...issuedTokens].some(value=>log.includes(value)))passed=false;}
 if(browserEvents.some(event=>event.event==='page_error'))passed=false;

 let unchanged=false;try{unchanged=Object.entries(snapshots).every(([p,v])=>hash(readFileSync(join(root,p)))===v&&hash(readFileSync(join(copy,p)))===v);}catch{unchanged=false;}const result={passed:passed&&unchanged&&Object.values(stopped).every(x=>x===true||(x.exited&&!x.forced)),checks,proof,source_sha256:snapshots,source_unchanged:unchanged,stopped,limitations:['actual Vite CLI / KDG FastAPI; synthetic Auth HTTP and synthetic Access transport; no real accounts/SQL/SMTP/device','retained proof-capsule dependencies, no normal installed KDG workspace qualification']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
