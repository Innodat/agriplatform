// Selected-source synthetic loopback proof; no active API/browser entry is started.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync} from 'node:fs';
import {resolve,join,dirname} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {watchChild,readyChild,stopChild} from './persistence-child.mjs';
import {createHash,randomUUID} from 'node:crypto';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createRequire} from 'node:module';
const root=process.cwd(),owner='apps/kdg-capture',hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v26.11.1');
const retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(JSON.parse(readFileSync(join(retained,'node_modules/typescript/package.json'))).version,'7.0.2');
const proof=join(root,'platform/deployment/.local/kdg-explicit-edit-delivery-20261026','http-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
 'web/src/edit-delivery.ts','web/src/edit-delivery-entry.ts','web/tests/edit-delivery-http-proof.mjs',
 'web/src/own-observation.ts',
 'web/src/edit-context.ts','web/src/edit-context-entry.ts','contracts/edit-context-generated/types.gen.ts','web/tests/persistence-child.mjs','web/tests/persistence-http-proof.mjs','web/tests/persistence-http-fixture.py','web/tsconfig.auth.json',
 'web/src/provision.ts','contracts/provision-generated/types.gen.ts','web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history-download.ts','web/src/history.ts','web/src/history-entry.ts','web/src/read-validation.ts','web/src/read.ts','web/src/read-entry.ts','web/src/create.ts','web/src/create-entry.ts','web/src/edit.ts','web/src/edit-entry.ts','web/src/recovery.ts','web/src/recovery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/entry.ts','web/src/auth-public-input.ts',
 'contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/create-generated/types.gen.ts','contracts/edit-generated/types.gen.ts','contracts/recovery-generated/types.gen.ts','contracts/generated/types.gen.ts',
 'api/main.py','api/context.py','api/safe_errors.py','api/capture_commands.py','api/questionnaire.py','write-tools/transaction_context.py',
 ...['own_observation_openapi','edit_context','edit_context_http','edit_context_openapi','history_http','history_openapi','capture_history','read_http','read_openapi','capture_read','create_http','edit_http','recovery_http','create_openapi','edit_openapi','recovery_openapi','capture_create_handler','capture_edit_handler','capture_create','capture_edit','operation_recovery','operation_outcomes'].map(x=>'write-candidate/'+x+'.py')
].map(x=>owner+'/'+x);
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
writeFileSync(join(capsule,'package.json'),'{"private":true,"type":"module"}\n');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['edit-delivery-entry','edit-context-entry','history-entry','read-entry','create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0);
let childOwner,server,origin,browser,host,passed=false,stdout='',stderr='';
let shutdown={forced_stop:false,shutdown_failed:false},stopped=false;const checks=[],traffic=[],sockets=new Set();
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 server=spawn(python,['-I','-B',join(capsule,owner,'web/tests/persistence-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});
 childOwner=watchChild(server);server.stdout.on('data',x=>stdout+=x);server.stderr.on('data',x=>stderr+=x);
 const ready=await readyChild(server,childOwner);origin=ready.origin;assert.equal(new URL(origin).hostname,'127.0.0.1');
 host=createServer(async(req,res)=>{
  const path=new URL(req.url,'http://local').pathname;
  try{
   if(path.startsWith('/api/v1/')){
    const chunks=[];for await(const bytes of req)chunks.push(bytes);
    const response=await fetch(origin+req.url,{method:req.method,headers:{authorization:req.headers.authorization??'', 'content-type':req.headers['content-type']??'application/json'},...(req.method==='GET'?{}:{body:Buffer.concat(chunks)})});
    traffic.push({path:req.url,method:req.method,status:response.status});res.writeHead(response.status,{'content-type':response.headers.get('content-type')??'application/json','cache-control':'private, no-store'});res.end(Buffer.from(await response.arrayBuffer()));return;
   }
   if(path==='/'){res.setHeader('content-type','text/html');res.end('<!doctype html><title>Synthetic delivery</title>');return;}
   const local=resolve(capsule,'.'+path);if(!local.startsWith(capsule+'/')){res.writeHead(404).end();return;}
   res.setHeader('content-type','text/javascript');res.end(readFileSync(local));
  }catch{res.writeHead(503).end();}
 });host.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});host.listen(0,'127.0.0.1');await once(host,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));
 browser=await require('@playwright/test').chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const page=await browser.newPage();await page.exposeFunction('fixtureMode',async mode=>{assert.ok(['all','edit_denied','deny'].includes(mode));const response=await fetch(origin+'/__fixture',{method:'POST',body:JSON.stringify({mode})});assert.equal(response.status,200);return response.json();});const localOrigin='http://127.0.0.1:'+host.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===localOrigin?r.continue():r.abort());await page.goto(localOrigin);
 checks.push(...await page.evaluate(async ids=>{
  const {editCapture}=await import('/compiled/web/src/edit.js');const {createCapture}=await import('/compiled/web/src/create.js');const {loadEditContext}=await import('/compiled/web/src/edit-context.js');
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {createEditDeliveryEntry}=await import('/compiled/web/src/edit-delivery-entry.js');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
  const session={account_id:ids.account,access_token:'synthetic-token'},scope={account_id:ids.account,org_id:ids.org},pin={...scope,capture_id:ids.capture};
  const signal=new AbortController().signal,execution={signal,isCurrent:()=>true};
  const command={operation_id:ids.create,command_version:1,capture_id:ids.capture,child_id:ids.child,questionnaire_version_id:ids.version,observation_date:'2026-10-26',captured_at:'2026-10-26T10:00:00Z',child_eligibility_ref:'synthetic',answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};
  ok((await createCapture(session,{...scope,command},execution)).kind==='committed','actual_api_create');
  const context=await loadEditContext(session,pin,execution);ok(context.kind==='loaded','actual_api_edit_context');
  const now=Math.max(Date.parse(context.context.read_observation.checked_at),Date.parse(context.context.edit_observation.checked_at))+1000;
  const store=await openHistoryStore(scope,{database:'actual-http-delivery',wall:()=>now,monotonic:()=>1});
  let entry;
  try{
   ok((await store.importEditContext(context.context,pin)).kind==='committed','actual_context_import');
   const answers={...command.answers,[ids.question]:{value:2}};
   ok((await store.saveEdit((await store.openEdit(ids.capture)).reviewed,ids.edit,{observation_date:'2026-10-26',answers})).kind==='saved_locally','explicit_local_save');
   const sdkSession={user:{id:ids.account},access_token:'synthetic-token'};
   const auth={getSession:async()=>({data:{session:sdkSession},error:null}),refreshSession:async()=>({data:{session:sdkSession},error:null}),signOut:async()=>({error:null}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})};
   const calls=[];entry=createEditDeliveryEntry({org:ids.org,auth,store,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{calls.push(init?.method??'GET');return fetch(url,init);}});await entry.start();
   const delivered=await entry.deliver({...scope,action_id:ids.edit});
   ok(delivered.kind==='acknowledged'&&delivered.readback==='imported','actual_delivery_acknowledged_and_readback');
   ok(calls.slice(-3).join(',')==='GET,PUT,GET','actual_recover_before_send_and_readback');
   const row=(await store.read()).records[0];ok(row.baseline.revision==='2'&&!row.saved_edit&&row.edit_status==='Synced','actual_receipt_detail_reconciles');
   ok(row.baseline.owner_actor_id===ids.actor&&row.baseline.updated_by===ids.actor,'actual_durable_actor_provenance');
   await store.denyEdit();calls.length=0;
   const retry=await entry.deliver({...scope,action_id:ids.edit});
   ok(retry.kind==='acknowledged'&&retry.readback==='imported'&&calls.join(',')==='GET,GET','actual_original_recovery_after_edit_denial_no_put');
   ok((await store.openEdit(ids.capture)).kind==='denied','actual_readback_preserves_edit_denial');
  }finally{entry?.dispose();store.close();}
  const sdkSession={user:{id:ids.account},access_token:'synthetic-token'};
  const auth={getSession:async()=>({data:{session:sdkSession},error:null}),refreshSession:async()=>({data:{session:sdkSession},error:null}),signOut:async()=>({error:null}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})};
  for(const mode of ['lost_response','edit_denied','read_denied','conflict']){
   await window.fixtureMode('all');const fresh=await loadEditContext(session,pin,execution);ok(fresh.kind==='loaded','case_context_'+mode);
   const local=await openHistoryStore(scope,{database:'actual-http-'+mode,wall:()=>Math.max(Date.parse(fresh.context.read_observation.checked_at),Date.parse(fresh.context.edit_observation.checked_at))+1000,monotonic:()=>1});let gate;
   const selected=crypto.randomUUID(),proposal={observation_date:'2026-10-26',answers:{...command.answers,[ids.question]:{value:mode==='lost_response'?3:4}}};
   try{
    await local.importEditContext(fresh.context,pin);ok((await local.saveEdit((await local.openEdit(ids.capture)).reviewed,selected,proposal)).kind==='saved_locally','case_saved_'+mode);
    let lose=mode==='lost_response';const calls=[];
    gate=createEditDeliveryEntry({org:ids.org,auth,store:local,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{calls.push(init?.method??'GET');const response=await fetch(url,init);if(init?.method==='PUT'&&lose){lose=false;throw Error('synthetic_lost_response');}return response;}});await gate.start();calls.length=0;
    if(mode==='edit_denied')await window.fixtureMode('edit_denied');
    if(mode==='read_denied')await window.fixtureMode('deny');
    if(mode==='conflict'){
     const external=await editCapture(session,{...pin,command:{operation_id:crypto.randomUUID(),command_version:1,expected_revision:fresh.context.capture.revision,observation_date:'2026-10-26',answers:{...command.answers,[ids.question]:{value:5}}}},execution);
     ok(external.kind==='committed','actual_concurrent_revision_committed');
    }
    const first=await gate.deliver({...scope,action_id:selected});
    if(mode==='lost_response'){
     ok(first.kind==='verification_unavailable'&&(await local.read()).records[0].saved_edit.action_id===selected,'actual_lost_response_retains_original_input');
     const second=await gate.deliver({...scope,action_id:selected});
     ok(second.kind==='acknowledged'&&second.readback==='imported','actual_lost_response_recovers_receipt');
     ok(calls.join(',')==='GET,PUT,GET,GET','actual_lost_response_one_put_original_recovery');
     ok((await local.lookupPreparedEdit({...scope,action_id:selected})).pending.command.operation_id===selected,'actual_lost_response_original_identity');
    }else if(mode==='edit_denied'){
     ok(first.kind==='denied'&&calls.join(',')==='GET,PUT,GET','actual_server_edit_denial_probes_read');
     ok((await local.read()).kind==='available'&&(await local.openEdit(ids.capture)).kind==='denied','actual_server_edit_denial_keeps_read');
    }else if(mode==='read_denied'){
     ok(first.kind==='denied'&&calls.join(',')==='GET'&&(await local.read()).kind==='unavailable','actual_server_read_denial_locks_before_put');
    }else{
     ok(first.kind==='conflict'&&first.readback==='imported','actual_server_revision_conflict_reconciles');
     const row=(await local.read()).records[0];ok(row.edit_status==='Needs attention'&&row.saved_edit.action_id===selected&&row.baseline.revision==='4','actual_conflict_keeps_proposal_new_baseline');
    }
   }finally{gate?.dispose();local.close();await window.fixtureMode('all');}
  }
  return checks;
 },ready.ids));
 const state=await(await fetch(origin+'/__fixture')).json();
 assert.equal(state.outcomes,4);assert.equal(state.history,4);assert.equal(state.captures[ready.ids.capture].revision,4);assert.equal(state.acquired,state.released);
 checks.push('actual_four_effects_create_edit_lost_response_remote_conflict_balanced_resources');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(state,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(browser)await browser.close();if(host){const done=new Promise(r=>host.close(r));for(const s of sockets)s.destroy();await done;}
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);
 stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);
 const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,child:childOwner?.state??null,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['synthetic Access and storage; no actual PostgreSQL permission or rollback evidence','isolated Chromium; no startup or real account']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
