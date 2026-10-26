// Explicit selected-source synthetic audit HTTP proof. No startup activation.
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
 "apps/kdg-capture/web/tests/persistence-child.mjs",
 "apps/kdg-capture/write-candidate/audit_read.py",
 "apps/kdg-capture/write-candidate/audit_http.py",
 "apps/kdg-capture/write-candidate/audit_openapi.py",
 "apps/kdg-capture/web/tests/audit-read-http-fixture.py",
 "apps/kdg-capture/web/tests/audit-read-http-proof.mjs"
];
const proof=join(root,'platform/deployment/.local/kdg-online-audit-read-20261026/network-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
const forceStall=process.argv.includes('--force-stall'),started=performance.now(),deadlineMs=forceStall?10000:60000,controller=new AbortController();let forcedStop=false;
const watchdog=setTimeout(()=>{forcedStop=true;controller.abort();},deadlineMs);
const checks=[],traffic=[],ok=(value,name)=>{assert.ok(value,name);checks.push(name);};
let child,owner,origin,passed=false,stdout='',stderr='',shutdown={forced_stop:false,shutdown_failed:false};
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 child=spawn(python,['-I','-B',join(capsule,'apps/kdg-capture/web/tests/audit-read-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});owner=watchChild(child);child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
 const ready=await readyChild(child,owner);origin=ready.origin;ok(new URL(origin).hostname==='127.0.0.1','loopback_only');const ids=ready.ids;
 if(forceStall)await new Promise((_,reject)=>{if(controller.signal.aborted)reject(Error('proof_deadline'));else controller.signal.addEventListener('abort',()=>reject(Error('proof_deadline')),{once:true});});
 const request=async(path,options={})=>{const response=await fetch(origin+path,{...options,signal:AbortSignal.any([controller.signal,AbortSignal.timeout(10000)])});traffic.push({path:path.split('?')[0],method:options.method??'GET',status:response.status});return response;};
 const state=async(mode)=>{const response=await request('/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(response.status,200);return response.json();};
 const api=async(path,status=200,options={})=>{const response=await request(path,{...options,headers:{authorization:'Bearer synthetic',...options.headers}});assert.equal(response.status,status);assert.equal(response.headers.get('cache-control'),'private, no-store');const body=await response.json();if(status!==200)assert.ok(typeof body.error_id==='string');return body;};
 const create={operation_id:ids.create,command_version:1,capture_id:ids.capture,child_id:ids.child,questionnaire_version_id:ids.version,observation_date:'2026-10-26',captured_at:'2026-10-26T10:00:00Z',child_eligibility_ref:'synthetic',answers:{[ids.question]:{value:1},[ids.actor]:{value:false},[ids.child]:{value:false},[ids.version]:{value:false}}};
 const send=async(method,path,body)=>api(path,200,{method,headers:{'content-type':'application/json'},body:JSON.stringify(body)});
 const created=await send('POST','/api/v1/captures',create);assert.equal(created.result.revision,'1');assert.deepEqual(await send('POST','/api/v1/captures',create),created);
 const edit={operation_id:ids.edit,command_version:1,expected_revision:'1',observation_date:create.observation_date,answers:{...create.answers,[ids.question]:{value:2}}};
 const edited=await send('PUT','/api/v1/captures/'+ids.capture,edit);assert.equal(edited.result.revision,'2');assert.deepEqual(await send('PUT','/api/v1/captures/'+ids.capture,edit),edited);
 const noop=await send('PUT','/api/v1/captures/'+ids.capture,{...edit,operation_id:ids.noop,expected_revision:'2'});assert.equal(noop.result.revision,'2');
 let before=await state('reader');ok(before.outcomes===3&&before.events===2&&before.capture_revisions[ids.capture]===2,'actual_create_changed_edit_retry_noop_have_only_two_events');
 const prefix='/api/v1/admin/captures/',url=prefix+ids.capture+'/events';
 let page=await api(url+'?limit=1');ok(page.org_id===ids.org&&page.account_id===ids.reader&&page.capture_id===ids.capture,'page_bound_to_verified_foreign_reader_and_record');ok(page.owner_account_id===ids.account&&page.owner_actor_id===ids.actor&&page.created_by===ids.actor&&page.updated_by===ids.actor&&page.current_revision==='2','original_latest_durable_attribution_preserved');ok(page.events.length===1&&page.events[0].revision==='2'&&page.events[0].command_type==='capture.edit'&&page.events[0].executor_actor_id===ids.actor,'latest_changed_edit_event_returned');ok(page.events[0].initiator_actor_id===ids.actor,'known_edit_initiator_preserved');ok(page.events[0].recorded_at!==page.updated_at,'capture_and_event_statement_timestamps_remain_distinct');
 ok(!JSON.stringify(page).includes('answers')&&!JSON.stringify(page).includes('definition')&&!JSON.stringify(page).includes('operation_id')&&!JSON.stringify(page).includes('outcome_id')&&!('observation' in page)&&!('expires_at' in page),'metadata_only_no_payload_receipt_or_offline_authority');ok(Buffer.byteLength(JSON.stringify(page),'utf8')<=65536,'actual_utf8_page_bound');
 const cursor=page.next_cursor;ok(typeof cursor==='string'&&cursor.length<=2048,'bounded_navigation_cursor');
 const second=await api(url+'?limit=1&cursor='+encodeURIComponent(cursor));ok(second.events.length===1&&second.events[0].revision==='1'&&second.events[0].command_type==='capture.create'&&second.next_cursor===null,'numeric_revision_continuation_without_duplicate_or_fake_noop');ok(second.events[0].initiator_actor_id===ids.actor,'known_create_initiator_preserved');
 const whole=await api(url);ok(whole.limit===30&&JSON.stringify(whole.events.map(x=>x.revision))===JSON.stringify(['2','1']),'default_page_lists_exact_two_revision_events');
 await api('/api/v1/captures/'+ids.capture,404);ok(true,'unchanged_own_endpoint_refuses_other_owner');
 before=await state('deny');let value=await api(url+'?limit=1&cursor='+encodeURIComponent(cursor),403);ok(value.error_id==='access_denied','continuation_rechecks_current_read_all');let after=await state();ok(after.acquired===before.acquired&&JSON.stringify(after.checks.slice(before.checks.length))===JSON.stringify(['kdg_capture.capture.read.all']),'denial_before_checkout_no_own_fallback');
 for(const mode of ['actor_missing','wrong_scope','wrong_org','wrong_permission','outage','expired']){before=await state(mode);value=await api(url,mode==='expired'?401:503);ok((await state()).acquired===before.acquired&&!JSON.stringify(value).includes('synthetic-private'),'safe_invalid_authority_before_checkout_'+mode);}
 before=await state('other_account');await api(url+'?limit=1&cursor='+encodeURIComponent(cursor),422);ok((await state()).acquired===before.acquired,'cursor_bound_to_current_verified_reader');
 await state('reader');for(const suffix of ['?owner_account_id='+ids.account,'?org_id='+ids.org,'?limit=1&limit=1','?limit=101','?cursor=bad','?limit=2&cursor='+encodeURIComponent(cursor)]){before=await state();await api(url+suffix,422);ok((await state()).acquired===before.acquired,'invalid_selectors_query_or_cursor_refused_without_checkout');}
 before=await state();await api(prefix+'bad/events',422);ok((await state()).checks.length===before.checks.length,'invalid_capture_id_before_access');
 const {request:httpRequest}=await import('node:http');before=await state();await new Promise((resolve,reject)=>{const work=httpRequest(origin+url,{method:'GET',signal:controller.signal,headers:{authorization:'Bearer synthetic','content-length':'4'}},response=>{let body='';response.on('data',b=>body+=b);response.on('end',()=>{try{assert.equal(response.statusCode,422);assert.equal(response.headers['cache-control'],'private, no-store');assert.ok(JSON.parse(body).error_id);resolve();}catch(error){reject(error);}});});work.setTimeout(10000,()=>work.destroy(Error('body_timeout')));work.on('error',reject);work.end('body');});ok((await state()).checks.length===before.checks.length,'actual_nonempty_get_body_refused_before_access');
 await state('seed_foreign');await state('reader');value=await api(prefix+ids.foreign_capture+'/events',404);const missing=await api(prefix+ids.unknown+'/events',404);ok(value.error_id===missing.error_id&&value.error_id==='capture_unavailable','foreign_org_and_missing_same_private404');
 await state('inactive_removed');ok((await api(url)).events.length===2,'historical_events_survive_inactive_child_removed_assignment');
 for(const mode of ['fail_acquire','fail_sql','fail_commit','fail_release','invalid_event','empty_evidence']){await state(mode);value=await api(url,503);ok(typeof value.error_id==='string'&&!JSON.stringify(value).includes('synthetic-private'),'safe_whole_response_failure_'+mode);}
 const final=await state('reader');ok(final.acquired===final.released,'all_connections_owned_through_release');ok(final.outcomes===3&&final.events===2&&final.capture_revisions[ids.capture]===2,'metadata_reads_never_mutate_business_evidence');ok(JSON.stringify(final.stored_evidence)===JSON.stringify(before.stored_evidence),'original_events_unchanged_by_reads_and_failures');ok(final.contexts.some(c=>c.mode==='all_read'&&c.account===ids.reader&&c.actor===ids.reader_actor),'all_read_uses_verified_reader_not_original_owner');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(final,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(child&&owner)shutdown=await stopChild(child,owner,origin);clearTimeout(watchdog);writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const stopped=!!owner&&owner.state.code===0&&!shutdown.forced_stop,unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged&&!forcedStop,checks,traffic,source_sha256:sources,source_unchanged:unchanged,server_stopped:stopped,shutdown,forced_stop:forcedStop,deadline_ms:deadlineMs,elapsed_ms:performance.now()-started,node:process.version,proof,limitations:['actual loopback create/edit/audit execution with synthetic Access and recorded storage; no native SQL/RLS/driver qualification','stable actor IDs only; no Identity label resolution, portal/UI, offline cache or activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
