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
 "apps/kdg-capture/write-candidate/admin_edit.py",
 "apps/kdg-capture/write-candidate/admin_edit_http.py",
 "apps/kdg-capture/write-candidate/admin_edit_openapi.py",
 "apps/kdg-capture/web/tests/admin-edit-http-fixture.py",
 "apps/kdg-capture/web/tests/admin-edit-http-proof.mjs"
];
const proof=join(root,'platform/deployment/.local/kdg-online-admin-edit-20261027/network-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
const forceStall=process.argv.includes('--force-stall'),started=performance.now(),deadlineMs=forceStall?10000:60000,controller=new AbortController();let forcedStop=false;
const watchdog=setTimeout(()=>{forcedStop=true;controller.abort();},deadlineMs);
const checks=[],traffic=[],ok=(value,name)=>{assert.ok(value,name);checks.push(name);};
let child,owner,origin,passed=false,stdout='',stderr='',shutdown={forced_stop:false,shutdown_failed:false};
try{
 child=spawn(join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python'),['-I','-B',join(capsule,'apps/kdg-capture/web/tests/admin-edit-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});owner=watchChild(child);child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
 const ready=await readyChild(child,owner);origin=ready.origin;ok(new URL(origin).hostname==='127.0.0.1','loopback_only');const ids=ready.ids;
 if(forceStall)await new Promise((_,reject)=>{if(controller.signal.aborted)reject(Error('proof_deadline'));else controller.signal.addEventListener('abort',()=>reject(Error('proof_deadline')),{once:true});});
 const request=async(path,options={})=>{const response=await fetch(origin+path,{...options,signal:AbortSignal.any([controller.signal,AbortSignal.timeout(10000)])});traffic.push({path:path.split('?')[0],method:options.method??'GET',status:response.status});return response;};
 const state=async(mode)=>{const response=await request('/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(response.status,200);return response.json();};
 const api=async(path,status=200,options={},expectedId)=>{const response=await request(path,{headers:{authorization:'Bearer administrator'},...options});assert.equal(response.status,status);assert.equal(response.headers.get('cache-control'),'private, no-store');const bytes=Buffer.from(await response.arrayBuffer());assert.ok(bytes.length<=16384);const value=JSON.parse(bytes.toString('utf8'));if(status!==200){assert.equal(value.error_id,expectedId??({401:'authentication_required',403:'access_denied',404:'capture_unavailable',409:'kdg_capture.capture_revision_conflict',422:'validation_failed',500:'internal_error',503:'authorization_unavailable'})[status]);assert.ok(!JSON.stringify(value).includes('synthetic-private'));}return value;};
 const command=(revision,value,operation=randomUUID())=>({operation_id:operation,command_version:1,expected_revision:String(revision),observation_date:'2026-10-25',answers:{[ids.question]:{value},...Object.fromEntries(ids.boolean_questions.map(q=>[q,{value:false}]))}});
 const path=(id,principal)=>'/api/v1/'+(principal==='facilitator'?'':'admin/')+'captures/'+id;
 const put=(id,cmd,status=200,principal='administrator',expectedId)=>api(path(id,principal),status,{method:'PUT',headers:{authorization:'Bearer '+principal,'content-type':'application/json'},body:JSON.stringify(cmd)},expectedId);
 const recover=(operation,status=200,principal='administrator',expectedId)=>api('/api/v1/admin/operations/'+operation+'?command_type=capture.edit',status,{headers:{authorization:'Bearer '+principal}},expectedId);
 const immutable=c=>Object.fromEntries(['org','account','owner_actor','child','version','questionnaire','display_version','definition','captured_at','created_by','created_at'].map(k=>[k,c[k]]));
 const initial=await state(),[a,b,foreign,concurrent]=ids.captures,first=command(1,2);let before=initial,receipt=await put(a,first),after=await state();
 ok(JSON.stringify(after.checks.slice(before.checks.length).map(x=>x.permission))===JSON.stringify(['kdg_capture.capture.read.all','kdg_capture.capture.edit.all']),'exact_all_pair_before_write');ok(receipt.status==='committed'&&receipt.result.capture_id===a&&receipt.result.revision==='2','administrator_corrects_foreign_owner');ok(JSON.stringify(immutable(after.captures[a]))===JSON.stringify(immutable(initial.captures[a])),'all_original_owner_creation_child_version_facts_preserved');ok(after.captures[a].updated_by===ids.actor,'actual_admin_last_editor');ok(after.events.length===1&&after.outcomes===initial.outcomes+1,'one_capture_event_and_private_receipt');ok(after.events[0].executor_actor_id===ids.actor&&after.events[0].executor_account_id===ids.account&&after.events[0].owner_actor_id===ids.owner_actor&&after.events[0].initiator_actor_id===ids.actor,'original_owner_and_actual_executor_in_linked_event');
 ok(initial.json_equality_type_distinct,'synthetic_json_equality_preserves_boolean_number_types');
 let conflict=await put(a,command(1,3),409,'facilitator');ok(conflict.error_id==='kdg_capture.capture_revision_conflict'&&conflict.current_revision==='2'&&Object.keys(conflict).sort().join(',')==='current_revision,error,error_id','admin_first_facilitator_stale_conflict_has_revision_only');
 const facilitator=command(2,3);await put(a,facilitator,200,'facilitator');conflict=await put(a,command(2,4),409);ok(conflict.current_revision==='3','intervening_facilitator_save_repeats_admin_conflict');
 const reviewed=command(3,4);await put(a,reviewed);after=await state();ok(after.captures[a].revision===4&&after.captures[a].answers[ids.question].value===4,'new_reviewed_admin_operation_at_reviewed_revision');ok(after.events.length===3&&after.outcomes===initial.outcomes+3,'rejected_conflicts_store_no_receipt_or_event');
 const ownFirst=command(1,2);await put(b,ownFirst,200,'facilitator');conflict=await put(b,command(1,3),409);ok(conflict.current_revision==='2','facilitator_first_admin_stale_conflict');await put(b,command(2,3));
 before=await state();const noop=command(3,3);receipt=await put(b,noop);after=await state();ok(receipt.result.revision==='3'&&after.outcomes===before.outcomes+1&&after.events.length===before.events.length&&JSON.stringify(after.captures[b])===JSON.stringify(before.captures[b]),'noop_appends_receipt_without_fictitious_change');
 before=await state();receipt=await put(b,{...first,expected_revision:'1',answers:{}});after=await state();ok(receipt.result.capture_id===a&&receipt.result.revision==='2'&&receipt.operation_id===first.operation_id,'changed_retry_path_payload_revision_returns_original_action');ok(after.outcomes===before.outcomes&&after.events.length===before.events.length&&JSON.stringify(after.captures)===JSON.stringify(before.captures),'replay_has_no_duplicate_effect');
 const detail=await api('/api/v1/admin/captures/'+a);ok(detail.revision==='4'&&detail.definition.questions[0].label==='Original retained question','current_detail_and_original_definition_independent_of_old_receipt');
 await state('deny_edit');before=await state();receipt=await recover(first.operation_id);after=await state();ok(receipt.result.revision==='2'&&after.checks.slice(before.checks.length).every(x=>x.permission==='kdg_capture.capture.read.all'),'original_receipt_recovered_after_edit_all_loss_using_read_all_only');await put(a,command(4,5),403);ok((await state()).outcomes===after.outcomes,'edit_denial_prevents_new_writes');
 await state('all');receipt=await recover(randomUUID());ok(receipt.status==='unresolved','verified_private_absence_unresolved');receipt=await recover(first.operation_id,200,'other-admin');ok(receipt.status==='unresolved','another_executor_cannot_discover_admin_receipt');receipt=await recover(facilitator.operation_id,200,'facilitator');ok(receipt.status==='committed'&&receipt.result.revision==='3','recovery_current_all_read_does_not_invent_original_surface_provenance');
 await state('target_unavailable');await recover(first.operation_id,503,'administrator','operation_verification_unavailable');ok(true,'stored_target_failure_never_receipt_or_unresolved');await state('all');
 receipt=await recover(ids.foreign_operation);ok(receipt.status==='unresolved','same_executor_operation_in_valid_foreign_org_stays_private');await state('target_sql_error');await recover(first.operation_id,503,'administrator','operation_verification_unavailable');await put(b,first,503,'administrator','operation_verification_unavailable');ok(true,'stored_target_sql_failures_use_exact_verification_error');await state('all');
 before=await state();await put(foreign,command(1,2),404);await put('99999999-aaaa-4aaa-8aaa-999999999999',command(1,2),404);ok((await state()).outcomes===before.outcomes,'fresh_foreign_org_and_missing_private404_without_effect');
 for(const mode of ['deny_read','deny_edit','outage','expired','actor_setup','mismatch_actor','wrong_org']){await state(mode);before=await state();await put(a,command(4,5),mode==='expired'?401:mode==='actor_setup'?409:mode.startsWith('deny_')?403:503,'administrator',mode==='actor_setup'?'identity.actor_setup_required':undefined);after=await state();ok(after.acquired===before.acquired&&after.outcomes===before.outcomes,'authority_failure_before_checkout_'+mode);ok(after.checks.slice(before.checks.length).every(x=>x.permission.endsWith('.all')),'no_own_fallback_'+mode);}
 await state('deny_read');before=await state();await recover(first.operation_id,403);ok((await state()).acquired===before.acquired,'read_loss_denies_recovery_before_checkout');
 await state('inactive_removed');await put(a,command(4,5));ok((await state()).captures[a].revision===5,'historical_edit_requires_no_current_child_assignment_or_activity');
 for(const mode of ['fail_history','fail_outcome','fail_commit','fail_sql','fail_acquire']){await state(mode);before=await state();await put(a,command(5,1),500);after=await state();ok(JSON.stringify(after.captures)===JSON.stringify(before.captures)&&after.outcomes===before.outcomes&&after.events.length===before.events.length,'synthetic_atomic_failure_'+mode);}
 await state('fail_release');const uncertain=command(5,1);await put(a,uncertain,500);await state('all');receipt=await recover(uncertain.operation_id);ok(receipt.status==='committed'&&receipt.result.revision==='6','release_failure_uncertain_commit_recovered_without_reexecution');
 before=await state();await put(a,{...command(6,2),answers:{}},422);ok((await state()).outcomes===before.outcomes,'invalid_original_answers_no_effect');
 const concurrentResults=await Promise.all(['administrator','facilitator'].map(principal=>request(path(concurrent,principal),{method:'PUT',headers:{authorization:'Bearer '+principal,'content-type':'application/json'},body:JSON.stringify(command(1,principal==='administrator'?2:3))})));
 ok(concurrentResults.map(r=>r.status).sort().join(',')==='200,409','overlapping_actual_http_saves_have_one_winner');for(const r of concurrentResults)await r.arrayBuffer();
 await state('drop_response');before=await state();const lost=command(6,2);let interrupted=false;try{await put(a,lost);}catch(error){interrupted=error instanceof TypeError;}ok(interrupted,'actual_post_commit_response_body_interrupted');await state('all');receipt=await recover(lost.operation_id);after=await state();ok(receipt.status==='committed'&&receipt.result.revision==='7'&&after.outcomes===before.outcomes+1&&after.events.length===before.events.length+1,'dropped_response_recovers_one_original_committed_action');
 const sameOperation=randomUUID();before=await state();const retries=[put(a,command(7,3,sameOperation)),put(b,command(3,4,sameOperation))];const receipts=await Promise.all(retries);after=await state();assert.deepEqual(receipts[0],receipts[1]);ok(after.outcomes===before.outcomes+1&&after.events.length===before.events.length+1,'same_executor_operation_concurrent_different_targets_one_effect_identical_receipts');ok(Object.keys(after.captures).filter(k=>after.captures[k].revision!==before.captures[k].revision).length===1,'same_operation_retries_cannot_change_second_target');
 await state('all');before=await state();for(const suffix of ['?org_id='+ids.org,'?x=1&x=1'])await api(path(a,'administrator')+suffix,422,{method:'PUT',headers:{authorization:'Bearer administrator','content-type':'application/json'},body:JSON.stringify(command(6,2))});
 await api('/api/v1/admin/operations/'+first.operation_id+'?command_type=capture.create',422);await api('/api/v1/admin/operations/'+first.operation_id+'?command_type=capture.edit&command_type=capture.edit',422);await api(path(a,'administrator'),422,{method:'PUT',headers:{authorization:'Bearer administrator','content-type':'application/json'},body:'x'.repeat(131073)});ok((await state()).checks.length===before.checks.length,'wire_selectors_discriminator_and_byte_bound_before_authority');
 const final=await state();ok(final.acquired===final.released&&final.foreign_unchanged,'owned_connections_balanced_foreign_record_unchanged');ok(final.contexts.some(c=>c.mode==='all_write'&&c.account===ids.account&&c.actor===ids.actor)&&final.contexts.some(c=>c.mode==='all_read'),'actual_admin_context_and_readonly_recovery_modes');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(final,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(child&&owner)shutdown=await stopChild(child,owner,origin);clearTimeout(watchdog);writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const stopped=!!owner&&owner.state.code===0&&!shutdown.forced_stop&&!shutdown.shutdown_failed;let finalStorageValid=false;if(passed&&stopped){try{const final=JSON.parse(readFileSync(join(proof,'storage-final.json'),'utf8'));ok(final.disposed===4,'all_owned_candidate_engines_disposed');ok(final.acquired===final.released&&final.foreign_unchanged,'post_shutdown_storage_and_connection_checks');const before=JSON.parse(readFileSync(join(proof,'integration-state.json'),'utf8'));assert.deepEqual({captures:final.captures,events:final.events,outcomes:final.outcomes},{captures:before.captures,events:before.events,outcomes:before.outcomes});ok(true,'no_unobserved_effect_after_final_response');finalStorageValid=true;}catch(error){writeFileSync(join(proof,'final-storage-failure.log'),String(error?.stack??error)+'\n');}}
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]),result={passed:passed&&stopped&&finalStorageValid&&unchanged&&!forcedStop,checks,traffic,source_sha256:sources,source_unchanged:unchanged,server_stopped:stopped,shutdown,forced_stop:forcedStop,deadline_ms:deadlineMs,elapsed_ms:performance.now()-started,node:process.version,proof,limitations:['Actual loopback API/HTTP with synthetic Access and recorded storage; does not establish native SQL/RLS/locking/driver rollback or live authority','No portal/in-memory comparison/session rendering/device, startup or release activation; no offline administrator authority']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
