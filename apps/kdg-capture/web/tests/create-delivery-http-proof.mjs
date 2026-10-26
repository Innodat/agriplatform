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
const proof=join(root,'platform/deployment/.local/kdg-explicit-create-delivery-20261026','http-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
 'web/src/create-delivery.ts','web/src/create-delivery-entry.ts','web/tests/create-delivery-http-proof.mjs','web/tests/create-delivery-http-fixture.py',
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
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['create-delivery-entry','edit-delivery-entry','edit-context-entry','history-entry','read-entry','create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0);
let childOwner,server,origin,browser,host,passed=false,stdout='',stderr='';
let shutdown={forced_stop:false,shutdown_failed:false},stopped=false;const checks=[],traffic=[],sockets=new Set();
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 server=spawn(python,['-I','-B',join(capsule,owner,'web/tests/create-delivery-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});
 childOwner=watchChild(server);server.stdout.on('data',x=>stdout+=x);server.stderr.on('data',x=>stderr+=x);
 const ready=await readyChild(server,childOwner);origin=ready.origin;assert.equal(new URL(origin).hostname,'127.0.0.1');
 host=createServer(async(req,res)=>{
  const path=new URL(req.url,'http://local').pathname;
  try{
   if(path.startsWith('/api/v1/')){
    const chunks=[];for await(const bytes of req)chunks.push(bytes);
    const response=await fetch(origin+req.url,{method:req.method,headers:{authorization:req.headers.authorization??'', 'content-type':req.headers['content-type']??'application/json'},...(req.method==='GET'?{}:{body:Buffer.concat(chunks)})});
    traffic.push({path:req.url,method:req.method,status:response.status});res.writeHead(response.status,{'content-type':response.headers.get('content-type')??'application/json','cache-control':response.headers.get('cache-control')??''});res.end(Buffer.from(await response.arrayBuffer()));return;
   }
   if(path==='/'){res.setHeader('content-type','text/html');res.end('<!doctype html><title>Synthetic create delivery</title>');return;}
   const local=resolve(capsule,'.'+path);if(!local.startsWith(capsule+'/')){res.writeHead(404).end();return;}
   res.setHeader('content-type','text/javascript');res.end(readFileSync(local));
  }catch{res.writeHead(503).end();}
 });host.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});host.listen(0,'127.0.0.1');await once(host,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));
 browser=await require('@playwright/test').chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const page=await browser.newPage();await page.exposeFunction('fixtureMode',async mode=>{const response=await fetch(origin+'/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(response.status,200);return response.json();});const localOrigin='http://127.0.0.1:'+host.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===localOrigin?r.continue():r.abort());await page.goto(localOrigin);
 checks.push(...await page.evaluate(async ids=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {createCreateDeliveryEntry}=await import('/compiled/web/src/create-delivery-entry.js');
  const {readCapture}=await import('/compiled/web/src/read.js');const {editCapture}=await import('/compiled/web/src/edit.js');const {loadEditContext}=await import('/compiled/web/src/edit-context.js');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);},scope={account_id:ids.account,org_id:ids.org},session={account_id:ids.account,access_token:'synthetic-token'},execution={signal:new AbortController().signal,isCurrent:()=>true};
  const sdkSession={user:{id:ids.account},access_token:'synthetic-token'},auth={getSession:async()=>({data:{session:sdkSession},error:null}),refreshSession:async()=>({data:{session:sdkSession},error:null}),signOut:async()=>({error:null}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})};
  let n=0;const identities=()=>({capture_id:`dddddddd-dddd-4ddd-8ddd-${String(++n).padStart(12,'0')}`,operation_id:`eeeeeeee-eeee-4eee-8eee-${String(n).padStart(12,'0')}`});
  const setup=()=>{const checked_at=new Date().toISOString(),expires_at=new Date(Date.parse(checked_at)+604800000).toISOString(),observation=permission=>({account_id:ids.account,actor_id:ids.actor,membership_id:'7',authorization_scope:{kind:'organization',org_id:ids.org},resource_scope:{kind:'own_account',account_id:ids.account},permission,decision_id:ids.decision,checked_at,expires_at});return {schema_version:1,...scope,actor_id:ids.actor,membership_id:'7',read_observation:observation('kdg_capture.capture.read.own'),edit_observation:observation('kdg_capture.capture.edit.own'),create_all_observation:observation('kdg_capture.capture.create.all'),create_assigned_observation:null,create_state:'ready',children:[{child_id:ids.child,child_label:'Synthetic child',child_revision:'1',child_eligibility_ref:ids.eligibility_ref,create_permission:'kdg_capture.capture.create.all',assignment:null,checked_at,expires_at}],questionnaire:{questionnaire_id:ids.questionnaire,questionnaire_version_id:ids.version,questionnaire_version:'1',definition:ids.definition}};};
  const createLocal=async(name)=>{
   const store=await openHistoryStore(scope,{database:'actual-create-'+name}),ticket=await store.beginSetupRefresh();ok((await store.importProvision(setup(),ticket.ticket)).kind==='committed',name+'_setup');const opened=await store.openCreate(ids.child),identity=identities();
   const input={observation_date:'2026-10-26',captured_at:new Date().toISOString(),answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};ok((await store.saveCreate(opened.reviewed,identity,input)).kind==='saved_locally',name+'_actual_local_save');
   return {store,identity,input,pin:{...scope,action_id:identity.operation_id},name};
  };
  const entryFor=(local,request=fetch)=>createCreateDeliveryEntry({org:ids.org,auth,store:local.store,publish(){},beginSignIn:async()=>{},request});
  // Normal create: exact original bytes, one receipt, actual server attribution.
  await window.fixtureMode('all');const normal=await createLocal('normal');let entry=entryFor(normal),posts=0,sent;
  entry.dispose();entry=entryFor(normal,async(url,init)=>{if(init?.method==='POST'){posts++;sent=init.body;}return fetch(url,init);});
  try{await entry.start();const original=(await normal.store.lookupPreparedCreate(normal.pin)).serialized,result=await entry.deliver(normal.pin);ok(result.kind==='acknowledged'&&result.readback==='imported','actual_first_create_acknowledged');ok(posts===1&&sent===original,'actual_one_exact_frozen_post');const row=(await normal.store.read()).records[0];ok(row.create_status==='Synced'&&row.baseline.revision==='1'&&row.baseline.created_by===ids.actor&&!!row.baseline.created_at,'actual_server_baseline_and_attribution');}finally{entry.dispose();normal.store.close();}
  // Lost response, then a later server edit and a newer local saved edit.
  await window.fixtureMode('all');const lost=await createLocal('lost');let drop=true,lostPosts=0;entry=entryFor(lost,async(url,init)=>{const response=await fetch(url,init);if(init?.method==='POST'){lostPosts++;if(drop){drop=false;await response.text();throw TypeError('synthetic committed response loss');}}return response;});
  try{
   await entry.start();ok((await entry.deliver(lost.pin)).kind==='verification_unavailable','actual_committed_create_response_lost');
   const beforeRead=await readCapture(session,{...scope,capture_id:lost.identity.capture_id},execution);ok(beforeRead.kind==='loaded','actual_saved_create_server_read');await lost.store.importCurrentDetail(beforeRead.snapshot,{...scope,capture_id:lost.identity.capture_id});ok((await lost.store.read()).records[0].create_status==='Pending','actual_history_only_does_not_acknowledge');
   const edited=await editCapture(session,{...scope,capture_id:lost.identity.capture_id,command:{operation_id:'ffffffff-ffff-4fff-8fff-000000000001',command_version:1,expected_revision:'1',observation_date:lost.input.observation_date,answers:{...lost.input.answers,[ids.question]:{value:4}}}},execution);ok(edited.kind==='committed','actual_other_server_edit_before_create_recovery');
   const context=await loadEditContext(session,{...scope,capture_id:lost.identity.capture_id},execution);ok(context.kind==='loaded','actual_current_edit_context_for_newer_overlay');await lost.store.importEditContext(context.context,{...scope,capture_id:lost.identity.capture_id});const opened=await lost.store.openEdit(lost.identity.capture_id);ok(opened.kind==='opened','actual_newer_local_edit_opened');await lost.store.saveEdit(opened.reviewed,'ffffffff-ffff-4fff-8fff-000000000002',{observation_date:lost.input.observation_date,answers:{...lost.input.answers,[ids.question]:{value:5}}});
   await window.fixtureMode('create_denied');const recovered=await entry.deliver(lost.pin);ok(recovered.kind==='acknowledged'&&recovered.readback==='imported'&&lostPosts===1,'actual_recovery_after_creation_denial_without_post');
   const row=(await lost.store.read()).records[0],action=(await lost.store.readCreateActions()).actions[0];ok(row.baseline.revision==='2'&&action.delivery.receipt.result.revision==='1','actual_original_receipt_with_newer_current_baseline');ok(row.saved_edit.changes.answers[ids.question].value===5&&row.edit_status==='Pending'&&row.local_capture.answers[ids.question].value===1,'actual_create_readback_preserves_newer_edit_and_original_capture');
  }finally{entry.dispose();lost.store.close();}
  // Prior observed active eligibility supports ordinary later inactivity.
  await window.fixtureMode('all');const inactive=await createLocal('inactive');await window.fixtureMode('inactive_removed');entry=entryFor(inactive);try{await entry.start();ok((await entry.deliver(inactive.pin)).kind==='acknowledged','actual_prior_eligibility_inactive_child_delivered');}finally{entry.dispose();inactive.store.close();}
  // Current assignment rejection retains only this action and leaves reads usable.
  await window.fixtureMode('all');const assigned=await createLocal('assignment');await window.fixtureMode('assigned_removed');entry=entryFor(assigned);try{await entry.start();const result=await entry.deliver(assigned.pin);ok(result.kind==='error'&&result.error_id==='assignment_unavailable','actual_assignment_rejection');const row=(await assigned.store.read()).records[0],action=(await assigned.store.readCreateActions()).actions[0];ok(row.create_status==='Needs attention'&&action.delivery.attention==='assignment_unavailable','actual_assignment_attention_durable');ok((await assigned.store.read()).kind==='available','actual_assignment_rejection_preserves_read');
   await window.fixtureMode('all');const independent=await createLocal('assignment');try{const delivered=await entry.deliver(independent.pin);ok(delivered.kind==='acknowledged','actual_independent_same_partition_create_continues');const rows=(await assigned.store.read()).records;ok(rows.find(r=>r.local_capture.capture_id===assigned.identity.capture_id).create_status==='Needs attention'&&rows.find(r=>r.local_capture.capture_id===independent.identity.capture_id).create_status==='Synced','actual_selected_attention_does_not_block_other_record');}finally{independent.store.close();}}finally{entry.dispose();assigned.store.close();}
  // Creation-only denial probes current read, preserving cached data.
  await window.fixtureMode('all');const denied=await createLocal('denied');entry=entryFor(denied);try{await entry.start();await window.fixtureMode('create_denied');ok((await entry.deliver(denied.pin)).kind==='denied','actual_creation_permission_denied');ok((await denied.store.read()).kind==='available'&&(await denied.store.prepareCreate(denied.pin)).kind==='denied','actual_creation_denial_preserves_read_blocks_new_send');}finally{entry.dispose();denied.store.close();}
  // Force both actual handlers through unresolved recovery before competing POSTs.
  await window.fixtureMode('all');const concurrent=await createLocal('concurrent'),beforeConcurrent=await window.fixtureMode();let waiting=0,release;const barrier=new Promise(resolve=>release=resolve);let concurrentPosts=0;
  entry=entryFor(concurrent,async(url,init)=>{const response=await fetch(url,init);if(url.startsWith('/api/v1/operations/')){waiting++;if(waiting===2)release();await barrier;}if(init?.method==='POST')concurrentPosts++;return response;});
  try{await entry.start();const results=await Promise.all([entry.deliver(concurrent.pin),entry.deliver(concurrent.pin)]);ok(results.every(r=>r.kind==='acknowledged')&&concurrentPosts===2,'actual_competing_explicit_handlers_acknowledge');const after=await window.fixtureMode();ok(Object.keys(after.captures).length===Object.keys(beforeConcurrent.captures).length+1&&after.outcomes===beforeConcurrent.outcomes+1&&after.history===beforeConcurrent.history+1,'actual_competing_posts_one_create_receipt_history');}finally{entry.dispose();concurrent.store.close();}
  // Recovery read denial locks protected local display without deleting the intent.
  await window.fixtureMode('all');const readDenied=await createLocal('read-denied');entry=entryFor(readDenied);try{await entry.start();await window.fixtureMode('deny');ok((await entry.deliver(readDenied.pin)).kind==='denied'&&(await readDenied.store.read()).kind!=='available','actual_read_denial_locks_partition');}finally{entry.dispose();readDenied.store.close();}
  await window.fixtureMode('all');return checks;
 },ready.ids));
 const response=await fetch(origin+'/__fixture');assert.equal(response.status,200);const state=await response.json();assert.equal(Object.keys(state.captures).length,5);assert.equal(state.outcomes,6);assert.equal(state.history,6);assert.equal(state.acquired,state.released);checks.push('actual_five_creates_one_edit_balanced_storage');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(state,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(browser)await browser.close();if(host){const done=new Promise(r=>host.close(r));for(const socket of sockets)socket.destroy();await done;}
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['actual synthetic capture/recovery/read/context/edit HTTP plus real Chromium IDB; Auth/Access and storage are fixtures','strict synthetic setup uses existing actual Provision contract already independently qualified','no native permissions/rollback, real account or startup/sender activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
