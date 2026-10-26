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
const proof=join(root,'platform/deployment/.local/kdg-explicit-create-delivery-20261026/focused-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/src/create-delivery.ts','web/src/create-delivery-entry.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/src/recovery.ts','contracts/recovery-generated/types.gen.ts','web/tsconfig.create-delivery.json','web/tsconfig.auth.json','web/tests/create-delivery.types.ts','web/tests/local-create-save.types.ts','web/src/history-store.ts','web/src/create.ts','contracts/create-generated/types.gen.ts','web/src/own-observation.ts','web/src/provision.ts','web/src/edit-context.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','web/offline-tools/idb.ts','contracts/edit-context-generated/types.gen.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','contracts/provision-generated/types.gen.ts','web/tests/read-fixture.mjs','web/tests/provision-fixture.mjs','web/tests/create-delivery-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[join(capsule,owner,'web/src/create-delivery-entry.ts'),join(capsule,owner,'web/tests/create-delivery.types.ts'),join(capsule,owner,'web/src/history-store.ts'),join(capsule,owner,'web/tests/local-create-save.types.ts')]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const configured=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,owner,'web/tsconfig.create-delivery.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'configured-types.log'),configured.stdout+configured.stderr);assert.equal(configured.status,0,'actual_create_delivery_config_failed');checks.push('actual_create_delivery_config_strict_check');
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const out=await page.evaluate(async()=>{
 const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
 const {deliverSavedCreate}=await import('/compiled/web/src/create-delivery.js');
 const {A,O,C,Q,provision,actor,response}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');
 const {detail}=await import('/apps/kdg-capture/web/tests/read-fixture.mjs');
 const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const scope={account_id:A,org_id:O},ids={capture_id:'88888888-8888-4888-8888-888888888888',operation_id:'99999999-9999-4999-8999-999999999999'},pin={...scope,action_id:ids.operation_id};
 const input={observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value:1}}};
 const receipt={operation_id:ids.operation_id,command_type:'capture.create',command_version:1,status:'committed',result:{capture_id:ids.capture_id,revision:'1'}},unresolved={operation_id:ids.operation_id,command_type:'capture.create',status:'unresolved'};
 const snapshot=detail({capture_id:ids.capture_id,owner_actor_id:actor,created_by:actor,child_id:C,captured_at:input.captured_at,answers:input.answers,observation_date:input.observation_date});
 const seed=async(name)=>{
  const clock={now:Date.parse('2026-10-26T10:00:02Z'),tick:1},opts={database:'create-delivery-'+name,wall:()=>clock.now,monotonic:()=>clock.tick};
  const store=await openHistoryStore(scope,opts),ticket=await store.beginSetupRefresh();ok((await store.importProvision(provision(),ticket.ticket)).kind==='committed','seed_'+name);
  const reviewed=(await store.openCreate(C)).reviewed;ok((await store.saveCreate(reviewed,ids,input)).kind==='saved_locally','save_'+name);return {store,clock,opts,reviewed};
 };
 const run=(store,request,opts={})=>deliverSavedCreate({account_id:A,access_token:'synthetic.token'},pin,{store,request,signal:new AbortController().signal,isCurrent:()=>true,...opts});
 const standard=(calls=[],recovery=unresolved,read=snapshot)=>async(url,init)=>{calls.push([url,init.method,init.body]);return response(url.includes('/operations/')?recovery:init.method==='POST'?receipt:read);};
 const {getCurrentContext}=await import('/compiled/web/src/entry.js');
 const emptyStarted=performance.now();let pulls=0;
 const emptyResult=await getCurrentContext({account_id:A,access_token:'synthetic.token'},O,{timeoutMs:20,request:async()=>new Response(new ReadableStream({pull(controller){pulls++;if(performance.now()-emptyStarted<90)controller.enqueue(new Uint8Array());else{const {expires_at,...context}=provision().read_observation;controller.enqueue(new TextEncoder().encode(JSON.stringify(context)));controller.close();}}}))});
 ok(emptyResult.kind==='authorization_unavailable'&&performance.now()-emptyStarted<80&&pulls>0,'context_empty_chunks_bounded_by_monotonic_deadline');
 let seeded=await seed('first'),store=seeded.store,calls=[],result=await run(store,standard(calls));
 ok(result.kind==='acknowledged'&&result.readback==='imported','first_delivery_receipt_and_current_readback');ok(calls.map(x=>x[1]).join(',')==='GET,POST,GET','original_recovery_before_single_post');
 ok(calls[1][2]===(await store.lookupPreparedCreate(pin)).serialized,'post_uses_exact_original_bytes');
 let row=(await store.read()).records[0],action=(await store.readCreateActions()).actions[0];
 ok(row.create_status==='Synced'&&row.local_capture.answers[Q].value===1&&row.baseline.revision==='1','bound_actual_detail_synchronizes_preserving_local_evidence');
 ok(action.delivery.receipt.result.revision==='1'&&action.delivery.readback_revision==='1','durable_original_receipt_and_current_revision');
 ok((await store.saveCreate(seeded.reviewed,ids,input)).kind==='saved_locally','original_save_retry_survives_delivery');
 store.close();store=await openHistoryStore(scope,seeded.opts);calls=[];result=await run(store,standard(calls,receipt));ok(result.kind==='acknowledged'&&calls.map(x=>x[1]).join(',')==='GET,GET','reopen_recovers_original_without_post');store.close();
 for(const scenario of ['lost','receipt_failure','read_failure','newer','mismatch','wrong_target','wrong_version','history_only','unsupported','attention','expired','child_omitted','create_denied','read_denied','busy','unavailable','malformed','scope','abort','session','slow_storage','slow_headers','slow_body','denial_probe','denial_probe_missing']){
  seeded=await seed(scenario);store=seeded.store;calls=[];
  if(scenario==='lost'||scenario==='receipt_failure'){
   let posts=0;const wrapped=scenario==='receipt_failure'?{...store,consumeCreateReceipt:async()=>({kind:'unavailable'})}:store;
   result=await run(wrapped,async(url,init)=>{if(init.method==='POST'){posts++;if(scenario==='lost')throw Error('lost committed response');}return standard()(url,init);});
   ok(result.kind===(scenario==='lost'?'verification_unavailable':'unavailable'),'uncertain_'+scenario);
   result=await run(store,standard(calls,receipt));ok(result.kind==='acknowledged'&&posts===1&&!calls.some(x=>x[1]==='POST'),'original_recovery_no_repeat_'+scenario);
  }
  if(scenario==='read_failure'){
   result=await run(store,async(url,init)=>{if(!url.includes('/operations/')&&init.method==='GET')throw Error('offline');return standard()(url,init);});
   row=(await store.read()).records[0];action=(await store.readCreateActions()).actions[0];ok(result.kind==='acknowledged'&&result.readback==='unavailable'&&row.create_status==='Pending'&&!row.baseline&&action.delivery.receipt,'receipt_survives_unavailable_read_without_false_synced');
  }
  if(scenario==='newer'||scenario==='mismatch'){
   result=await run(store,standard(calls,receipt,{...snapshot,revision:scenario==='newer'?'3':'1',answers:{[Q]:{value:4}}}));
   row=(await store.read()).records[0];action=(await store.readCreateActions()).actions[0];
   ok(scenario==='newer'?result.readback==='imported'&&row.baseline.answers[Q].value===4&&action.delivery.receipt.result.revision==='1':result.readback==='unavailable'&&!row.baseline&&row.create_status==='Pending','receipt_revision_content_binding_'+scenario);
  }
  if(scenario==='wrong_target'||scenario==='wrong_version'){
   result=await run(store,standard(calls,{...receipt,...(scenario==='wrong_version'?{command_version:2}:{result:{capture_id:C,revision:'1'}})}));ok(result.kind==='invalid'||result.kind==='invalid_response','reject_'+scenario);ok(!calls.some(x=>x[1]==='POST')&&!(await store.readCreateActions()).actions[0].delivery?.receipt,'no_substitute_receipt_'+scenario);
  }
  if(scenario==='history_only'){
   await store.importCurrentDetail(snapshot,{...scope,capture_id:ids.capture_id});ok((await store.read()).records[0].create_status==='Pending','detail_alone_never_acknowledges_uncertain_operation');
  }
  if(scenario==='unsupported'){
   const db=await new Promise(resolve=>{const r=indexedDB.open(seeded.opts.database);r.onsuccess=()=>resolve(r.result);});await new Promise(resolve=>{const tx=db.transaction('create_actions','readwrite'),st=tx.objectStore('create_actions'),r=st.get(A+'/'+O+'/'+ids.operation_id);r.onsuccess=()=>st.put({...r.result,delivery:{version:2,opaque:'retained'}});tx.oncomplete=resolve;});db.close();result=await run(store,standard(calls));ok(result.kind==='blocked'&&calls.length===0,'unsupported_delivery_retained_without_http');
  }
  if(scenario==='attention'){
   result=await run(store,async(url,init)=>{calls.push(init.method);return response(init.method==='POST'?{error:'safe',error_id:'assignment_unavailable'}:unresolved,init.method==='POST'?403:200);});
   ok(result.kind==='error'&&calls.join(',')==='GET,POST'&&(await store.readCreateActions()).actions[0].delivery.attention==='assignment_unavailable'&&(await store.read()).records[0].create_status==='Needs attention','scoped_rejection_retains_attention_and_read');
  }
  if(scenario==='expired'){
   const t=await store.beginSetupRefresh(),p=provision();p.read_observation={...p.read_observation,checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};
   seeded.clock.now=Date.parse('2026-10-27T10:00:01Z');seeded.clock.tick+=86400000-1000;await store.importProvision(p,t.ticket);seeded.clock.tick+=6*86400000;seeded.clock.now+=6*86400000;
   result=await run(store,standard(calls));ok(result.kind==='acknowledged'&&calls.some(x=>x[1]==='POST'),'expired_original_create_setup_does_not_veto_delayed_post');
  }
  if(scenario==='child_omitted'){
   const t=await store.beginSetupRefresh(),p=provision();p.children=[];p.create_state='no_eligible_children';ok((await store.importProvision(p,t.ticket)).kind==='committed','current_child_omission_imported');result=await run(store,standard(calls));ok(result.kind==='acknowledged'&&calls.some(x=>x[1]==='POST'),'current_child_list_omission_alone_does_not_veto_original_reference');
  }
  if(scenario==='create_denied'){
   await store.denyCreate(pin);result=await run(store,standard(calls));ok(result.kind==='denied'&&calls.length===1,'known_creation_denial_blocks_post');calls=[];result=await run(store,standard(calls,receipt));ok(result.kind==='acknowledged'&&calls.length===2,'receipt_recovery_survives_creation_denial');
  }
  if(scenario==='read_denied'){
   result=await run(store,async()=>response({error:'safe',error_id:'access_denied'},403));ok(result.kind==='denied'&&(await store.read()).kind==='unavailable','recovery_read_denial_locks');
  }
  if(['busy','unavailable','malformed'].includes(scenario)){
   result=await run(store,async(url,init)=>{calls.push(init.method);if(scenario==='unavailable')throw Error('offline');return response(scenario==='malformed'?{}:{error:'safe',error_id:'operation_busy'},scenario==='malformed'?200:409);});ok(!calls.includes('POST'),'uncertain_recovery_never_sends_'+scenario);
  }
  if(scenario==='scope'){
   result=await run({...store,lookupPreparedCreate:async()=>({kind:'prepared',pending:{...((await store.lookupPreparedCreate(pin)).pending),org_id:C},serialized:'{}'})},standard(calls));ok(result.kind==='invalid_request'&&calls.length===0,'adapter_scope_checked_before_http');
  }
  if(scenario==='abort'||scenario==='session'){
   let fresh=true;const controller=new AbortController();result=await run(store,async(url,init)=>{calls.push(init.method);if(scenario==='abort')controller.abort();else fresh=false;return response(receipt);},{signal:controller.signal,isCurrent:()=>fresh});ok(result.kind===(scenario==='abort'?'cancelled':'superseded')&&calls.join(',')==='GET'&&!(await store.readCreateActions()).actions[0].delivery?.receipt,'execution_fence_'+scenario);
  }
  if(scenario.startsWith('slow_')){
   const wrapped=scenario==='slow_storage'?{...store,lookupPreparedCreate:async()=>new Promise(()=>{})}:store;
   result=await run(wrapped,async()=>scenario==='slow_body'?new Response(new ReadableStream({start(){}}),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}}):new Promise(()=>{}),{timeoutMs:20});ok(result.kind==='verification_unavailable','total_deadline_'+scenario);
  }
  if(scenario.startsWith('denial_probe')){
   result=await run(store,async(url,init)=>{calls.push(url);if(url==='/api/v1/context'){if(scenario==='denial_probe_missing')throw Error('offline');const p=provision(),{expires_at,...context}=p.read_observation;return response(context);}return response(init.method==='POST'?{error:'safe',error_id:'access_denied'}:unresolved,init.method==='POST'?403:200);});
   ok(result.kind==='denied'&&calls.at(-1)==='/api/v1/context','post_denial_uses_current_context_'+scenario);ok((await store.read()).kind===(scenario==='denial_probe'?'available':'unavailable'),'post_denial_read_scope_'+scenario);
  }
  store.close();
 }
 for(const direction of ['assigned_to_all','all_to_assigned']){
  const clock={now:Date.parse('2026-10-26T10:00:02Z'),tick:1},opts={database:'create-delivery-transition-'+direction,wall:()=>clock.now,monotonic:()=>clock.tick};store=await openHistoryStore(scope,opts);
  const original=provision();if(direction==='all_to_assigned'){original.create_all_observation={...original.create_assigned_observation,permission:'kdg_capture.capture.create.all'};original.create_assigned_observation=null;original.children[0].create_permission='kdg_capture.capture.create.all';original.children[0].assignment=null;}
  let ticket=await store.beginSetupRefresh();ok((await store.importProvision(original,ticket.ticket)).kind==='committed','original_capability_'+direction);await store.saveCreate((await store.openCreate(C)).reviewed,ids,input);await store.denyCreate(pin);
  ok((await store.prepareCreate(pin)).kind==='denied','both_creation_capabilities_latched_'+direction);
  clock.now+=1000;clock.tick+=1000;const replacement=provision(),next=direction==='assigned_to_all'?'create_all_observation':'create_assigned_observation',other=direction==='assigned_to_all'?'create_assigned_observation':'create_all_observation';replacement.children=[];replacement.create_state='no_eligible_children';replacement[next]={...original.read_observation,permission:next==='create_all_observation'?'kdg_capture.capture.create.all':'kdg_capture.capture.create.assigned',checked_at:'2026-10-26T10:00:03Z',expires_at:'2026-11-02T10:00:03Z'};replacement[other]=null;
  ticket=await store.beginSetupRefresh();ok((await store.importProvision(replacement,ticket.ticket)).kind==='committed','explicit_newer_capability_'+direction);
  calls=[];result=await run(store,standard(calls));ok(result.kind==='acknowledged'&&calls.some(x=>x[1]==='POST'),'newer_other_creation_capability_allows_original_post_'+direction);store.close();
 }
 for(const scenario of ['quota','completion','queued_abort','newer_overlay']){
  seeded=await seed(scenario);store=seeded.store;calls=[];
  if(scenario==='quota'){
   const put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(value,...args){if(this.name==='create_actions'&&value.delivery?.receipt){this.transaction.abort();throw Error('synthetic quota');}return put.call(this,value,...args);};
   try{result=await run(store,standard(calls));}finally{IDBObjectStore.prototype.put=put;}
   ok(result.kind==='unavailable'&&!(await store.readCreateActions()).actions[0].delivery?.receipt,'failed_receipt_write_never_acknowledges');
  }
  if(scenario==='completion'){
   let fresh=true;const wrapped={...store,consumeCreateReceipt:async(...args)=>{const value=await store.consumeCreateReceipt(...args);fresh=false;return value;}};
   result=await run(wrapped,standard(calls),{isCurrent:()=>fresh});ok(result.kind==='superseded'&&(await store.readCreateActions()).actions[0].delivery.receipt,'completion_uncertainty_retains_original_receipt_without_publication');
  }
  if(scenario==='queued_abort'){
   const db=await new Promise(resolve=>{const q=indexedDB.open(seeded.opts.database);q.onsuccess=()=>resolve(q.result);});let hold=true;
   const tx=db.transaction('create_actions','readwrite'),st=tx.objectStore('create_actions');const keep=()=>{const r=st.get('holding');r.onsuccess=()=>{if(hold)keep();};};keep();
   result=await run(store,standard(calls),{timeoutMs:20});hold=false;await new Promise(resolve=>{tx.oncomplete=resolve;});db.close();ok(result.kind==='verification_unavailable'&&calls.length===0,'queued_idb_cancelled_before_any_http');
  }
  if(scenario==='newer_overlay'){
   const next='66666666-6666-4666-8666-666666666666';result=await run(store,async(url,init)=>{
    if(!url.includes('/operations/')&&init.method==='GET'){
     const read=provision().read_observation;await store.importEditContext({capture:snapshot,editable_fields:['observation_date','answers'],read_observation:read,edit_observation:{...read,permission:'kdg_capture.capture.edit.own'}},{...scope,capture_id:ids.capture_id});
     await store.saveEdit((await store.openEdit(ids.capture_id)).reviewed,next,{observation_date:'2026-10-25',answers:{[Q]:{value:2}}});
    }return standard()(url,init);
   });row=(await store.read()).records[0];ok(result.kind==='acknowledged'&&row.saved_edit.action_id===next&&row.edit_status==='Pending','create_readback_preserves_newer_local_edit_overlay');
  }
  store.close();
 }
 for(const envelope of [null,false,0,'',{version:1,receipt:null},{version:1,receipt:false},{version:1,attention:null},{version:1,receipt,attention:'assignment_unavailable'},{version:1,readback_revision:null}]){
  seeded=await seed('envelope-'+JSON.stringify(envelope));store=seeded.store;const db=await new Promise(resolve=>{const q=indexedDB.open(seeded.opts.database);q.onsuccess=()=>resolve(q.result);});await new Promise(resolve=>{const tx=db.transaction('create_actions','readwrite'),st=tx.objectStore('create_actions'),q=st.get(A+'/'+O+'/'+ids.operation_id);q.onsuccess=()=>st.put({...q.result,delivery:envelope});tx.oncomplete=resolve;});db.close();calls=[];result=await run(store,standard(calls));ok(result.kind==='blocked'&&calls.length===0,'malformed_envelope_retained_blocked_'+JSON.stringify(envelope));store.close();
 }
 for(const phase of ['transaction','read','write']){
  seeded=await seed('denial-fails-'+phase);store=seeded.store;const target=phase==='transaction'?IDBDatabase.prototype:IDBObjectStore.prototype,key=phase==='transaction'?'transaction':phase==='read'?'get':'put',original=target[key];let failed=false;
  target[key]=function(...args){if(!failed){failed=true;throw Error('synthetic denial persistence failure');}return original.apply(this,args);};
  try{result=await store.denyCreate(pin);}finally{target[key]=original;}
  ok(result.kind==='unavailable','denial_persistence_failure_visible_'+phase);ok((await store.prepareCreate(pin)).kind==='denied','failed_denial_latches_both_capabilities_'+phase);
  const otherIds={capture_id:'66666666-6666-4666-8666-666666666666',operation_id:'77777777-7777-4777-8777-777777777778'};
  ok((await store.saveCreate(seeded.reviewed,otherIds,input)).kind==='denied','old_form_cannot_revive_failed_denial_'+phase);store.close();
 }
 seeded=await seed('negative-floor');store=seeded.store;
 const floorDB=await new Promise(resolve=>{const q=indexedDB.open(seeded.opts.database);q.onsuccess=()=>resolve(q.result);});await new Promise(resolve=>{const tx=floorDB.transaction('partitions','readwrite'),st=tx.objectStore('partitions'),q=st.get(A+'/'+O);q.onsuccess=()=>st.put({...q.result,createGenerations:{...q.result.createGenerations,create_assigned_observation:7}});tx.oncomplete=resolve;});floorDB.close();
 const oldReviewed=(await store.openCreate(C)).reviewed,originalTransaction=IDBDatabase.prototype.transaction;
 IDBDatabase.prototype.transaction=function(){throw Error('synthetic transaction acquisition failure');};try{await store.denyCreate(pin);}finally{IDBDatabase.prototype.transaction=originalTransaction;}
 const laterIds={capture_id:'66666666-6666-4666-8666-666666666667',operation_id:'77777777-7777-4777-8777-777777777779'};
 ok((await store.saveCreate(oldReviewed,laterIds,input)).kind==='denied','negative_time_floor_blocks_old_form_even_with_higher_durable_generation');
 const staleTicket=await store.beginSetupRefresh();ok((await store.importProvision(provision(),staleTicket.ticket)).kind==='denied','old_positive_observation_cannot_restore_failed_denial');ok((await store.openCreate(C)).kind==='denied','current_observation_respects_negative_time_floor');store.close();
 seeded=await seed('attention-complete');store=seeded.store;await run(store,standard());const before=JSON.stringify((await store.readCreateActions()).actions[0]);await store.attentionCreate(pin,'assignment_unavailable');ok(JSON.stringify((await store.readCreateActions()).actions[0])===before&&(await store.read()).records[0].create_status==='Synced','late_rejection_cannot_overwrite_committed_receipt');store.close();
 for(const phase of ['denial','attention']){
  seeded=await seed('retention-fails-'+phase);store=seeded.store;const wrapped={...store,[phase==='denial'?'denyCreate':'attentionCreate']:async()=>({kind:'unavailable'})};
  result=await run(wrapped,async(url,init)=>response(init.method==='POST'?{error:'safe',error_id:phase==='denial'?'access_denied':'assignment_unavailable'}:unresolved,init.method==='POST'?403:200));ok(result.kind==='unavailable','retention_failure_exposed_'+phase);store.close();
 }
 seeded=await seed('read403');store=seeded.store;result=await run(store,async(url,init)=>response(url.includes('/operations/')?unresolved:init.method==='POST'?receipt:{error:'safe',error_id:'access_denied'},!url.includes('/operations/')&&init.method==='GET'?403:200));ok(result.kind==='acknowledged'&&result.readback==='unavailable'&&(await store.read()).kind==='unavailable','detail403_locks_after_receipt');store.close();
 const locked=await openHistoryStore(scope,seeded.opts);ok((await locked.read()).kind==='unavailable','detail403_protected_reads_remain_locked_on_reopen');locked.close();
 const inspect=await new Promise(resolve=>{const q=indexedDB.open(seeded.opts.database);q.onsuccess=()=>resolve(q.result);});
 const persisted=await new Promise(resolve=>{const tx=inspect.transaction(['create_actions','records'],'readonly'),a=tx.objectStore('create_actions').get(A+'/'+O+'/'+ids.operation_id),r=tx.objectStore('records').get(A+'/'+O+'/'+ids.capture_id);tx.oncomplete=()=>resolve({action:a.result,row:r.result});});inspect.close();ok(persisted.action.delivery.receipt.operation_id===ids.operation_id&&persisted.row.local_capture.answers[Q].value===1&&!persisted.row.baseline,'detail403_keeps_original_intent_and_receipt_on_reopen');
 seeded=await seed('local-receipt-unresolved');store=seeded.store;const frozen=(await store.lookupPreparedCreate(pin)).pending;await store.consumeCreateReceipt(frozen,{kind:'committed',receipt});calls=[];result=await run(store,standard(calls,unresolved,{...snapshot,answers:{[Q]:{value:4}}}));ok(result.kind==='acknowledged'&&result.readback==='unavailable'&&!calls.some(x=>x[1]==='POST')&&!(await store.read()).records[0].baseline,'durable_receipt_unresolved_never_posts_and_checks_detail');store.close();
 seeded=await seed('late-storage');store=seeded.store;let release,finish,expire,returned,phaseReached=false,elapsed=0;const waiting=new Promise(resolve=>release=resolve),finished=new Promise(resolve=>finish=resolve);
 // Select the receipt-storage phase before expiring the same ten-second budget.
 // A short real timer can otherwise expire during IndexedDB setup on a busy host.
 const nowDescriptor=Object.getOwnPropertyDescriptor(performance,'now'),originalTimeout=globalThis.setTimeout;
 Object.defineProperty(performance,'now',{configurable:true,value:()=>elapsed});globalThis.setTimeout=function(callback,delay,...args){const timer=originalTimeout.call(this,callback,delay,...args);if(!expire&&delay===10000)expire=()=>callback(...args);return timer;};
 const wrapped={...store,consumeCreateReceipt:async(...args)=>{phaseReached=true;elapsed=10001;expire();await waiting;try{returned=await store.consumeCreateReceipt(...args);return returned;}finally{finish();}}};
 try{result=await run(wrapped,standard(),{timeoutMs:10000});ok(phaseReached,'late_storage_phase_reached_before_expiry');release();await finished;ok(result.kind==='verification_unavailable'&&returned.kind==='unavailable'&&!(await store.readCreateActions()).actions[0].delivery?.receipt,'late_storage_execution_aborted_without_dependent_commit');}
 finally{release();globalThis.setTimeout=originalTimeout;if(nowDescriptor)Object.defineProperty(performance,'now',nowDescriptor);else delete performance.now;store.close();}
 const {createCreateDeliveryEntry}=await import('/compiled/web/src/create-delivery-entry.js');
 for(const mode of ['success','account','org','dispose','cancel','replace','reuse']){
  seeded=await seed('auth-'+mode);store=seeded.store;calls=[];let callback,seenSignal,aborts=0,gate,first=true;
  const provider={user:{id:A},access_token:'synthetic.token'},auth={getSession:async()=>({data:{session:provider},error:null}),refreshSession:async()=>({data:{session:provider},error:null}),signOut:async()=>({error:null}),onAuthStateChange:cb=>{callback=cb;return {data:{subscription:{unsubscribe(){}}}};}};
  const wrapped={...store,lookupPreparedCreate:async(pin,execution)=>{seenSignal=execution.signal;execution.signal.addEventListener('abort',()=>aborts++);return store.lookupPreparedCreate(pin,execution);}};
  gate=createCreateDeliveryEntry({org:O,auth,store:wrapped,publish(){},beginSignIn:async()=>{},request:async(url,init)=>{
   if(url==='/api/v1/context'){const {expires_at,...context}=provision().read_observation;return response(context);}calls.push(init.method);
   if(mode==='dispose')gate.dispose();if(mode==='cancel')callback('SIGNED_OUT',null);if(mode==='replace')callback('SIGNED_IN',{...provider,user:{id:C}});
   if(mode==='reuse'&&first){first=false;throw Error('offline');}return standard()(url,init);
  }});
  ok((await gate.deliver(pin)).kind==='superseded','auth_unadmitted_'+mode);await gate.start();result=await gate.deliver({...pin,...(mode==='account'?{account_id:C}:mode==='org'?{org_id:C}:{})});
  ok(result.kind===(mode==='success'?'acknowledged':mode==='account'||mode==='org'?'invalid_request':mode==='reuse'?'verification_unavailable':'superseded'),'auth_wrapper_result_'+mode);
  if(mode==='success')ok(seenSignal.aborted&&aborts===1,'auth_one_execution_lease_released');
  if(mode==='account'||mode==='org')ok(calls.length===0,'auth_scope_no_delivery_http_'+mode);
  if(mode==='reuse'){result=await gate.deliver(pin);ok(result.kind==='acknowledged'&&aborts===2,'auth_lease_reusable_after_failed_invocation');}
  if(mode==='dispose'||mode==='cancel'||mode==='replace')ok(calls.join(',')==='GET'&&!(await store.readCreateActions()).actions[0].delivery?.receipt,'auth_cancellation_suppresses_dependent_work_'+mode);
  gate.dispose();store.close();
 }
 seeded=await seed('duplicate');store=seeded.store;calls=[];const results=await Promise.all([run(store,standard(calls)),run(store,standard(calls))]);ok(results.every(x=>x.kind==='acknowledged')&&calls.filter(x=>x[1]==='POST').every(x=>x[2]===calls.find(y=>y[1]==='POST')[2]),'competing_explicit_calls_preserve_original_command');store.close();
 return checks;
 });checks.push(...out);passed=true;
}finally{if(browser)await browser.close();if(server){for(const socket of sockets)socket.destroy();server.close();}writeFileSync(join(proof,'result.json'),JSON.stringify({passed,checks,sources:captured},null,2));console.log(JSON.stringify({proof,passed,checks:checks.length}));}
