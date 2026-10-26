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
const proof=join(root,'platform/deployment/.local/kdg-pending-create-edit-20261026','http-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
 'web/src/create-delivery.ts','web/src/create-delivery-entry.ts','web/tests/pending-create-edit-http-proof.mjs','web/tests/create-delivery-http-fixture.py',
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
  const {createEditDeliveryEntry}=await import('/compiled/web/src/edit-delivery-entry.js');const {readCapture}=await import('/compiled/web/src/read.js');const {editCapture}=await import('/compiled/web/src/edit.js');const {loadEditContext}=await import('/compiled/web/src/edit-context.js');
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
  const editFor=(local,request=fetch)=>createEditDeliveryEntry({org:ids.org,auth,store:local.store,publish(){},beginSignIn:async()=>{},request});
  let editCounter=0;const editID=()=>`ffffffff-ffff-4fff-8fff-${String(++editCounter).padStart(12,'0')}`;
  const saveProposal=async(local,rating)=>{const opened=await local.store.openEdit(local.identity.capture_id);ok(opened.kind==='opened','pending_original_local_edit_opened');const action_id=editID(),changes={observation_date:local.input.observation_date,answers:{...local.input.answers,[ids.question]:{value:rating}}};const saved=await local.store.saveEdit(opened.reviewed,action_id,changes);ok(saved.kind==='saved_locally','pending_completed_edit_saved_atomically');return {pin:{...scope,action_id},changes};};
  // Actual local create and two completed edits before the server knows the capture.
  await window.fixtureMode('all');const ordered=await createLocal('pending-ordered');let createEntry=entryFor(ordered),editEntry=editFor(ordered);
  try{
   const original=(await ordered.store.lookupPreparedCreate(ordered.pin)).serialized;
   const first=await saveProposal(ordered,4),second=await saveProposal(ordered,5);
   const pendingRow=(await ordered.store.read()).records[0];ok(!pendingRow.baseline&&pendingRow.local_capture.answers[ids.question].value===1,'pending_no_fabricated_server_baseline');
   ok((await ordered.store.prepareEdit(first.pin.action_id)).kind==='blocked'&&(await ordered.store.prepareEdit(second.pin.action_id)).kind==='blocked','pending_descendants_block_without_predecessor_receipts');
   ok((await ordered.store.lookupPreparedCreate(ordered.pin)).serialized===original,'pending_edits_preserve_original_create_bytes');
   await createEntry.start();await editEntry.start();ok((await createEntry.deliver(ordered.pin)).kind==='acknowledged','pending_original_create_delivered');
   const prepared=await ordered.store.prepareEdit(first.pin.action_id);ok(prepared.kind==='prepared'&&prepared.pending.command.expected_revision==='1','pending_first_edit_uses_actual_create_receipt');
   ok((await ordered.store.prepareEdit(second.pin.action_id)).kind==='blocked','pending_second_edit_waits_for_first_receipt');
   ok((await editEntry.deliver(first.pin)).kind==='acknowledged','pending_first_edit_delivered');
   let row=(await ordered.store.read()).records[0];ok(row.saved_edit.changes.answers[ids.question].value===5&&row.edit_status==='Pending','pending_first_ack_preserves_later_overlay');
   const next=await ordered.store.prepareEdit(second.pin.action_id);ok(next.kind==='prepared'&&next.pending.command.expected_revision==='2','pending_second_uses_actual_first_edit_receipt');
   ok((await editEntry.deliver(second.pin)).kind==='acknowledged','pending_second_edit_delivered');row=(await ordered.store.read()).records[0];ok(row.baseline.revision==='3'&&row.baseline.answers[ids.question].value===5&&row.edit_status==='Synced'&&row.local_capture.answers[ids.question].value===1,'pending_final_readback_original_and_latest_retained');
   const detail=await readCapture(session,{...scope,capture_id:ordered.identity.capture_id},execution);ok(detail.kind==='loaded'&&detail.snapshot.revision==='3'&&detail.snapshot.created_by===ids.actor,'pending_actual_server_revision_and_attribution');
  }finally{createEntry.dispose();editEntry.dispose();ordered.store.close();}
  // The create receipt resolves ordering even when the response was lost and readback fails.
  await window.fixtureMode('all');const uncertain=await createLocal('pending-uncertain');let posts=0,drop=true,failDetail=true;
  createEntry=entryFor(uncertain,async(url,init)=>{if(url.startsWith('/api/v1/captures/')&&(!init?.method||init.method==='GET')&&failDetail)throw TypeError('synthetic readback outage');const response=await fetch(url,init);if(init?.method==='POST'){posts++;if(drop){drop=false;await response.text();throw TypeError('synthetic committed response loss');}}return response;});editEntry=editFor(uncertain);
  try{
   const proposal=await saveProposal(uncertain,4);await createEntry.start();await editEntry.start();ok((await createEntry.deliver(uncertain.pin)).kind==='verification_unavailable','pending_create_committed_response_loss');ok((await uncertain.store.prepareEdit(proposal.pin.action_id)).kind==='blocked','pending_lost_create_does_not_guess_predecessor');
   const recovered=await createEntry.deliver(uncertain.pin);ok(recovered.kind==='acknowledged'&&recovered.readback==='unavailable'&&posts===1,'pending_receipt_recovery_without_repeat_create_or_readback');ok(!(await uncertain.store.read()).records[0].baseline,'pending_receipt_does_not_fabricate_content');
   const prepared=await uncertain.store.prepareEdit(proposal.pin.action_id);ok(prepared.kind==='prepared'&&prepared.pending.command.expected_revision==='1','pending_receipt_without_readback_resolves_predecessor');ok((await editEntry.deliver(proposal.pin)).kind==='acknowledged','pending_receipt_only_predecessor_edit_delivered');const row=(await uncertain.store.read()).records[0];ok(row.baseline.revision==='2'&&row.baseline.answers[ids.question].value===4,'pending_receipt_only_actual_edit_readback');
  }finally{createEntry.dispose();editEntry.dispose();uncertain.store.close();}
  // An unrelated server edit cannot supply a newer expected revision to our saved proposal.
  await window.fixtureMode('all');const advanced=await createLocal('pending-advanced');createEntry=entryFor(advanced);editEntry=editFor(advanced);
  try{
   const proposal=await saveProposal(advanced,5);await createEntry.start();await editEntry.start();ok((await createEntry.deliver(advanced.pin)).kind==='acknowledged','pending_conflict_original_create_delivered');
   const foreign=await editCapture(session,{...scope,capture_id:advanced.identity.capture_id,command:{operation_id:editID(),command_version:1,expected_revision:'1',observation_date:advanced.input.observation_date,answers:{...advanced.input.answers,[ids.question]:{value:4}}}},execution);ok(foreign.kind==='committed','pending_unrelated_server_progress');const detail=await readCapture(session,{...scope,capture_id:advanced.identity.capture_id},execution);ok(detail.kind==='loaded','pending_unrelated_progress_readback');await advanced.store.importCurrentDetail(detail.snapshot,{...scope,capture_id:advanced.identity.capture_id});
   const prepared=await advanced.store.prepareEdit(proposal.pin.action_id);ok(prepared.kind==='blocked','pending_unrelated_progress_does_not_rebase');const row=(await advanced.store.read()).records[0];ok(row.edit_status==='Needs attention'&&row.saved_edit.changes.answers[ids.question].value===5&&row.baseline.revision==='2','pending_unrelated_progress_preserves_proposal_for_attention');
  }finally{createEntry.dispose();editEntry.dispose();advanced.store.close();}
  // A known rejected original create never permits a descendant PUT.
  await window.fixtureMode('all');const rejected=await createLocal('pending-rejected');let rejectedPuts=0;createEntry=entryFor(rejected);editEntry=editFor(rejected,async(url,init)=>{if(init?.method==='PUT')rejectedPuts++;return fetch(url,init);});
  try{
   const original=(await rejected.store.lookupPreparedCreate(rejected.pin)).serialized,proposal=await saveProposal(rejected,4);await createEntry.start();await editEntry.start();await window.fixtureMode('assigned_removed');const denied=await createEntry.deliver(rejected.pin);ok(denied.kind==='error'&&denied.error_id==='assignment_unavailable','pending_original_create_known_rejection');
   ok((await editEntry.deliver(proposal.pin)).kind==='blocked'&&rejectedPuts===0,'pending_rejected_create_descendant_never_puts');const row=(await rejected.store.read()).records[0],action=(await rejected.store.readEditActions()).actions.find(a=>a.action_id===proposal.pin.action_id);ok(row.create_status==='Needs attention'&&row.saved_edit.action_id===proposal.pin.action_id&&action.changes.answers[ids.question].value===4,'pending_rejected_create_keeps_readable_saved_edit');ok((await rejected.store.lookupPreparedCreate(rejected.pin)).serialized===original,'pending_rejected_create_identity_and_bytes_preserved');
  }finally{createEntry.dispose();editEntry.dispose();rejected.store.close();}
  await window.fixtureMode('all');return checks;
 },ready.ids));
 const response=await fetch(origin+'/__fixture');assert.equal(response.status,200);const state=await response.json();assert.equal(Object.keys(state.captures).length,3);assert.equal(state.outcomes,7);assert.equal(state.history,7);assert.equal(state.acquired,state.released);checks.push('actual_three_creates_four_edits_balanced_storage');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(state,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(browser)await browser.close();if(host){const done=new Promise(r=>host.close(r));for(const socket of sockets)socket.destroy();await done;}
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['actual synthetic capture/recovery/read/context/edit HTTP plus real Chromium IDB; Auth/Access and storage are fixtures','strict synthetic setup uses existing actual Provision contract already independently qualified','no native permissions/rollback, real account or startup/sender activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
