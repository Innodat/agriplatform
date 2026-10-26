// Selected-source synthetic loopback proof; no active API/browser entry is started.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync} from 'node:fs';
import {resolve,join,dirname} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {watchChild,readyChild,stopChild} from './persistence-child.mjs';
import {createHash,randomUUID} from 'node:crypto';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {once} from 'node:events';
const root=process.cwd(),owner='apps/kdg-capture',hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v26.11.1');
const retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(JSON.parse(readFileSync(join(retained,'node_modules/typescript/package.json'))).version,'7.0.2');
const proof=join(root,'platform/deployment/.local/kdg-local-create-save-20261026','http-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
 'web/src/setup-download.ts','web/tests/local-create-http-proof.mjs',
 'web/src/provision.ts','web/src/provision-entry.ts','contracts/provision-generated/types.gen.ts','web/tests/provision-http-proof.mjs','web/tests/provision-http-fixture.py','write-candidate/provision.py','write-candidate/provision_http.py','write-candidate/provision_openapi.py',
 'web/src/own-observation.ts',
 'web/src/edit-context.ts','web/src/edit-context-entry.ts','contracts/edit-context-generated/types.gen.ts','web/tests/persistence-child.mjs','web/tests/persistence-http-proof.mjs','web/tests/persistence-http-fixture.py','web/tsconfig.auth.json',
 'web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history-download.ts','web/src/history.ts','web/src/history-entry.ts','web/src/read-validation.ts','web/src/read.ts','web/src/read-entry.ts','web/src/create.ts','web/src/create-entry.ts','web/src/edit.ts','web/src/edit-entry.ts','web/src/recovery.ts','web/src/recovery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/entry.ts','web/src/auth-public-input.ts',
 'contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/create-generated/types.gen.ts','contracts/edit-generated/types.gen.ts','contracts/recovery-generated/types.gen.ts','contracts/generated/types.gen.ts',
 'api/main.py','api/context.py','api/safe_errors.py','api/capture_commands.py','api/questionnaire.py','write-tools/transaction_context.py',
 ...['own_observation_openapi','edit_context','edit_context_http','edit_context_openapi','history_http','history_openapi','capture_history','read_http','read_openapi','capture_read','create_http','edit_http','recovery_http','create_openapi','edit_openapi','recovery_openapi','capture_create_handler','capture_edit_handler','capture_create','capture_edit','operation_recovery','operation_outcomes'].map(x=>'write-candidate/'+x+'.py')
].map(x=>owner+'/'+x);
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
writeFileSync(join(capsule,'package.json'),'{"private":true,"type":"module"}\n');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['setup-download','history-store','provision-entry','edit-context-entry','history-entry','read-entry','create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0);
let server,childOwner,origin,passed=false,stdout='',stderr='',browser,web;
const checks=[],traffic=[],sockets=new Set();let shutdown={forced_stop:false,shutdown_failed:false},stopped=false;
try{
 server=spawn(join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python'),['-I','-B',join(capsule,owner,'web/tests/provision-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});
 childOwner=watchChild(server);server.stdout.on('data',x=>stdout+=x);server.stderr.on('data',x=>stderr+=x);
 const ready=await readyChild(server,childOwner);origin=ready.origin;assert.equal(new URL(origin).hostname,'127.0.0.1');
 const fixture=async mode=>{const r=await fetch(origin+'/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(r.status,200);return r.json();};
 await fixture('all');
 web=createServer(async(req,res)=>{
  const path=new URL(req.url,'http://local').pathname;
  if(path==='/api/v1/provision'){
   try{const r=await fetch(origin+path,{headers:req.headers});traffic.push({path,method:req.method,status:r.status});res.writeHead(r.status,{'Content-Type':'application/json','Cache-Control':r.headers.get('cache-control')??''});res.end(await r.text());}catch{res.writeHead(503).end();}return;
  }
  res.setHeader('Content-Type',path.endsWith('.js')?'text/javascript':'text/html');
  if(path==='/')res.end('<!doctype html><title>Isolated setup Save proof</title>');
  else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}
 });web.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});web.listen(0,'127.0.0.1');await once(web,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));
 const {chromium}=require('@playwright/test');browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const context=await browser.newContext(),page=await context.newPage(),webOrigin='http://127.0.0.1:'+web.address().port;
 await page.route('**/*',r=>new URL(r.request().url()).origin===webOrigin?r.continue():r.abort());await page.goto(webOrigin);
 const actual=await page.evaluate(async ids=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {createSetupEntry}=await import('/compiled/web/src/setup-download.js');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
  const scope={account_id:ids.account,org_id:ids.org};let store=await openHistoryStore(scope,{database:'actual-create-save'});
  let hold=false;const session={user:{id:ids.account},access_token:'synthetic-token'};
  const auth={getSession:async()=>({data:{session},error:null}),refreshSession:async()=>({data:{session},error:null}),signOut:async()=>({error:null}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})};
  const configuration={org:ids.org,auth,store,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{
   if(url==='/api/v1/context')return new Response(JSON.stringify({account_id:ids.account,actor_id:ids.actor,membership_id:'7',authorization_scope:{kind:'organization',org_id:ids.org},resource_scope:{kind:'own_account',account_id:ids.account},permission:'kdg_capture.capture.read.own',decision_id:ids.decision,checked_at:new Date().toISOString()}));
   if(hold)return new Promise(()=>{});return fetch(url,init);
  }};const entry=createSetupEntry(configuration);
  try{
   await entry.start();ok(entry.state().kind==='authorized','actual_auth_admission');
   const setup=await entry.refresh(scope);ok(setup.kind==='committed','actual_setup_request_import_committed:'+setup.kind);
   const opened=await store.openCreate(ids.child);ok(opened.kind==='opened','actual_child_original_definition_opened');
   const identity={capture_id:'88888888-8888-4888-8888-888888888888',operation_id:'99999999-9999-4999-8999-999999999999'};
   const input={observation_date:new Date().toISOString().slice(0,10),captured_at:new Date().toISOString(),answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};
   ok((await store.saveCreate(opened.reviewed,identity,input)).kind==='saved_locally','actual_completed_capture_saved');
   store.close();store=await openHistoryStore(scope,{database:'actual-create-save'});
   const actions=await store.readCreateActions(),history=await store.read();
   ok(actions.kind==='available'&&actions.actions.length===1,'actual_reopen_one_original_create_action');
   ok(history.kind==='available'&&history.records.length===1&&!history.records[0].baseline,'actual_local_record_without_server_baseline');
   const command=actions.actions[0].pending.command;
   ok(command.capture_id===identity.capture_id&&command.operation_id===identity.operation_id&&command.answers[ids.question].value===1,'actual_exact_create_identity_and_answers');
   ok((await store.saveCreate(opened.reviewed,identity,input)).kind==='saved_locally'&&(await store.readCreateActions()).actions.length===1,'actual_original_retry_idempotent_after_reopen');
   // A bounded failed setup releases its lease; a later explicit refresh can succeed.
   const bounded=createSetupEntry({...configuration,store,setupTimeoutMs:1000});
   try{await bounded.start();hold=true;const timed=await bounded.refresh(scope);ok(timed.kind==='verification_unavailable','actual_setup_total_deadline');hold=false;ok((await bounded.refresh(scope)).kind==='committed','actual_setup_lease_released_after_timeout');}finally{hold=false;bounded.dispose();}
   globalThis.runSafeSetup=async expected=>{
    const next=await openHistoryStore(scope,{database:'actual-create-save'}),candidate=createSetupEntry({...configuration,store:next});
    try{await candidate.start();const old=await next.openCreate(ids.child);const result=await candidate.refresh(scope,{restoreDenied:expected==='committed'});ok(result.kind===expected,'actual_setup_safe_failure:'+expected);if(expected==='error')ok(result.error_id==='authorization_unavailable','actual_setup_safe_outage_identifier');if(expected==='locked'){
     ok((await next.saveCreate(old.reviewed,{capture_id:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',operation_id:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'},input)).kind!=='saved_locally','actual_denial_invalidates_open_form');
     ok((await next.read()).kind!=='available'&&(await next.readCreateActions()).kind!=='available','actual_denial_locks_open_reads');
     const reopened=await openHistoryStore(scope,{database:'actual-create-save'});try{ok((await reopened.read()).kind!=='available'&&(await reopened.readCreateActions()).kind==='denied','actual_denial_survives_reopen');}finally{reopened.close();}
    }
    return {result,actions:(await next.readCreateActions()).actions?.length};}finally{candidate.dispose();next.close();}
   };
   globalThis.beginOrderedSetup=async()=>{
    const ordered=await openHistoryStore(scope,{database:'actual-create-save'});let first=true,release,captured;
    const gate=new Promise(resolve=>release=resolve),held=new Promise(resolve=>captured=resolve);
    const candidate=createSetupEntry({...configuration,store:ordered,request:async(url,init)=>{
     if(url!=='/api/v1/provision'||!first)return configuration.request(url,init);
     first=false;const response=await configuration.request(url,init);captured();await gate;return response;
    }});await candidate.start();const old=candidate.refresh(scope);
    globalThis.finishOrderedSetup=async()=>{try{const current=await candidate.refresh(scope);ok(current.kind==='committed','actual_newer_setup_success');release();ok((await old).kind==='superseded','actual_older_http_denial_result_superseded');ok((await ordered.read()).kind==='available'&&(await ordered.readCreateActions()).actions.length===1,'actual_older_http_denial_cannot_lock_newer_success');return true;}finally{candidate.dispose();ordered.close();}};
    await held;return true;
   };
   globalThis.setupPersistenceDeadline=async phase=>{
    const target=await openHistoryStore(scope,{database:'actual-create-save'});
    const raw=await new Promise((resolve,reject)=>{const q=indexedDB.open('actual-create-save');q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);});
    const snapshot=()=>new Promise((resolve,reject)=>{const tx=raw.transaction('setups','readonly'),q=tx.objectStore('setups').get(scope.account_id+'/'+scope.org_id);q.onsuccess=()=>resolve(JSON.stringify(q.result));q.onerror=()=>reject(q.error);});
    const before=await snapshot();let blocker,active=false,seen=false,release=()=>{},fallbackTimer;
    const wrapped={...target,[phase==='import'?'importProvision':'denySetup']:(...args)=>{seen=true;return target[phase==='import'?'importProvision':'denySetup'](...args);}};
    const candidate=createSetupEntry({...configuration,store:wrapped,setupTimeoutMs:1000,request:async(url,init)=>{
     const response=await configuration.request(url,init);if(url!=='/api/v1/provision')return response;
     blocker=raw.transaction('partitions','readwrite');active=true;
     const pump=()=>{const q=blocker.objectStore('partitions').get('fixture-block');q.onsuccess=()=>{if(active)pump();};};pump();
     release=()=>{active=false;try{blocker.abort();}catch{}};return response;
    }});
    try{
     await candidate.start();const pending=candidate.refresh(scope);
     const result=await Promise.race([pending,new Promise(resolve=>{fallbackTimer=setTimeout(()=>resolve({kind:'test_deadline_missed'}),1500);})]);
     const stillBlocked=active;release();await pending;
     ok(seen&&stillBlocked&&result.kind==='verification_unavailable','actual_'+phase+'_deadline_aborts_queued_publication');
     ok(await snapshot()===before,'actual_'+phase+'_deadline_preserves_previous_setup');
     return true;
    }finally{clearTimeout(fallbackTimer);release();candidate.dispose();target.close();raw.close();}
   };
   return {checks,eligibility_ref:command.child_eligibility_ref};
  }finally{entry.dispose();store.close();}
 },ready.ids);
 checks.push(...actual.checks);
 await fixture('outage');const outage=await page.evaluate(()=>globalThis.runSafeSetup('error'));assert.equal(outage.actions,1);checks.push('actual_setup_outage_preserves_pending_create');
 await fixture('all');const recovery=await page.evaluate(()=>globalThis.runSafeSetup('committed'));assert.equal(recovery.actions,1);checks.push('actual_setup_explicit_retry_after_outage');
 await fixture('deny');await page.evaluate(()=>globalThis.beginOrderedSetup());await fixture('all');assert.equal(await page.evaluate(()=>globalThis.finishOrderedSetup()),true);checks.push('actual_older_http_denial_cannot_lock_newer_success');
 await fixture('deny');const denied=await page.evaluate(()=>globalThis.runSafeSetup('locked'));assert.equal(denied.actions,undefined);checks.push('actual_current_http_denial_locks_open_form_reads_and_reopen');
 await fixture('all');const restored=await page.evaluate(()=>globalThis.runSafeSetup('committed'));assert.equal(restored.actions,1);checks.push('actual_explicit_restore_with_reopened_store_and_new_entry');
 await fixture('all');assert.equal(await page.evaluate(()=>globalThis.setupPersistenceDeadline('import')),true);checks.push('actual_import_deadline_aborts_queued_idb_publication');
 await fixture('deny');assert.equal(await page.evaluate(()=>globalThis.setupPersistenceDeadline('denial')),true);checks.push('actual_denial_deadline_aborts_queued_idb_publication');
 const after=await fixture();
 assert.ok(after.eligibility[actual.eligibility_ref]);assert.equal(after.captures+after.outcomes+after.history,0);assert.equal(after.acquired,after.released);checks.push('actual_setup_reference_committed_without_server_capture');
 writeFileSync(join(proof,'integration-state.json'),JSON.stringify(after,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(browser)await browser.close();if(web){const done=new Promise(r=>web.close(r));for(const socket of sockets)socket.destroy();await done;}
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['actual synthetic provision HTTP and real Chromium IndexedDB; Auth/Access and database are fixtures','no actual database permissions/rollback, server create delivery or browser startup activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
