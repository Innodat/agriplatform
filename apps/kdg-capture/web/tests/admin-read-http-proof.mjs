// Explicit selected-source synthetic administrator HTTP proof. No startup activation.
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
 "apps/kdg-capture/web/tests/admin-read-http-proof.mjs",
 "apps/kdg-capture/web/tests/persistence-child.mjs"
];
const proof=join(root,'platform/deployment/.local/kdg-online-admin-read-20261026/network-'+randomUUID()),capsule=join(proof,'capsule');mkdirSync(capsule,{recursive:true,mode:0o700});
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),dest=join(capsule,path);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,bytes);return[path,hash(bytes)];}));
const forceStall=process.argv.includes('--force-stall'),started=performance.now(),deadlineMs=forceStall?10000:60000,controller=new AbortController();let forcedStop=false;
const watchdog=setTimeout(()=>{forcedStop=true;controller.abort();},deadlineMs);
const checks=[],traffic=[],ok=(value,name)=>{assert.ok(value,name);checks.push(name);};
let child,owner,origin,passed=false,stdout='',stderr='',shutdown={forced_stop:false,shutdown_failed:false};
try{
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 child=spawn(python,['-I','-B',join(capsule,'apps/kdg-capture/web/tests/admin-read-http-fixture.py'),'--proof-directory',proof],{stdio:['ignore','pipe','pipe']});owner=watchChild(child);child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
 const ready=await readyChild(child,owner);origin=ready.origin;ok(new URL(origin).hostname==='127.0.0.1','loopback_only');const ids=ready.ids;
 if(forceStall)await new Promise((_,reject)=>{if(controller.signal.aborted)reject(Error('proof_deadline'));else controller.signal.addEventListener('abort',()=>reject(Error('proof_deadline')),{once:true});});
 const request=async(path,options={})=>{const response=await fetch(origin+path,{...options,signal:AbortSignal.any([controller.signal,AbortSignal.timeout(10000)])});traffic.push({path:path.split('?')[0],method:options.method??'GET',status:response.status});return response;};
 const state=async(mode)=>{const response=await request('/__fixture',mode?{method:'POST',body:JSON.stringify({mode})}:{});assert.equal(response.status,200);return response.json();};
 const get=async(path,status=200,options={})=>{const response=await request(path,{headers:{authorization:'Bearer synthetic'},...options});assert.equal(response.status,status);assert.equal(response.headers.get('cache-control'),'private, no-store');const body=await response.json();if(status!==200)assert.ok(typeof body.error_id==='string');return body;};
 const prefix='/api/v1/admin/captures',query='?from_date=2026-10-01&to_date=2026-10-26&limit=1',ownPrefix='/api/v1/captures';
 let value=await get(prefix+'/'+ids.captures[1]);ok(value.owner_account_id===ids.other_account&&value.owner_actor_id===ids.other_actor&&value.created_by===ids.other_actor&&value.updated_by===ids.actor,'foreign_owner_original_durable_provenance');ok(value.definition.questions[0].label==='Original retained question','original_definition_returned');ok(!('observation' in value)&&!('expires_at' in value),'detail_no_offline_authority');
 value=await get(ownPrefix+'/'+ids.captures[1],404);ok(value.error_id==='capture_unavailable','own_endpoint_still_refuses_foreign_owner');
 value=await get(ownPrefix+'/'+ids.captures[0]);ok(value.owner_account_id===ids.account,'own_endpoint_unchanged');
 value=await get(prefix+'/'+ids.captures[3],404);ok(value.error_id.endsWith('capture_unavailable'),'foreign_org_private404');
 const visited=[];let page=await get(prefix+query),cursor;
 do{ok(page.org_id===ids.org&&page.account_id===ids.account&&page.limit===1,'admin_page_bound_to_verified_caller');ok(!('observation' in page)&&!('expires_at' in page),'page_no_offline_observation');visited.push(...page.items.map(item=>item.capture_id));cursor=page.next_cursor;if(cursor)page=await get(prefix+query+'&cursor='+encodeURIComponent(cursor));}while(cursor);
 ok(JSON.stringify(visited)===JSON.stringify(ids.captures.slice(0,3).reverse()),'tied_keyset_all_owners_only_configured_org_dates_without_duplicates');
 const first=await get(prefix+query);const beforeDenied=await state('deny');value=await get(prefix+query+'&cursor='+encodeURIComponent(first.next_cursor),403);ok(value.error_id==='access_denied','role_loss_between_pages_denies');const denied=await state();ok(denied.acquired===beforeDenied.acquired&&JSON.stringify(denied.checks.slice(beforeDenied.checks.length))===JSON.stringify(['kdg_capture.capture.read.all']),'denial_before_checkout_no_own_fallback');ok((await get(ownPrefix+'/'+ids.captures[0])).owner_account_id===ids.account,'own_permission_never_substituted_for_all');
 await state('all');const ownPage=await get(ownPrefix+'?from_date=2026-09-01&to_date=2026-10-26&limit=1');ok(!!ownPage.observation&&!!ownPage.next_cursor,'own_history_keeps_own_observation_and_cursor');await get(prefix+query+'&cursor='+encodeURIComponent(ownPage.next_cursor),422);ok(true,'own_cursor_refused_by_all_boundary');await get(ownPrefix+query+'&cursor='+encodeURIComponent(first.next_cursor),422);ok(true,'all_cursor_refused_by_own_boundary');
 await state('other_account');const beforeCaller=await state();await get(prefix+query+'&cursor='+encodeURIComponent(first.next_cursor),422);ok((await state()).acquired===beforeCaller.acquired,'cursor_bound_to_current_verified_caller');await state('all');
 for(const mode of ['actor_missing','wrong_scope','wrong_permission','wrong_org','outage','expired']){const before=await state(mode);value=await get(prefix+'/'+ids.captures[1],mode==='expired'?401:503);ok((await state()).acquired===before.acquired&&typeof value.error_id==='string','invalid_current_evidence_before_checkout_'+mode);}
 await state('all');for(const [path,options] of [[prefix+query+'&owner_account_id='+ids.other_account,{}],[prefix+query+'&limit=1',{}],[prefix+'/bad',{}]]){
  const before=await state();await get(path,422,options);ok((await state()).checks.length===before.checks.length,'invalid_query_or_id_before_access');
 }
 // Node fetch does not permit GET bodies; use a real HTTP request for this strict-wire case.
 const {request:httpRequest}=await import('node:http');const beforeBody=await state();await new Promise((resolve,reject)=>{const request=httpRequest(origin+prefix+'/'+ids.captures[1],{method:'GET',signal:controller.signal,headers:{authorization:'Bearer synthetic','content-length':'4'}},response=>{let body='';response.on('data',b=>body+=b);response.on('end',()=>{try{assert.equal(response.statusCode,422);assert.equal(response.headers['cache-control'],'private, no-store');assert.ok(JSON.parse(body).error_id);resolve();}catch(error){reject(error);}});});request.setTimeout(10000,()=>request.destroy(Error('body_timeout')));request.on('error',reject);request.end('body');});ok((await state()).checks.length===beforeBody.checks.length,'nonempty_get_body_before_access');
 for(const mode of ['fail_sql','fail_release','invalid_detail']){await state(mode);value=await get(prefix+query,503);ok(typeof value.error_id==='string'&&!JSON.stringify(value).includes('synthetic-private'),'safe_whole_page_failure_'+mode);}
 await state('all');const final=await state();ok(final.acquired===final.released,'all_owned_connections_released');ok(final.source_records_unchanged&&final.outcomes===0&&final.history===0,'read_only_records_outcomes_history_unchanged');ok(final.contexts.some(c=>c.mode==='all_read'&&c.account===ids.account&&c.actor===ids.actor)&&final.contexts.some(c=>c.mode==='own_read'),'separate_verified_all_and_own_contexts');writeFileSync(join(proof,'integration-state.json'),JSON.stringify(final,null,2)+'\n');passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}
finally{
 if(child&&owner)shutdown=await stopChild(child,owner,origin);clearTimeout(watchdog);writeFileSync(join(proof,'fixture.log'),stdout+stderr);
 const stopped=!!owner&&owner.state.code===0&&!shutdown.forced_stop,unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);const result={passed:passed&&stopped&&unchanged&&!forcedStop,checks,traffic,source_sha256:sources,source_unchanged:unchanged,server_stopped:stopped,shutdown,forced_stop:forcedStop,deadline_ms:deadlineMs,elapsed_ms:performance.now()-started,node:process.version,proof,limitations:['actual loopback API/read execution with synthetic Access and recorded storage; no native SQL or live privileges','no portal/Auth client, offline all-read observation, cache, schema/startup/release activation']};writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
