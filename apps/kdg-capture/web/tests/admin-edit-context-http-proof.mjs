// Explicit selected-source synthetic administrator edit-context HTTP proof. No startup activation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {spawn} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
import {watchChild,readyChild,stopChild} from './persistence-child.mjs';
const root=process.cwd(),hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(process.version,'v26.11.1');
const paths=[
 "apps/kdg-capture/web/tests/persistence-http-fixture.py",
 "apps/kdg-capture/api/main.py",
 "apps/kdg-capture/api/context.py",
 "apps/kdg-capture/api/safe_errors.py",
 "apps/kdg-capture/api/capture_commands.py",
 "apps/kdg-capture/api/questionnaire.py",
 "apps/kdg-capture/write-tools/transaction_context.py",
 "apps/kdg-capture/write-candidate/own_observation_openapi.py",
 "apps/kdg-capture/write-candidate/edit_context.py",
 "apps/kdg-capture/write-candidate/edit_context_http.py",
 "apps/kdg-capture/write-candidate/edit_context_openapi.py",
 "apps/kdg-capture/write-candidate/history_http.py",
 "apps/kdg-capture/write-candidate/history_openapi.py",
 "apps/kdg-capture/write-candidate/capture_history.py",
 "apps/kdg-capture/write-candidate/read_http.py",
 "apps/kdg-capture/write-candidate/read_openapi.py",
 "apps/kdg-capture/write-candidate/capture_read.py",
 "apps/kdg-capture/write-candidate/create_http.py",
 "apps/kdg-capture/write-candidate/edit_http.py",
 "apps/kdg-capture/write-candidate/recovery_http.py",
 "apps/kdg-capture/write-candidate/create_openapi.py",
 "apps/kdg-capture/write-candidate/edit_openapi.py",
 "apps/kdg-capture/write-candidate/recovery_openapi.py",
 "apps/kdg-capture/write-candidate/capture_create_handler.py",
 "apps/kdg-capture/write-candidate/capture_edit_handler.py",
 "apps/kdg-capture/write-candidate/capture_create.py",
 "apps/kdg-capture/write-candidate/capture_edit.py",
 "apps/kdg-capture/write-candidate/operation_recovery.py",
 "apps/kdg-capture/write-candidate/operation_outcomes.py",
 "apps/kdg-capture/write-candidate/admin_read.py",
 "apps/kdg-capture/write-candidate/admin_http.py",
 "apps/kdg-capture/write-candidate/admin_openapi.py",
 "apps/kdg-capture/web/tests/admin-read-http-fixture.py",
 "apps/kdg-capture/web/tests/persistence-child.mjs",
 "apps/kdg-capture/write-candidate/admin_edit_context.py",
 "apps/kdg-capture/write-candidate/admin_edit_context_http.py",
 "apps/kdg-capture/write-candidate/admin_edit_context_openapi.py",
 "apps/kdg-capture/web/tests/admin-edit-context-http-fixture.py",
 "apps/kdg-capture/web/tests/admin-edit-context-http-proof.mjs"
];
const proof=join(root,'platform/deployment/.local/kdg-online-admin-edit-context-20261026/network-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
const forceStall=process.argv.includes('--force-stall'),started=performance.now(),deadlineMs=forceStall?10000:60000,controller=new AbortController();let forcedStop=false;
const watchdog=setTimeout(()=>{forcedStop=true;controller.abort();},deadlineMs);
const checks=[],traffic=[],ok=(value,name)=>{assert.ok(value,name);checks.push(name);};
let child,owner,origin,passed=false,stdout='',stderr='',shutdown={forced_stop:false,shutdown_failed:false};
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 child=spawn(python,['-I','-B',join(capsule,'apps/kdg-capture/web/tests/admin-edit-context-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});owner=watchChild(child);child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
 const ready=await readyChild(child,owner);origin=ready.origin;ok(new URL(origin).hostname==='127.0.0.1','loopback_only');const ids=ready.ids;
 if(forceStall)await new Promise((_,reject)=>{if(controller.signal.aborted)reject(Error('proof_deadline'));else controller.signal.addEventListener('abort',()=>reject(Error('proof_deadline')),{once:true});});
 const request=async(path,options={})=>{const response=await fetch(origin+path,{...options,signal:AbortSignal.any([controller.signal,AbortSignal.timeout(10000)])});traffic.push({path:path.split('?')[0],method:options.method??'GET',status:response.status});return response;};
 const state=async(mode)=>{const response=await request('/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(response.status,200);return response.json();};
 const get=async(path,status=200,options={})=>{const response=await request(path,{headers:{authorization:'Bearer synthetic'},...options});assert.equal(response.status,status);assert.equal(response.headers.get('cache-control'),'private, no-store');const bytes=Buffer.from(await response.arrayBuffer());if(status===200&&path.endsWith('/edit-context')&&path.startsWith('/api/v1/admin/'))ok(bytes.length<=544*1024,'actual_wire_utf8_context_bound');const body=JSON.parse(bytes.toString('utf8'));if(status!==200)assert.ok(typeof body.error_id==='string');return body;};
 const prefix='/api/v1/admin/captures/',detail=prefix+ids.captures[1],url=detail+'/edit-context',own='/api/v1/captures/';
 let before=await state(),value=await get(url),after=await state();ok(JSON.stringify(after.checks.slice(before.checks.length))===JSON.stringify(['kdg_capture.capture.read.all','kdg_capture.capture.edit.all']),'exact_current_read_all_then_edit_all_pair');ok(after.acquired===before.acquired+1&&after.released===before.released+1,'both_checks_before_single_owned_checkout');ok(JSON.stringify(Object.keys(value).sort())===JSON.stringify(['capture','editable_fields']),'closed_online_context_envelope');ok(JSON.stringify(value.editable_fields)===JSON.stringify(['observation_date','answers']),'only_date_and_answers_editable');
 ok(value.capture.owner_account_id===ids.other_account&&value.capture.owner_actor_id===ids.other_actor&&value.capture.created_by===ids.other_actor&&value.capture.updated_by===ids.actor,'foreign_original_owner_creator_latest_editor_preserved');ok(value.capture.revision==='2'&&value.capture.definition.questions[0].label==='Original retained question','shown_revision_and_original_definition_preserved');ok(!('read_observation' in value)&&!('edit_observation' in value)&&!('expires_at' in value)&&!('permission' in value),'no_offline_observation_expiry_or_permission_lease');
 await get(own+ids.captures[1]+'/edit-context',404);ok(true,'own_edit_context_still_refuses_foreign_owner');
 value=await get(own+ids.captures[0]+'/edit-context');ok(!!value.read_observation&&!!value.edit_observation&&value.capture.owner_account_id===ids.account,'existing_own_context_observations_unchanged');
 for(const mode of ['deny_read','deny_edit','outage_read','outage_edit','expired','actor_setup']){
  before=await state(mode);value=await get(url,mode==='expired'?401:mode==='actor_setup'?409:mode.startsWith('deny_')?403:503);after=await state();ok(after.acquired===before.acquired,'authority_failure_no_checkout_'+mode);const expected=['deny_read','outage_read','expired'].includes(mode)?['kdg_capture.capture.read.all']:['kdg_capture.capture.read.all','kdg_capture.capture.edit.all'];ok(JSON.stringify(after.checks.slice(before.checks.length))===JSON.stringify(expected),'authority_failure_no_own_fallback_'+mode);
 }
 await state('deny_edit');value=await get(detail);ok(value.owner_account_id===ids.other_account,'read_all_detail_stays_independent_of_edit_all');
 for(const mode of ['mismatch_account','mismatch_actor','mismatch_membership','wrong_auth_org','wrong_resource_org','wrong_resource_kind','wrong_permission','missing_actor']){before=await state(mode);value=await get(url,503);ok((await state()).acquired===before.acquired&&value.error_id==='authorization_unavailable','paired_evidence_mismatch_before_checkout_'+mode);}
 await state('all');for(const path of [url+'?org_id='+ids.org,url+'?account_id='+ids.account,url+'?capture_id='+ids.captures[0],url+'?x=1&x=1',prefix+'bad/edit-context']){before=await state();await get(path,422);ok((await state()).checks.length===before.checks.length,'invalid_path_or_any_query_before_authority');}
 const {request:httpRequest}=await import('node:http');before=await state();await new Promise((resolve,reject)=>{const work=httpRequest(origin+url,{method:'GET',signal:controller.signal,headers:{authorization:'Bearer synthetic','content-length':'4'}},response=>{let body='';response.on('data',b=>body+=b);response.on('end',()=>{try{assert.equal(response.statusCode,422);assert.equal(response.headers['cache-control'],'private, no-store');assert.ok(JSON.parse(body).error_id);resolve();}catch(error){reject(error);}});});work.setTimeout(10000,()=>work.destroy(Error('body_timeout')));work.on('error',reject);work.end('body');});ok((await state()).checks.length===before.checks.length,'actual_get_body_refused_before_authority');
 value=await get(prefix+ids.captures[3]+'/edit-context',404);const missing=await get(prefix+'99999999-aaaa-4aaa-8aaa-999999999999/edit-context',404);ok(value.error_id===missing.error_id&&value.error_id==='capture_unavailable','foreign_org_and_missing_same_private404');
 await state('inactive_removed');value=await get(url);ok(value.capture.owner_account_id===ids.other_account,'historical_context_ignores_current_assignment_and_activity');
 for(const mode of ['fail_acquire','fail_sql','fail_commit','fail_release','invalid_detail']){await state(mode);value=await get(url,503);ok(typeof value.error_id==='string'&&!JSON.stringify(value).includes('synthetic-private'),'safe_whole_context_failure_'+mode);}
 await state('all');before=await state();await get(url,405,{method:'PUT'});ok((await state()).checks.length===before.checks.length,'candidate_exposes_no_put');
 const final=await state();ok(final.acquired===final.released,'all_connections_owned_through_release');ok(final.records_unchanged&&final.outcomes===0&&final.events===0,'read_only_context_never_mutates_records_receipts_or_events');ok(final.contexts.some(c=>c.mode==='all_read'&&c.account===ids.account&&c.actor===ids.actor),'context_uses_current_admin_identity_not_original_owner');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(final,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(child&&owner)shutdown=await stopChild(child,owner,origin);clearTimeout(watchdog);writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const stopped=!!owner&&owner.state.code===0&&!shutdown.forced_stop&&!shutdown.shutdown_failed;let finalStorageValid=false;if(passed&&stopped){try{const final=JSON.parse(readFileSync(join(proof,'storage-final.json'),'utf8'));ok(final.disposed===3,'all_three_candidate_engines_disposed');ok(final.acquired===final.released&&final.records_unchanged&&final.outcomes===0&&final.events===0,'post_shutdown_storage_unchanged_and_connections_released');finalStorageValid=true;}catch(error){writeFileSync(join(proof,'final-storage-failure.log'),String(error?.stack??error)+'\n');}}const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&finalStorageValid&&unchanged&&!forcedStop,checks,traffic,source_sha256:sources,source_unchanged:unchanged,server_stopped:stopped,shutdown,forced_stop:forcedStop,deadline_ms:deadlineMs,elapsed_ms:performance.now()-started,node:process.version,proof,limitations:['actual loopback candidate with synthetic Access/recorded storage; no native SQL/RLS/driver or live identity proof','no admin PUT/recovery/conflict, offline authority, UI/session/startup/cache activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
