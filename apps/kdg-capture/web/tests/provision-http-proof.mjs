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
const proof=join(root,'platform/deployment/.local/kdg-provision-contract-20261026','http-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const paths=[
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
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:['provision-entry','edit-context-entry','history-entry','read-entry','create-entry','edit-entry','recovery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts'))}));
const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'--project',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.ifError(types.error);assert.equal(types.status,0);
let server,childOwner,origin,passed=false,stdout='',stderr='';const checks=[],traffic=[];
let shutdown={forced_stop:false,shutdown_failed:false},stopped=false;
try{
 server=spawn(join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python'),['-I','-B',join(capsule,owner,'web/tests/provision-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});
 childOwner=watchChild(server);server.stdout.on('data',x=>stdout+=x);server.stderr.on('data',x=>stderr+=x);
 const ready=await readyChild(server,childOwner);origin=ready.origin;assert.equal(new URL(origin).hostname,'127.0.0.1');const {ids}=ready;
 const fixture=async mode=>{const r=await fetch(origin+'/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(r.status,200);return r.json();};
 const {createProvisionEntry}=await import(pathToFileURL(join(capsule,'compiled/web/src/provision-entry.js')));
 let callback;const session={user:{id:ids.account},access_token:'synthetic-token'};
 const auth={getSession:async()=>({data:{session},error:null}),refreshSession:async()=>({data:{session},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return{data:{subscription:{unsubscribe(){}}}};}};
 const entry=createProvisionEntry({org:ids.org,auth,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{
  if(url==='/api/v1/context')return new Response(JSON.stringify({account_id:ids.account,actor_id:ids.actor,membership_id:'7',authorization_scope:{kind:'organization',org_id:ids.org},resource_scope:{kind:'own_account',account_id:ids.account},permission:'kdg_capture.capture.read.own',decision_id:ids.decision,checked_at:new Date().toISOString()}));
  assert.equal(url,'/api/v1/provision');const r=await fetch(origin+url,init);traffic.push({path:url,method:init.method,status:r.status});return r;
 }});
 try{
  await entry.start();assert.equal(entry.state().kind,'authorized');const pending={account_id:ids.account,org_id:ids.org};
  for(const mode of ['all','assigned','edit_denied','not_permitted','empty','inactive','no_published']){
   const before=await fixture(mode);const result=await entry.load(pending);assert.equal(result.kind,'loaded',mode);const value=result.provision;
   assert.equal(value.actor_id,ids.actor);assert.equal(value.account_id,ids.account);assert.equal(value.membership_id,'7');assert.equal(value.org_id,ids.org);assert.equal(value.schema_version,1);
   const expected=mode==='not_permitted'?'not_permitted':['empty','inactive'].includes(mode)?'no_eligible_children':mode==='no_published'?'no_published_questionnaire':'ready';assert.equal(value.create_state,expected);
   if(mode==='assigned'){assert.equal(value.create_all_observation,null);assert.equal(value.children[0].assignment.assignment_id,ids.assignment);assert.equal(value.children[0].assignment.assignment_revision,'4');}
   if(mode==='all'){assert.ok(value.create_all_observation);assert.ok(value.create_assigned_observation);assert.equal(value.children[0].assignment,null);}
   if(mode==='edit_denied')assert.equal(value.edit_observation,null);
   if(mode==='not_permitted'){assert.equal(value.create_all_observation,null);assert.equal(value.create_assigned_observation,null);assert.equal(value.children.length,0);}
   if(mode==='no_published')assert.equal(value.questionnaire,null);else assert.equal(value.questionnaire.questionnaire_version_id,ids.version);
   const after=await fixture();assert.equal(after.acquired-before.acquired,1);assert.equal(after.released-before.released,1);assert.equal(after.captures+after.outcomes+after.history,0);
   for(const child of value.children){const stored=after.eligibility[child.child_eligibility_ref];assert.ok(stored);assert.equal(stored.child,child.child_id);assert.equal(stored.account,ids.account);assert.equal(stored.member,7);assert.equal(stored.actor,ids.actor);assert.equal(child.checked_at,stored.issued_at);assert.equal(Date.parse(child.expires_at)-Date.parse(child.checked_at),604800000);}
   checks.push('actual_setup_'+mode);
  }
  for(const [mode,status,error_id] of [['deny',403,'access_denied'],['expired',401,'authentication_required'],['outage',503,'authorization_unavailable'],['identity_mismatch',503,'authorization_unavailable'],['assignment_changed',503,'provision_unavailable'],['fail_acquire',503,'provision_unavailable'],['fail_sql',503,'provision_unavailable'],['fail_commit',503,'provision_unavailable'],['fail_release',503,'provision_unavailable']]){
   const before=await fixture(mode),result=await entry.load(pending);assert.deepEqual(result,{kind:'error',status,error_id});const after=await fixture();
   if(mode==='fail_release')assert.equal(Object.keys(after.eligibility).length,Object.keys(before.eligibility).length+1);
   else assert.equal(Object.keys(after.eligibility).length,Object.keys(before.eligibility).length);
   checks.push('actual_safe_failure_'+mode);
  }
  await fixture('all');const before=await fixture(),first=await entry.load(pending),second=await entry.load(pending);assert.equal(first.kind,'loaded');assert.equal(second.kind,'loaded');assert.notEqual(first.provision.children[0].child_eligibility_ref,second.provision.children[0].child_eligibility_ref);const after=await fixture();assert.equal(Object.keys(after.eligibility).length,Object.keys(before.eligibility).length+2);assert.equal(after.acquired,after.released);assert.equal(after.captures+after.outcomes+after.history,0);checks.push('actual_repeat_unique_committed_refs_without_business_writes');
  const beforeInvalid=await fixture();for(const [url,init,status] of [['/api/v1/provision',{},401],['/api/v1/provision?org_id=x',{headers:{Authorization:'Bearer synthetic'}},422]]){
   const r=await fetch(origin+url,init);assert.equal(r.status,status);assert.equal(r.headers.get('cache-control'),'private, no-store');assert.ok(!JSON.stringify(await r.json()).includes('synthetic-token'));
  }
  assert.equal((await fixture()).acquired,beforeInvalid.acquired);checks.push('actual_auth_selectors_before_storage_private_safe');
  assert.equal(typeof callback,'function');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(await fixture(),null,2)+'\n');passed=true;
 }finally{entry.dispose();}
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(server&&childOwner)shutdown=await stopChild(server,childOwner,origin);stopped=!!childOwner&&childOwner.state.code===0&&!shutdown.forced_stop;writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged,checks,traffic,server_stopped:stopped,shutdown,source_unchanged:unchanged,source_sha256:sources,node:process.version,typescript:'7.0.2',proof,limitations:['synthetic Auth admission and Access/storage; no actual database permissions/rollback','unmounted API and explicit consumer only; no live setup or local persistence']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
