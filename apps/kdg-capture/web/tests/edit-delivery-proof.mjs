// Isolated synthetic Chromium IndexedDB proof. No application startup or real authority.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync} from 'node:fs';
import {join,resolve,extname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {randomUUID,createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {createServer} from 'node:http';
import {once} from 'node:events';
const root=process.cwd(),owner='apps/kdg-capture',retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(process.version,'v26.11.1');assert.equal(JSON.parse(readFileSync(join(retained,'node_modules/typescript/package.json'))).version,'7.0.2');
const proof=join(root,'platform/deployment/.local/kdg-explicit-edit-delivery-20261026/delivery-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/src/provision.ts','web/src/create.ts','contracts/provision-generated/types.gen.ts','contracts/create-generated/types.gen.ts','web/tests/edit-delivery.types.ts','web/tsconfig.edit-delivery.json','web/tsconfig.auth.json','web/src/edit-delivery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/edit-delivery.ts','web/src/recovery.ts','contracts/recovery-generated/types.gen.ts','web/src/edit.ts','contracts/edit-generated/types.gen.ts','web/tests/edit-reconciliation.types.ts','web/src/edit-context.ts','contracts/edit-context-generated/types.gen.ts','web/src/own-observation.ts','web/tests/local-edit-save.types.ts','web/tests/history-store.types.ts','web/src/history-download.ts','web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','web/tests/history-fixture.mjs','web/tests/read-fixture.mjs','web/tests/edit-delivery-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({extends:join(capsule,owner,'web/tsconfig.edit-delivery.json'),compilerOptions:{noEmit:false,rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[...['history-store','history-download','edit-delivery','edit-delivery-entry'].map(x=>join(capsule,owner,'web/src/'+x+'.ts')),...['edit-reconciliation','local-edit-save','history-store','edit-delivery'].map(x=>join(capsule,owner,'web/tests/'+x+'.types.ts'))]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const configured=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,owner,'web/tsconfig.edit-delivery.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'configured-types.log'),configured.stdout+configured.stderr);assert.equal(configured.status,0,'actual_delivery_config_failed');checks.push('actual_delivery_tsconfig_strict_check');
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const observed=await page.evaluate(async()=>{
 const {deliverSavedEdit}=await import('/compiled/web/src/edit-delivery.js');
 const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
 const {A,O,C,Q,detail,observation,response}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
 const checks=[],ok=(value,name)=>{if(!value)throw Error(name);checks.push(name);};
 const scope={account_id:A,org_id:O},pin={...scope,capture_id:C},action='55555555-5555-4555-8555-000000000001';
 const seed=async(name,clock={now:Date.parse('2026-10-26T10:00:01Z'),tick:1},overrides={})=>{const store=await openHistoryStore(scope,{database:name,wall:()=>clock.now,monotonic:()=>clock.tick});
 await store.importEditContext({capture:detail(),editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'},...overrides},pin);
 await store.saveEdit((await store.openEdit(C)).reviewed,action,{observation_date:'2026-10-25',answers:{[Q]:{value:1}}});return store;};
 const committed={operation_id:action,command_type:'capture.edit',command_version:1,status:'committed',result:{capture_id:C,revision:'2'}};
 const unresolved={operation_id:action,command_type:'capture.edit',status:'unresolved'};
 const snapshot=detail({revision:'2',observation_date:'2026-10-25',answers:{[Q]:{value:1}}});
 const run=(store,request,options={})=>deliverSavedEdit({account_id:A,access_token:'synthetic.token'},{...scope,action_id:action},{store,request,signal:new AbortController().signal,isCurrent:()=>true,...options});
 let store=await seed('delivery-new'),calls=[];
 let result=await run(store,async(url,init)=>{calls.push([url,init.method,init.body]);return response(url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot);});
 ok(result.kind==='acknowledged'&&result.readback==='imported','new_delivery_acknowledged');ok(calls.map(x=>x[1]).join(',')==='GET,PUT,GET','recover_before_one_put_then_read');
 ok(calls[1][2]===(await store.lookupPreparedEdit({...scope,action_id:action})).serialized,'exact_frozen_put_bytes');
 ok(!(await store.read()).records[0].saved_edit,'receipt_and_readback_retire_overlay');
 await store.denyEdit();calls=[];result=await run(store,async(url,init)=>{calls.push(init.method);return response(url.includes('/operations/')?committed:snapshot);});
 ok(result.kind==='acknowledged'&&calls.join(',')==='GET,GET','recovery_after_edit_denial_without_put');ok((await store.openEdit(C)).kind==='denied','readback_never_renews_edit');store.close();
 store=await seed('delivery-uncertain');calls=[];result=await run(store,async(url,init)=>{calls.push(init.method);return response({},200);});ok(result.kind==='invalid_response'&&calls.join(',')==='GET','malformed_recovery_no_blind_send');ok((await store.lookupPreparedEdit({...scope,action_id:action})).kind==='prepared','uncertainty_keeps_original');store.close();
 store=await seed('delivery-readback-failure');result=await run(store,async(url,init)=>{if(!url.includes('/operations/')&&init.method==='GET')throw Error('offline');return response(url.includes('/operations/')?unresolved:committed);});ok(result.kind==='acknowledged'&&result.readback==='unavailable','durable_ack_survives_failed_readback');ok((await store.read()).records[0].saved_edit,'failed_readback_keeps_overlay');store.close();
 store=await seed('delivery-timeout');let puts=0;result=await run(store,async()=>new Promise(()=>{}),{timeoutMs:20});ok(result.kind==='verification_unavailable'&&puts===0,'one_total_deadline_bounds_headers');store.close();
 store=await seed('delivery-scope');let transactions=0;const transaction=IDBDatabase.prototype.transaction;
 IDBDatabase.prototype.transaction=function(...args){transactions++;return transaction.apply(this,args);};
 try{ok((await store.lookupPreparedEdit({...scope,account_id:C,action_id:action})).kind==='invalid'&&transactions===0,'lookup_scope_rejected_before_idb');ok((await store.importCurrentDetail(snapshot,{...pin,org_id:C})).kind==='invalid'&&transactions===0,'detail_scope_rejected_before_idb');}finally{IDBDatabase.prototype.transaction=transaction;}
 const oversized=detail({child_label:'x'.repeat(524289)});ok((await store.importCurrentDetail(oversized,pin)).kind==='invalid','current_detail_size_bound');store.close();
 for(const phase of ['recover','put','read']){
  store=await seed('delivery-denial-'+phase);calls=[];
  result=await run(store,async(url,init)=>{calls.push(init.method);return response(phase==='recover'||phase==='put'&&init.method==='PUT'||phase==='read'&&!url.includes('/operations/')&&init.method==='GET'?{error:'sensitive',error_id:'access_denied'}:url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot,phase==='recover'||phase==='put'&&init.method==='PUT'||phase==='read'&&!url.includes('/operations/')&&init.method==='GET'?403:200);});
  ok(phase==='read'?result.kind==='acknowledged'&&result.readback==='unavailable':result.kind==='denied','denial_safe_'+phase);
  ok(phase==='put'?(await store.read()).kind==='available'&&(await store.openEdit(C)).kind==='denied':(await store.read()).kind==='unavailable','denial_partition_or_edit_'+phase);store.close();
 }
 store=await seed('delivery-put-unverifiable');result=await run(store,async(url,init)=>{if(init.method==='PUT')return response({error:'secret',error_id:'access_denied'},403);if(!url.includes('/operations/'))throw Error('offline');return response(unresolved);});ok(result.kind==='denied'&&(await store.read()).kind==='unavailable','ambiguous_put_denial_locks_on_unverifiable_probe');store.close();
 store=await seed('delivery-conflict');result=await run(store,async(url,init)=>response(url.includes('/operations/')?unresolved:init.method==='PUT'?{error:'secret',error_id:'kdg_capture.capture_revision_conflict',current_revision:'2'}:detail({revision:'2'}),init.method==='PUT'?409:200));ok(result.kind==='conflict'&&result.readback==='imported','exact_conflict_imports_detail');ok((await store.read()).records[0].edit_status==='Needs attention'&&!(await store.readEditActions()).actions[0].delivery.receipt,'conflict_retains_attention_without_receipt');store.close();
 for(const phase of ['lookup','receipt','import']){
  store=await seed('delivery-storage-'+phase);const wrapped={...store,[phase==='lookup'?'lookupPreparedEdit':phase==='receipt'?'consumeEditReceipt':'importCurrentDetail']:async()=>{throw Error('storage');}};
  result=await run(wrapped,async(url,init)=>response(url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot));
  ok(phase==='import'?result.kind==='acknowledged'&&result.readback==='unavailable':result.kind==='verification_unavailable','storage_failure_safe_'+phase);store.close();
 }
 store=await seed('delivery-slow-storage');calls=[];result=await run({...store,lookupPreparedEdit:async()=>new Promise(()=>{})},async(...args)=>{calls.push(args);return response();},{timeoutMs:20});ok(result.kind==='verification_unavailable'&&calls.length===0,'deadline_includes_slow_storage');store.close();
 for(const phase of ['headers','body']){
  store=await seed('delivery-slow-'+phase);result=await run(store,async()=>phase==='headers'?new Promise(()=>{}):new Response(new ReadableStream({start(){}}),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}),{timeoutMs:20});ok(result.kind==='verification_unavailable','deadline_bounds_'+phase);store.close();
 }
 for(const reason of ['abort','session']){
  store=await seed('delivery-stale-'+reason);let fresh=true;const controller=new AbortController();calls=[];
  result=await run(store,async(url,init)=>{calls.push(init.method);if(reason==='abort')controller.abort();else fresh=false;return response(committed);},{signal:controller.signal,isCurrent:()=>fresh});
  ok(result.kind===(reason==='abort'?'cancelled':'superseded')&&calls.join(',')==='GET','stale_suppresses_success_'+reason);ok(!(await store.readEditActions()).actions[0].delivery.receipt,'stale_never_consumes_receipt_'+reason);store.close();
 }
 store=await seed('delivery-newer-save');const next='55555555-5555-4555-8555-000000000002';
 result=await run(store,async(url,init)=>{if(init.method==='PUT')await store.saveEdit((await store.openEdit(C)).reviewed,next,{observation_date:'2026-10-25',answers:{[Q]:{value:2}}});return response(url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot);});ok(result.kind==='acknowledged'&&(await store.read()).records[0].saved_edit.action_id===next,'newer_save_overlay_survives_readback');store.close();
 store=await seed('delivery-duplicates');const bodies=[];
 const request=async(url,init)=>{if(init.method==='PUT')bodies.push(init.body);return response(url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot);};
 const duplicate=await Promise.all([run(store,request),run(store,request)]);ok(duplicate.every(x=>x.kind==='acknowledged')&&bodies.length===2&&bodies[0]===bodies[1],'simultaneous_calls_use_identical_operation');store.close();
 for(const failure of ['auth','unavailable','unresolved_denied','unsupported','predecessor']){
  store=await seed('delivery-blocked-'+failure);calls=[];
  if(failure==='unresolved_denied'){await store.prepareEdit(action);await store.denyEdit();}
  let selected=action;
  if(failure==='predecessor'){selected='55555555-5555-4555-8555-000000000002';await store.saveEdit((await store.openEdit(C)).reviewed,selected,{observation_date:'2026-10-25',answers:{[Q]:{value:2}}});}
  if(failure==='unsupported'){
   const db=await new Promise(resolve=>{const q=indexedDB.open('delivery-blocked-'+failure);q.onsuccess=()=>resolve(q.result);});
   await new Promise(resolve=>{const tx=db.transaction('edit_actions','readwrite'),st=tx.objectStore('edit_actions'),q=st.get(A+'/'+O+'/'+action);q.onsuccess=()=>st.put({...q.result,version:2});tx.oncomplete=resolve;});db.close();
  }
  result=await deliverSavedEdit({account_id:A,access_token:'synthetic.token'},{...scope,action_id:selected},{store,signal:new AbortController().signal,isCurrent:()=>true,request:async(url,init)=>{calls.push(init.method);if(failure==='unavailable')throw Error('offline');return response(failure==='auth'?{error:'secret',error_id:'authentication_required'}:unresolved,failure==='auth'?401:200);}});
  ok(result.kind===(failure==='auth'?'error':failure==='unavailable'?'verification_unavailable':failure==='unresolved_denied'?'denied':'blocked')&&!calls.includes('PUT'),'blocked_or_uncertain_no_put_'+failure);store.close();
 }
 for(const mode of ['committed','unresolved']){
  const clock={now:Date.parse('2026-10-27T10:00:01Z'),tick:1},read={...observation(),checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};
  store=await seed('delivery-edit-expired-'+mode,clock,{read_observation:read});await store.prepareEdit(action);
  clock.tick+=Date.parse('2026-11-02T10:00:01Z')-clock.now;clock.now=Date.parse('2026-11-02T10:00:01Z');calls=[];
  result=await run(store,async(url,init)=>{calls.push(init.method);return response(url.includes('/operations/')?(mode==='committed'?committed:unresolved):snapshot);});
  ok(mode==='committed'?result.kind==='acknowledged'&&result.readback==='imported':result.kind==='expired','independent_edit_expiry_'+mode);ok(!calls.includes('PUT'),'edit_expiry_never_put_'+mode);store.close();
 }
 store=await seed('delivery-one-total-deadline');calls=[];
 result=await run({...store,lookupPreparedEdit:async(...args)=>{await new Promise(r=>setTimeout(r,15));return store.lookupPreparedEdit(...args);}},async(url,init)=>{calls.push(init.method);await new Promise(r=>setTimeout(r,15));return response(unresolved);},{timeoutMs:25});
 ok(result.kind==='verification_unavailable'&&calls.every(method=>method==='GET')&&calls.length<=1,'one_total_deadline_across_storage_and_http');store.close();
 store=await seed('delivery-receipt-stale');let fresh=true;
 result=await run({...store,consumeEditReceipt:async(...args)=>{const value=await store.consumeEditReceipt(...args);fresh=false;return value;}},async(url,init)=>response(url.includes('/operations/')?unresolved:committed),{isCurrent:()=>fresh});
 ok(result.kind==='superseded'&&(await store.readEditActions()).actions[0].delivery.receipt,'late_storage_commit_retained_without_stale_publication');store.close();
 // Entry uses the real generated Auth lifecycle with synthetic admission only.
 const {createEditDeliveryEntry}=await import('/compiled/web/src/edit-delivery-entry.js');
 for(const mode of ['success','invalid','dispose','release_error']){
  store=await seed('delivery-entry-'+mode);let callback,seenSignal,releaseAborts=0;calls=[];
  const provider={user:{id:A},access_token:'synthetic.token'},auth={getSession:async()=>({data:{session:provider},error:null}),refreshSession:async()=>({data:{session:provider},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return {data:{subscription:{unsubscribe(){}}}};}};
  const wrapped={...store,lookupPreparedEdit:async(pin,execution)=>{seenSignal=execution.signal;execution.signal.addEventListener('abort',()=>releaseAborts++);return store.lookupPreparedEdit(pin,execution);}};
  let gate;gate=createEditDeliveryEntry({org:O,store:wrapped,auth,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{
   if(url.startsWith('/api/v1/context')){const observationValue=observation();delete observationValue.expires_at;return response(observationValue);}
   calls.push(init.method);if(mode==='dispose')gate.dispose();return response(url.includes('/operations/')?unresolved:init.method==='PUT'?committed:snapshot);
  }});
  ok((await gate.deliver({...scope,action_id:action})).kind==='superseded','entry_unadmitted_'+mode);await gate.start();
  const originalAbort=AbortController.prototype.abort;
  if(mode==='release_error')AbortController.prototype.abort=function(...args){if(this.signal===seenSignal)throw Error('release');return originalAbort.apply(this,args);};
  try{result=await gate.deliver({...scope,account_id:mode==='invalid'?C:A,action_id:action});}finally{AbortController.prototype.abort=originalAbort;}
  ok(result.kind===(mode==='success'?'acknowledged':mode==='invalid'?'invalid_request':mode==='dispose'?'superseded':'verification_unavailable'),'entry_safe_result_'+mode);
  if(mode==='success')ok(seenSignal.aborted&&releaseAborts===1,'entry_releases_one_lease');
  if(mode==='invalid')ok(calls.length===0,'entry_scope_no_network');ok(gate.acquireExecution===undefined&&typeof callback==='function','entry_hides_lease_'+mode);gate.dispose();store.close();
 }
 const reviewFailures=[],reviewOk=(value,name)=>{checks.push(name);if(!value)reviewFailures.push(name);};
 store=await seed('review-put-denial-probe-timeout');let probeSawEditDenied=false;
 result=await run(store,async(url,init)=>{if(init.method==='PUT')return response({error:'secret',error_id:'access_denied'},403);if(url.includes('/operations/'))return response(unresolved);probeSawEditDenied=(await store.openEdit(C)).kind==='denied';return new Promise(()=>{});},{timeoutMs:200});
 reviewOk(['verification_unavailable','denied'].includes(result.kind)&&probeSawEditDenied&&(await store.openEdit(C)).kind!=='opened','review_put_denial_latched_before_probe_timeout');store.close();
 for(const mode of ['both','lookup_only']){
  store=await seed('review-owned-command-'+mode);const original=await store.prepareEdit(action),mutable=structuredClone(original);calls=[];
  const wrapped={...store,lookupPreparedEdit:async()=>mutable,prepareEdit:mode==='both'?async()=>mutable:store.prepareEdit};
  result=await run(wrapped,async(url,init)=>{calls.push([url,init.method,init.body]);if(url.includes('/operations/')){mutable.pending.capture_id=Q;mutable.pending.command.observation_date='2026-10-24';mutable.serialized=JSON.stringify(mutable.pending.command);return response(unresolved);}return response(init.method==='PUT'?committed:snapshot);});
  reviewOk(mode==='both'?result.kind==='invalid_request'&&!calls.some(x=>x[1]==='PUT'):result.kind==='acknowledged'&&calls.find(x=>x[1]==='PUT')?.[2]===original.serialized&&calls.find(x=>x[1]==='PUT')?.[0].endsWith('/'+C),'review_adapter_mutation_preserves_original_'+mode);store.close();
 }
 for(const field of ['account','org','action','capture','serialized']){
  store=await seed('review-returned-scope-'+field);const prepared=structuredClone(await store.prepareEdit(action));calls=[];
  if(field==='account')prepared.pending.account_id=Q;
  else if(field==='org')prepared.pending.org_id=Q;
  else if(field==='action'){prepared.pending.command.operation_id=Q;prepared.serialized=JSON.stringify(prepared.pending.command);}
  else if(field==='capture')prepared.pending.capture_id='invalid';
  else prepared.serialized+=' ';
  result=await run({...store,lookupPreparedEdit:async()=>prepared},async(...args)=>{calls.push(args);return response();});
  reviewOk(result.kind==='invalid_request'&&calls.length===0,'review_returned_'+field+'_rejected_before_http');store.close();
 }
 for(const mode of ['successor_save','successor_delivery']){
  store=await seed('review-held-readback-'+mode);let release,readStarted;
  const held=new Promise(r=>release=r),started=new Promise(r=>readStarted=r);
  const older=run(store,async(url,init)=>{if(!url.includes('/operations/')&&init.method==='GET'){readStarted();await held;return response(snapshot);}return response(url.includes('/operations/')?unresolved:committed);});await Promise.race([started,older.then(value=>{throw Error('review_readback_not_started '+JSON.stringify(value));})]);
  await store.saveEdit((await store.openEdit(C)).reviewed,next,{observation_date:'2026-10-25',answers:{[Q]:{value:2}}});
  let latest;
  if(mode==='successor_delivery'){
   const nextReceipt={...committed,operation_id:next,result:{capture_id:C,revision:'3'}},nextUnresolved={...unresolved,operation_id:next},nextSnapshot=detail({revision:'3',observation_date:'2026-10-25',answers:{[Q]:{value:2}}});
   const successor=await deliverSavedEdit({account_id:A,access_token:'synthetic.token'},{...scope,action_id:next},{store,signal:new AbortController().signal,isCurrent:()=>true,request:async(url,init)=>response(url.includes('/operations/')?nextUnresolved:init.method==='PUT'?nextReceipt:nextSnapshot)});
   reviewOk(successor.kind==='acknowledged','review_successor_delivered_during_older_readback');
   const third='55555555-5555-4555-8555-000000000003';await store.saveEdit((await store.openEdit(C)).reviewed,third,{observation_date:'2026-10-25',answers:{[Q]:{value:3}}});latest=(await store.read()).records[0];
  }
  release();const oldResult=await older,row=(await store.read()).records[0];
  reviewOk(oldResult.kind==='acknowledged'&&(mode==='successor_save'?row.saved_edit?.action_id===next&&row.edit_status==='Pending'&&row.baseline.revision==='2':row.saved_edit?.action_id===latest.saved_edit.action_id&&row.edit_status===latest.edit_status&&JSON.stringify(row.baseline)===JSON.stringify(latest.baseline)),'review_older_readback_preserves_'+mode);store.close();
 }
 ok(reviewFailures.length===0,'review_regressions '+reviewFailures.join(','));
 return checks;
 });checks.push(...observed);passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}finally{
 if(browser)await browser.close();if(server){const done=new Promise(r=>server.close(r));for(const s of sockets)s.destroy();await done;}
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,checks,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limits:['synthetic Chromium IndexedDB only','no physical persistence, eviction or at-rest claim','restart checks persist wall watermark; monotonic anchor exists only within process']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));if(!record.passed)process.exitCode=1;
}
