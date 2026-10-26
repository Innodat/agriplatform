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
 'web/tests/persistence-child.mjs','web/tests/persistence-http-proof.mjs','web/tests/persistence-http-fixture.py','web/tsconfig.auth.json',
 'web/src/create.ts','web/src/create-entry.ts','web/src/edit.ts','web/src/edit-entry.ts','web/src/recovery.ts','web/src/recovery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/entry.ts','web/src/auth-public-input.ts',
 'contracts/create-generated/types.gen.ts','contracts/edit-generated/types.gen.ts','contracts/recovery-generated/types.gen.ts','contracts/generated/types.gen.ts',
 'api/main.py','api/context.py','api/safe_errors.py','api/capture_commands.py','api/questionnaire.py','write-tools/transaction_context.py',
 ...['create_http','edit_http','recovery_http','create_openapi','edit_openapi','recovery_openapi','capture_create_handler','capture_edit_handler','capture_create','capture_edit','operation_recovery','operation_outcomes'].map(x=>'write-candidate/'+x+'.py')
].map(x=>owner+'/'+x);
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
writeFileSync(join(capsule,'package.json'),'{"private":true,"type":"module"}\n');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'),'dir');
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
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
 const {createCreateEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/create-entry.js')));
 const {createEditEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/edit-entry.js')));
 const {createRecoveryEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/recovery-entry.js')));
 const session={user:{id:ids.account},access_token:'synthetic-token'};
 function entry(factory,adapter=request){let callback;const auth={getSession:async()=>({data:{session},error:null}),refreshSession:async()=>({data:{session},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return{data:{subscription:{unsubscribe(){}}}};}};const owner=factory({org:ids.org,auth,publish(){},beginSignIn:async()=>{},request:adapter});return{owner,replace(){callback('TOKEN_REFRESHED',{...session,access_token:'synthetic-replacement'});}};}
 const create=entry(createCreateEntry),edit=entry(createEditEntry),recover=entry(createRecoveryEntry);
 try{
  await Promise.all([create.owner.start(),edit.owner.start(),recover.owner.start()]);
  const command={operation_id:ids.create,command_version:1,capture_id:ids.capture,child_id:ids.child,questionnaire_version_id:ids.version,observation_date:'2026-10-26',captured_at:'2026-10-26T10:00:00Z',child_eligibility_ref:'synthetic',answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};
  const pending={account_id:ids.account,org_id:ids.org,command};
  const created=await create.owner.create(pending);assert.equal(created.kind,'committed');assert.equal(created.receipt.result.revision,'1');checks.push('create1_over_loopback');
  assert.equal((await create.owner.create(pending)).receipt.result.revision,'1');
  const changed={operation_id:ids.edit,command_version:1,expected_revision:'1',observation_date:'2026-10-26',answers:{...command.answers,[ids.question]:{value:2}}};
  const editPending={account_id:ids.account,org_id:ids.org,capture_id:ids.capture,command:changed};
  const edited=await edit.owner.edit(editPending);assert.equal(edited.kind,'committed');assert.equal(edited.receipt.result.revision,'2');
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
   assert.equal((await fixture()).acquired,before.acquired);assert.deepEqual(pending,input);
  }
  await fixture('assigned');assert.equal((await create.owner.create(pending)).kind,'committed');
  await fixture('assigned_removed');assert.deepEqual(await create.owner.create(pending),{kind:'error',status:403,error_id:'assignment_unavailable'});
  assert.equal((await recover.owner.recover(lookup(ids.create,'capture.create'))).kind,'committed');
  checks.push('current_authority_precedes_checkout_stored_assignment_and_verified_unresolved');
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
  writeFileSync(join(proof,'integration-state.json'),JSON.stringify(state,null,2)+'\n');
  passed=true;
 }finally{create.owner.dispose();edit.owner.dispose();recover.owner.dispose();}
}finally{
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);
 stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);
 const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,child:childOwner?.state??null,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['synthetic Access and storage; no native permission or rollback evidence','candidate only; no active browser/API startup or real account']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');process.stdout.write(JSON.stringify({passed:result.passed,proof})+'\n');if(!result.passed)process.exitCode=1;
}
