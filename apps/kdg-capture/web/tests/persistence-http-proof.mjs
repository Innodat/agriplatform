// Selected-source synthetic loopback proof; no active API/browser entry is started.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync} from 'node:fs';
import {resolve,join,dirname} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {watchChild,readyChild,stopChild} from './persistence-child.mjs';
import {createHash,randomUUID} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=process.cwd(),owner='apps/kdg-capture',hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v26.11.1');
const retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(JSON.parse(readFileSync(join(retained,'node_modules/typescript/package.json'))).version,'7.0.2');
const proof=join(root,'platform/deployment/.local/kdg-persistence-http-path-20261026','network-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
 'web/src/own-observation.ts',
 'web/src/edit-context.ts','web/src/edit-context-entry.ts','contracts/edit-context-generated/types.gen.ts','web/tests/persistence-child.mjs','web/tests/persistence-http-proof.mjs','web/tests/persistence-http-fixture.py','web/tsconfig.auth.json',
 'web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history-download.ts','web/src/history.ts','web/src/history-entry.ts','web/src/read-validation.ts','web/src/read.ts','web/src/read-entry.ts','web/src/create.ts','web/src/create-entry.ts','web/src/edit.ts','web/src/edit-entry.ts','web/src/recovery.ts','web/src/recovery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/entry.ts','web/src/auth-public-input.ts',
 'contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/create-generated/types.gen.ts','contracts/edit-generated/types.gen.ts','contracts/recovery-generated/types.gen.ts','contracts/generated/types.gen.ts',
 'api/main.py','api/context.py','api/safe_errors.py','api/capture_commands.py','api/questionnaire.py','write-tools/transaction_context.py',
 ...['own_observation_openapi','edit_context','edit_context_http','edit_context_openapi','history_http','history_openapi','capture_history','read_http','read_openapi','capture_read','create_http','edit_http','recovery_http','create_openapi','edit_openapi','recovery_openapi','capture_create_handler','capture_edit_handler','capture_create','capture_edit','operation_recovery','operation_outcomes'].map(x=>'write-candidate/'+x+'.py')
].map(x=>owner+'/'+x);
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
writeFileSync(join(capsule,'package.json'),'{"private":true,"type":"module"}\n');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['edit-context-entry','history-entry','read-entry','create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0);
let childOwner,shutdown={forced_stop:false,stop_signal:null,shutdown_failed:false},origin,server,passed=false,stopped=false,stderr='',stdout='';const checks=[],traffic=[];
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 server=spawn(python,['-I','-B',join(capsule,owner,'web/tests/persistence-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});
 childOwner=watchChild(server);
 server.stdout.on('data',bytes=>{stdout+=bytes;});server.stderr.on('data',bytes=>{stderr+=bytes;});
 const ready=await readyChild(server,childOwner);
 const {ids}=ready;origin=ready.origin;assert.equal(new URL(origin).hostname,'127.0.0.1');
 const request=async(url,init)=>{assert.ok(url.startsWith('/api/v1/'));const response=await fetch(origin+url,init);traffic.push({path:url,method:init?.method??'GET',status:response.status});return response;};
 const fixture=async mode=>{const r=await fetch(origin+'/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(r.status,200);return r.json();};
 const {createEditContextEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/edit-context-entry.js')));
 const {createHistoryEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/history-entry.js')));
 const {createReadEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/read-entry.js')));
 const {createCreateEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/create-entry.js')));
 const {createEditEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/edit-entry.js')));
 const {createRecoveryEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/recovery-entry.js')));
 const session={user:{id:ids.account},access_token:'synthetic-token'};
 function entry(factory,adapter=request){let callback;const auth={getSession:async()=>({data:{session},error:null}),refreshSession:async()=>({data:{session},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return{data:{subscription:{unsubscribe(){}}}};}};const owner=factory({org:ids.org,auth,publish(){},beginSignIn:async()=>{},request:adapter});return{owner,replace(){callback('TOKEN_REFRESHED',{...session,access_token:'synthetic-replacement'});}};}
 const editContext=entry(createEditContextEntry),create=entry(createCreateEntry),edit=entry(createEditEntry),recover=entry(createRecoveryEntry),read=entry(createReadEntry),history=entry(createHistoryEntry);
 try{
  await Promise.all([editContext.owner.start(),create.owner.start(),edit.owner.start(),recover.owner.start(),read.owner.start(),history.owner.start()]);
  const command={operation_id:ids.create,command_version:1,capture_id:ids.capture,child_id:ids.child,questionnaire_version_id:ids.version,observation_date:'2026-10-26',captured_at:'2026-10-26T10:00:00Z',child_eligibility_ref:'synthetic',answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};
  const pending={account_id:ids.account,org_id:ids.org,command};
  const created=await create.owner.create(pending);assert.equal(created.kind,'committed');assert.equal(created.receipt.result.revision,'1');checks.push('create1_over_loopback');
  const readPending={account_id:ids.account,org_id:ids.org,capture_id:ids.capture};
  const firstRead=await read.owner.read(readPending);assert.equal(firstRead.kind,'loaded');assert.equal(firstRead.snapshot.revision,'1');assert.deepEqual(firstRead.snapshot.answers,command.answers);assert.equal(firstRead.snapshot.captured_at,command.captured_at);assert.equal(firstRead.snapshot.child_label,'Synthetic child');assert.ok(Object.isFrozen(firstRead.snapshot.definition.questions));
  const originalDefinition=firstRead.snapshot.definition;
  const beforeContext=await fixture();const firstContext=await editContext.owner.load(readPending);
  assert.equal(firstContext.kind,'loaded');assert.deepEqual(firstContext.context.capture,firstRead.snapshot);
  assert.deepEqual(firstContext.context.editable_fields,['observation_date','answers']);
  assert.equal(firstContext.context.read_observation.permission,'kdg_capture.capture.read.own');assert.equal(firstContext.context.edit_observation.permission,'kdg_capture.capture.edit.own');
  const afterContext=await fixture();assert.equal(afterContext.outcomes,beforeContext.outcomes);assert.equal(afterContext.history,beforeContext.history);assert.deepEqual(afterContext.captures,beforeContext.captures);
  checks.push('edit_context_after_create_full_original_and_independent_observations_without_writes');
  assert.equal((await create.owner.create(pending)).receipt.result.revision,'1');
  const changed={operation_id:ids.edit,command_version:1,expected_revision:'1',observation_date:'2026-10-26',answers:{...command.answers,[ids.question]:{value:2}}};
  const editPending={account_id:ids.account,org_id:ids.org,capture_id:ids.capture,command:changed};
  const edited=await edit.owner.edit(editPending);assert.equal(edited.kind,'committed');assert.equal(edited.receipt.result.revision,'2');
  const currentRead=await read.owner.read(readPending);assert.equal(currentRead.kind,'loaded');assert.equal(currentRead.snapshot.revision,'2');assert.deepEqual(currentRead.snapshot.answers,changed.answers);assert.deepEqual(currentRead.snapshot.definition,originalDefinition);assert.equal(created.receipt.result.revision,'1');assert.equal(currentRead.snapshot.owner_actor_id,ids.actor);assert.equal(currentRead.snapshot.created_by,ids.actor);assert.equal(currentRead.snapshot.updated_by,ids.actor);checks.push('protected_current_read_after_create_and_edit_preserves_original_definition_and_receipt');
  const currentContext=await editContext.owner.load(readPending);assert.equal(currentContext.kind,'loaded');assert.deepEqual(currentContext.context.capture,currentRead.snapshot);assert.deepEqual(currentContext.context.capture.definition,originalDefinition);
  for(const [mode,error_id,status] of [['edit_denied','access_denied',403],['edit_identity','authorization_unavailable',503],['mismatch','authorization_unavailable',503]]){const before=await fixture(mode);assert.deepEqual(await editContext.owner.load(readPending),{kind:'error',status,error_id});assert.equal((await fixture()).acquired,before.acquired);}
  await fixture('inactive_removed');assert.equal((await editContext.owner.load(readPending)).kind,'loaded');await fixture('all');
  checks.push('edit_context_current_revision_edit_denial_identity_scope_and_inactive_original_version');
  assert.equal((await edit.owner.edit(editPending)).receipt.result.revision,'2');
  const lookup=(operation_id,command_type)=>({account_id:ids.account,org_id:ids.org,operation_id,command_type,...(command_type==='capture.edit'?{capture_id:ids.capture}:{})});
  assert.deepEqual((await recover.owner.recover(lookup(ids.create,'capture.create'))).receipt,created.receipt);
  assert.deepEqual((await recover.owner.recover(lookup(ids.edit,'capture.edit'))).receipt,edited.receipt);
  const noop=await edit.owner.edit({...editPending,command:{...changed,operation_id:ids.noop,expected_revision:'2'}});assert.equal(noop.receipt.result.revision,'2');
  let state=await fixture();assert.equal(state.outcomes,3);assert.equal(state.history,2);assert.equal(Object.keys(state.captures).length,1);
  checks.push('create_edit_original_recovery_duplicate_and_noop');
  const conflict=await edit.owner.edit({...editPending,command:{...changed,operation_id:ids.unknown}});
  assert.deepEqual(conflict,{kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'2'});
  assert.equal((await create.owner.create({...pending,command:{...command,capture_id:ids.unknown}})).kind,'invalid_response');
  assert.equal((await edit.owner.edit({...editPending,capture_id:ids.unknown})).kind,'invalid_response');
  checks.push('stale_revision_and_wrong_original_receipt_target');
  assert.equal((await recover.owner.recover(lookup(ids.unknown,'capture.create'))).kind,'unresolved');
  for(const [mode,status,error_id] of [['deny',403,'access_denied'],['expired',401,'authentication_required'],['mismatch',503,'authorization_unavailable'],['outage',503,'authorization_unavailable']]){
   const before=await fixture(mode),input=structuredClone(pending);
   assert.deepEqual(await create.owner.create(pending),{kind:'error',status,error_id});
   const result=await recover.owner.recover(lookup(ids.unknown,'capture.create'));assert.equal(result.kind,'error');
   assert.deepEqual(await read.owner.read(readPending),{kind:'error',status,error_id});
   assert.equal((await fixture()).acquired,before.acquired);assert.deepEqual(pending,input);
  }
  await fixture('assigned');assert.equal((await create.owner.create(pending)).kind,'committed');
  await fixture('assigned_removed');assert.deepEqual(await create.owner.create(pending),{kind:'error',status:403,error_id:'assignment_unavailable'});
  assert.equal((await recover.owner.recover(lookup(ids.create,'capture.create'))).kind,'committed');
  checks.push('current_authority_precedes_checkout_stored_assignment_and_verified_unresolved');
  await fixture('inactive_removed');assert.equal((await read.owner.read(readPending)).kind,'loaded');
  await fixture('foreign_read');const foreignRead=await read.owner.read(readPending);assert.deepEqual(foreignRead,{kind:'error',status:404,error_id:'capture_unavailable'});
  await fixture('all');assert.deepEqual(await read.owner.read({...readPending,capture_id:ids.unknown}),foreignRead);
  const beforeReadFailures=await fixture();
  for(const mode of ['fail_acquire','fail_sql','fail_commit','fail_release','invalid_detail']){await fixture(mode);assert.deepEqual(await read.owner.read(readPending),{kind:'error',status:503,error_id:'capture_read_unavailable'});}
  const afterReadFailures=await fixture('all');assert.deepEqual(afterReadFailures.captures,beforeReadFailures.captures);assert.equal(afterReadFailures.outcomes,beforeReadFailures.outcomes);assert.equal(afterReadFailures.history,beforeReadFailures.history);
  checks.push('read_inactive_unassigned_original_owner_foreign_missing_and_safe_failures');
  await fixture('all');const beforeMalformed=await fixture();
  for(const [url,init,status] of [
   ['/api/v1/captures',{method:'POST',body:'{}'},401],
   ['/api/v1/captures?org_id=x',{method:'POST',headers:{Authorization:'Bearer synthetic','Content-Type':'application/json'},body:JSON.stringify(command)},422],
   ['/api/v1/captures',{method:'POST',headers:{Authorization:'Bearer synthetic','Content-Type':'application/json'},body:'{"command_version":1,"command_version":1}'},422],
   ['/api/v1/captures',{method:'POST',headers:{Authorization:'Bearer synthetic','Content-Type':'application/json'},body:JSON.stringify({...command,command_version:2})},422],
   ['/api/v1/captures',{method:'POST',headers:{Authorization:'Bearer synthetic','Content-Type':'application/json'},body:'x'.repeat(131073)},422],
  ]){const r=await fetch(origin+url,init);assert.equal(r.status,status);assert.equal(r.headers.get('cache-control'),'private, no-store');assert.ok(!JSON.stringify(await r.json()).includes('synthetic-token'));}
  assert.equal((await fixture()).acquired,beforeMalformed.acquired);checks.push('strict_auth_body_selectors_version_before_storage');
  let releaseCommand;
  const freshId=n=>n.toString(16).padStart(8,'0')+'-bbbb-4bbb-8bbb-'+n.toString(16).padStart(12,'0');
  for(const [i,mode] of ['fail_acquire','fail_sql','fail_commit','fail_release'].entries()){
   const original=await fixture(mode);
   const fresh={...command,operation_id:freshId(i+20),capture_id:freshId(i+40)};
   const result=await create.owner.create({...pending,command:fresh});assert.equal(result.kind,'error');assert.equal(result.error_id,'internal_error');
   const after=await fixture();
   if(mode==='fail_release'){
    releaseCommand=fresh;assert.equal(after.outcomes,original.outcomes+1);assert.equal(after.history,original.history+1);assert.ok(after.captures[fresh.capture_id]);
   }else{assert.deepEqual(after.captures,original.captures);assert.equal(after.outcomes,original.outcomes);assert.equal(after.history,original.history);}
  }
  await fixture('all');
  const released=await recover.owner.recover(lookup(releaseCommand.operation_id,'capture.create'));
  assert.deepEqual(released,{kind:'committed',receipt:{operation_id:releaseCommand.operation_id,command_type:'capture.create',command_version:1,status:'committed',result:{capture_id:releaseCommand.capture_id,revision:'1'}}});
  assert.deepEqual(await create.owner.create({...pending,command:releaseCommand}),released);
  assert.deepEqual((await recover.owner.recover(lookup(ids.create,'capture.create'))).receipt,created.receipt);
  checks.push('fresh_acquisition_sql_commit_release_failure_no_ack_release_commit_recovered_once');
  const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
  for(const phase of ['headers','body']){
   const reached=deferred(),release=deferred();let held=true;
   const adapter=async(url,init)=>{
    const r=await request(url,init);if(!url.startsWith('/api/v1/captures')||!held)return r;
    held=false;
    if(phase==='headers'){reached.resolve();await release.promise;return r;}
    const bytes=new Uint8Array(await r.arrayBuffer());
    return new Response(new ReadableStream({async pull(c){reached.resolve();await release.promise;try{c.enqueue(bytes);c.close();}catch{}}}),{status:r.status,headers:r.headers});
   };
   const old=entry(createCreateEntry,adapter);await old.owner.start();const work=old.owner.create(pending);await reached.promise;
   old.replace();assert.equal((await work).kind,'superseded');release.resolve();
   for(let i=0;i<50&&old.owner.state().kind!=='authorized';i++)await new Promise(r=>setTimeout(r,2));
   assert.equal((await old.owner.create(pending)).kind,'committed');old.owner.dispose();
  }
  checks.push('auth_replacement_late_headers_and_body_new_execution_usable');
  state=await fixture();assert.equal(state.acquired,state.released);assert.equal(state.outcomes,4);assert.equal(state.history,3);assert.equal(state.captures[ids.capture].revision,2);

  await fixture('history_seed');
  const historyPending={account_id:ids.account,org_id:ids.org,from_date:'2026-10-01',to_date:'2026-10-26',limit:2};
  const all=[],pages=[];let historyCursor;
  do{
   const result=await history.owner.history({...historyPending,...(historyCursor?{cursor:historyCursor}:{})});
   assert.equal(result.kind,'loaded');assert.equal(result.page.account_id,ids.account);assert.equal(result.page.org_id,ids.org);
   pages.push(result.page);all.push(...result.page.items);historyCursor=result.page.next_cursor;
  }while(historyCursor);
  assert.ok(pages.length>=4);assert.equal(new Set(all.map(item=>item.capture_id)).size,all.length);
  assert.equal(all.filter(item=>item.capture_id.endsWith('-0000000000c9')).length,1);
  assert.ok(all.every(item=>item.owner_account_id===ids.account&&item.org_id===ids.org&&item.observation_date>='2026-10-01'&&item.observation_date<='2026-10-26'));
  const second=all.find(item=>item.questionnaire_version==='2');assert.equal(second.definition.questions[0].label,'Second original definition');
  assert.equal(all.find(item=>item.capture_id===ids.capture).revision,'2');
  const tieA=all.findIndex(item=>item.capture_id.startsWith('000000c9-')),tieB=all.findIndex(item=>item.capture_id.startsWith('000000ca-'));
  assert.ok(tieA<tieB,'microseconds precede inverse UUID tie breaker');
  assert.ok(Object.isFrozen(pages[0].items[0].definition.questions));
  checks.push('history_row_pages_inclusive_dates_original_versions_microseconds_no_loss');
  const beforeHistoryDenial=await fixture('deny');
  assert.deepEqual(await history.owner.history({...historyPending,cursor:pages[0].next_cursor}),{kind:'error',status:403,error_id:'access_denied'});
  assert.equal((await fixture()).acquired,beforeHistoryDenial.acquired);
  await fixture('foreign_read');const foreignPage=await history.owner.history(historyPending);assert.equal(foreignPage.kind,'invalid_response');
  await fixture('inactive_removed');assert.equal((await history.owner.history(historyPending)).kind,'loaded');
  checks.push('history_current_authority_before_checkout_and_empty_scope_validation');
  await fixture('history_bytes');
  const bytePending={...historyPending,from_date:'2026-10-20',to_date:'2026-10-20',limit:100};
  const byteFirst=await history.owner.history(bytePending);assert.equal(byteFirst.kind,'loaded');assert.equal(byteFirst.page.items.length,4);assert.ok(byteFirst.page.next_cursor);
  const byteLast=await history.owner.history({...bytePending,cursor:byteFirst.page.next_cursor});assert.equal(byteLast.kind,'loaded');assert.equal(byteLast.page.items.length,1);assert.equal(byteLast.page.next_cursor,null);
  assert.equal(new Set([...byteFirst.page.items,...byteLast.page.items].map(item=>item.capture_id)).size,5);
  checks.push('history_actual_utf8_byte_continuation_without_skipping');
  for(const phase of ['headers','body']){
   const reached=deferred(),release=deferred();let held=true;
   const adapter=async(url,init)=>{
    const r=await request(url,init);if(!url.startsWith('/api/v1/captures?')||!held)return r;held=false;
    if(phase==='headers'){reached.resolve();await release.promise;return r;}
    const bytes=new Uint8Array(await r.arrayBuffer());
    return new Response(new ReadableStream({async pull(c){reached.resolve();await release.promise;try{c.enqueue(bytes);c.close();}catch{}}}),{status:r.status,headers:r.headers});
   };
   const old=entry(createHistoryEntry,adapter);await old.owner.start();const work=old.owner.history(historyPending);await reached.promise;
   old.replace();assert.equal((await work).kind,'superseded');release.resolve();
   for(let i=0;i<50&&old.owner.state().kind!=='authorized';i++)await new Promise(r=>setTimeout(r,2));
   assert.equal((await old.owner.history(historyPending)).kind,'loaded');old.owner.dispose();
  }
  checks.push('history_auth_replacement_late_headers_and_body_fenced');
  for(const phase of ['headers','body']){
   const reached=deferred(),release=deferred();let held=true;
   const adapter=async(url,init)=>{const r=await request(url,init);if(!url.endsWith('/edit-context')||!held)return r;held=false;
    if(phase==='headers'){reached.resolve();await release.promise;return r;}
    const bytes=new Uint8Array(await r.arrayBuffer());return new Response(new ReadableStream({async pull(c){reached.resolve();await release.promise;try{c.enqueue(bytes);c.close();}catch{}}}),{status:r.status,headers:r.headers});};
   const old=entry(createEditContextEntry,adapter);await old.owner.start();const work=old.owner.load(readPending);await reached.promise;old.replace();assert.equal((await work).kind,'superseded');release.resolve();
   for(let i=0;i<50&&old.owner.state().kind!=='authorized';i++)await new Promise(r=>setTimeout(r,2));assert.equal((await old.owner.load(readPending)).kind,'loaded');old.owner.dispose();
  }
  checks.push('edit_context_auth_replacement_late_headers_and_body_fenced');
  state=await fixture();assert.equal(state.acquired,state.released);assert.equal(state.outcomes,4);assert.equal(state.history,3);
  writeFileSync(join(proof,'integration-state.json'),JSON.stringify(state,null,2)+'\n');
  passed=true;
 }finally{editContext.owner.dispose();create.owner.dispose();edit.owner.dispose();recover.owner.dispose();read.owner.dispose();history.owner.dispose();}
}finally{
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);
 stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);
 const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,child:childOwner?.state??null,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['synthetic Access and storage; no native permission or rollback evidence','candidate only; no active browser/API startup or real account']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify({passed:result.passed,proof})+'\n');if(!result.passed)process.exitCode=1;
}
