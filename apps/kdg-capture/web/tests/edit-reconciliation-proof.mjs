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
const proof=join(root,'platform/deployment/.local/kdg-edit-reconciliation-20261026/reconciliation-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/src/provision.ts','web/src/create.ts','contracts/provision-generated/types.gen.ts','contracts/create-generated/types.gen.ts','web/src/edit.ts','contracts/edit-generated/types.gen.ts','web/tests/edit-reconciliation.types.ts','web/src/edit-context.ts','contracts/edit-context-generated/types.gen.ts','web/src/own-observation.ts','web/tests/local-edit-save.types.ts','web/tests/history-store.types.ts','web/src/history-download.ts','web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','web/tests/history-fixture.mjs','web/tests/read-fixture.mjs','web/tests/edit-reconciliation-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[...['history-store','history-download'].map(x=>join(capsule,owner,'web/src/'+x+'.ts')),...['edit-reconciliation','local-edit-save','history-store'].map(x=>join(capsule,owner,'web/tests/'+x+'.types.ts'))]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const reviewFix=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,detail,observation,page:history,pending:historyPending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const checks=[],failures=[],ok=(v,n)=>(v?checks:failures).push(n),scope={account_id:A,org_id:O},pin={...scope,capture_id:C};let serial=9000;
  const uuid=()=>`99999999-9999-4999-8999-${String(++serial).padStart(12,'0')}`,change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}});
  let now=Date.parse('2026-10-26T10:00:01Z'),tick=1;const initial=now,options=database=>({database,wall:()=>now,monotonic:()=>tick});
  const context=(capture=detail())=>({capture,editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'}});
  const receipt=(p,revision)=>({kind:'committed',receipt:{operation_id:p.pending.command.operation_id,command_type:'capture.edit',status:'committed',command_version:1,result:{capture_id:C,revision}}});
  const seed=async database=>{now=initial;tick=1;const s=await openHistoryStore(scope,options(database));await s.importEditContext(context(),pin);return s;};
  const save=async(s,value)=>{const action=uuid();await s.saveEdit((await s.openEdit(C)).reviewed,action,change(value));return action;};
  const mutate=async(database,work)=>{const db=await new Promise((resolve,reject)=>{const q=indexedDB.open(database);q.onsuccess=()=>resolve(q.result);q.onerror=reject;});await new Promise((resolve,reject)=>{const tx=db.transaction('edit_actions','readwrite');work(tx.objectStore('edit_actions'));tx.oncomplete=resolve;tx.onabort=reject;});db.close();};
  for(const lookup of ['missing','unsupported']){
   const name='review-clock-'+lookup,s=await seed(name),action=await save(s,1);
   if(lookup==='unsupported')await mutate(name,st=>{const q=st.get(A+'/'+O+'/'+action);q.onsuccess=()=>st.put({...q.result,version:2});});
   now+=120000; // Wall drift without elapsed monotonic time must not be accepted as an anchor.
   const response=await s.prepareEdit(lookup==='missing'?uuid():action);
   ok(response.kind==='unavailable','clock_'+lookup+'_rejects_drift');ok((await s.openEdit(C)).kind==='unavailable','clock_'+lookup+'_leaves_normal_operation_locked');s.close();
  }
  const variants={receipt_version:r=>({...r,command_version:2}),receipt_operation:r=>({...r,operation_id:Q}),receipt_target:r=>({...r,result:{...r.result,capture_id:Q}}),receipt_revision:r=>({...r,result:{...r.result,revision:'7'}}),receipt_extra:r=>({...r,extra:true}),receipt_status:r=>({...r,status:'unresolved'})};
  for(const [label,corrupt] of Object.entries(variants)){
   const name='review-stored-'+label,s=await seed(name),first=await save(s,1),p=await s.prepareEdit(first),second=await save(s,2);
   await mutate(name,st=>{const q=st.get(A+'/'+O+'/'+first);q.onsuccess=()=>st.put({...q.result,delivery:{...q.result.delivery,receipt:corrupt(receipt(p,'2').receipt)}});});
   ok((await s.prepareEdit(second)).kind==='blocked','stored_'+label+'_blocks_successor');
   s.close();
   const retireName=name+'-readback',latest=await seed(retireName),id=await save(latest,1),prepared=await latest.prepareEdit(id);
   await mutate(retireName,st=>{const q=st.get(A+'/'+O+'/'+id);q.onsuccess=()=>st.put({...q.result,delivery:{...q.result.delivery,receipt:corrupt(receipt(prepared,'2').receipt)}});});
   await latest.importPage(history({items:[detail({revision:'8',...change(5)})]}),historyPending());const row=(await latest.read()).records[0];ok(row.saved_edit?.action_id===id&&row.edit_status!=='Synced','stored_'+label+'_cannot_retire_overlay');latest.close();
  }
  for(const [label,conflict] of Object.entries({version:{kind:'error',status:409,error_id:'unsupported',current_revision:'2'},revision:{kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'1'},extra:{kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'2',extra:true}})){
   const name='review-stored-conflict-'+label,s=await seed(name),id=await save(s,1),p=await s.prepareEdit(id);
   await mutate(name,st=>{const q=st.get(A+'/'+O+'/'+id);q.onsuccess=()=>st.put({...q.result,delivery:{...q.result.delivery,conflict}});});
   ok((await s.prepareEdit(id)).kind==='blocked'&&(await s.consumeEditReceipt(p.pending,receipt(p,'2'))).kind==='invalid','stored_conflict_'+label+'_retained_and_blocked');s.close();
  }
  for(const field of ['answers','observation_date']){
   const s=await seed('review-mismatch-'+field),id=await save(s,1),p=await s.prepareEdit(id);await s.consumeEditReceipt(p.pending,receipt(p,'2'));
   const mismatching=detail({revision:'2',...change(1),...(field==='answers'?change(5):{observation_date:'2026-10-24'})});await s.importPage(history({items:[mismatching]}),historyPending());const row=(await s.read()).records[0];ok(row.saved_edit?.action_id===id&&row.edit_status!=='Synced','equal_revision_mismatch_'+field+'_keeps_overlay');s.close();
  }
  for(const mode of ['save','prepare']){
   const database='review-ancestry-'+mode,s=await seed(database),first=await save(s,1),p=await s.prepareEdit(first),second=await save(s,2);await s.consumeEditReceipt(p.pending,receipt(p,'2'));
   // Preserve the descendant's old reviewed base while recording parent progress.
   await s.importPage(history({items:[detail({revision:'2',...change(1)})]}),historyPending());const reviewed=(await s.openEdit(C)).reviewed;
   if(mode==='prepare'){
    // Make known remote revision unrelated, so preparation attempts an attention marker.
    await s.importPage(history({items:[detail({revision:'3',...change(5)})]}),historyPending());
   }
   const get=IDBObjectStore.prototype.get;let reads=0;
   IDBObjectStore.prototype.get=function(...args){const q=get.apply(this,args);if(this.name==='edit_actions')q.addEventListener('success',()=>{if(++reads===2){const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;}});return q;};
   let outcome;
   try{outcome=mode==='save'?await s.saveEdit(reviewed,uuid(),change(4)):await s.prepareEdit(second);}finally{IDBObjectStore.prototype.get=get;}
   ok(outcome.kind==='expired','ancestry_'+mode+'_expires_before_write');
   // Inspect raw state because current own-read has expired.
   const db=await new Promise(resolve=>{const q=indexedDB.open(database);q.onsuccess=()=>resolve(q.result);});
   const retained=await new Promise(resolve=>{const q=db.transaction('edit_actions').objectStore('edit_actions').getAll();q.onsuccess=()=>resolve(q.result);});const row=await new Promise(resolve=>{const q=db.transaction('records').objectStore('records').get(A+'/'+O+'/'+C);q.onsuccess=()=>resolve(q.result);});db.close();
   ok(retained.length===2&&row.saved_edit.action_id===second&&row.edit_status==='Pending'&&!retained.find(a=>a.action_id===second).delivery,'ancestry_'+mode+'_no_action_overlay_attention_commit');s.close();
  }
  return {checks,failures};
 });writeFileSync(join(proof,'review-fix.json'),JSON.stringify(reviewFix,null,2));checks.push(...reviewFix.checks);assert.deepEqual(reviewFix.failures,[],'review_fix_failures');
 const observed=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,detail,observation,page:history,pending:historyPending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);},scope={account_id:A,org_id:O},pin={...scope,capture_id:C};let serial=5000;
  const uuid=()=>`77777777-7777-4777-8777-${String(++serial).padStart(12,'0')}`,change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}});
  let now=Date.parse('2026-10-26T10:00:01Z'),tick=1;const options=database=>({database,wall:()=>now,monotonic:()=>tick});
  const context=(capture=detail())=>({capture,editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'}});
  const receipt=(prepared,revision)=>({kind:'committed',receipt:{operation_id:prepared.pending.command.operation_id,command_type:'capture.edit',status:'committed',command_version:1,result:{capture_id:C,revision}}});
  const seed=async database=>{const s=await openHistoryStore(scope,options(database));await s.importEditContext(context(),pin);return s;};
  const save=async(s,value)=>{const action=uuid();ok((await s.saveEdit((await s.openEdit(C)).reviewed,action,change(value))).kind==='saved_locally','save_'+action);return action;};
  const actions=async s=>(await s.readEditActions()).actions;
  const mutate=async(database,table,work)=>{const db=await new Promise((resolve,reject)=>{const q=indexedDB.open(database);q.onsuccess=()=>resolve(q.result);q.onerror=reject;});await new Promise((resolve,reject)=>{const tx=db.transaction(table,'readwrite'),st=tx.objectStore(table);work(st);tx.oncomplete=resolve;tx.onabort=reject;});db.close();};
  let s=await seed('ordered'),one=await save(s,1),oldForm=(await s.openEdit(C)).reviewed,two=await save(s,2);
  ok(typeof s.prepareEdit==='function','preparation_api');
  ok((await s.prepareEdit(two)).kind==='blocked','successor_waits_exact_parent');
  const p1=await s.prepareEdit(one);ok(p1.kind==='prepared'&&p1.pending.command.expected_revision==='1'&&p1.pending.command.operation_id===one,'first_uses_reviewed_revision');
  ok(p1.serialized===JSON.stringify(p1.pending.command)&&Object.isFrozen(p1.pending.command.answers),'frozen_complete_exact_bytes');
  const peer=await openHistoryStore(scope,options('ordered'));
  ok(JSON.stringify(await peer.prepareEdit(one))===JSON.stringify(p1),'same_command_two_handles');peer.close();
  s.close();s=await openHistoryStore(scope,options('ordered'));ok(JSON.stringify(await s.prepareEdit(one))===JSON.stringify(p1),'same_command_reopen');
  ok((await s.consumeEditReceipt(p1.pending,{kind:'unresolved',outcome:{operation_id:one,command_type:'capture.edit',status:'unresolved'}})).kind==='invalid'&&(await s.prepareEdit(two)).kind==='blocked','unknown_outcome_retains_identity_no_receipt');
  const wrong=structuredClone(receipt(p1,'2'));wrong.receipt.result.capture_id=Q;
  for(const [label,value] of [['foreign',wrong],['extra',{...receipt(p1,'2'),extra:true}],['regressive',receipt(p1,'0')],['skipped_revision',receipt(p1,'3')],['unsupported',{...receipt(p1,'2'),receipt:{...receipt(p1,'2').receipt,command_version:2}}]])ok((await s.consumeEditReceipt(p1.pending,value)).kind==='invalid','reject_'+label);
  const foreignPin={...p1.pending,account_id:Q};ok((await s.consumeEditReceipt(foreignPin,receipt(p1,'2'))).kind==='invalid','reject_foreign_account');
  ok((await s.consumeEditReceipt(p1.pending,receipt(p1,'2'))).kind==='reconciled','late_original_receipt');
  ok((await s.consumeEditReceipt(p1.pending,receipt(p1,'2'))).kind==='reconciled','duplicate_receipt_idempotent');
  ok((await s.consumeEditReceipt(p1.pending,receipt(p1,'3'))).kind==='invalid','contradictory_receipt_rejected');
  ok((await s.openEdit(C)).reviewed.capture.answers[Q].value===2,'late_receipt_keeps_new_overlay');
  const p2=await s.prepareEdit(two);ok(p2.kind==='prepared'&&p2.pending.command.expected_revision==='2','successor_uses_exact_parent_result');
  oldForm=(await s.openEdit(C)).reviewed;
  const ownDetail=detail({revision:'2',...change(1),updated_by:Q,updated_at:'2026-10-26T10:00:00Z'});
  await s.importPage(history({items:[ownDetail]}),historyPending());
  ok((await s.openEdit(C)).reviewed.base.revision==='1'&&(await s.openEdit(C)).reviewed.capture.answers[Q].value===2,'parent_readback_preserves_descendant_base_overlay');
  ok((await s.saveEdit(oldForm,uuid(),change(4))).kind==='needs_attention','stale_form_after_parent_readback_requires_attention');
  const three=await save(s,4);ok((await s.prepareEdit(three)).kind==='blocked','third_waits_exact_second_parent');
  ok((await s.consumeEditReceipt(p2.pending,receipt(p2,'3'))).kind==='reconciled','second_receipt');
  const p3=await s.prepareEdit(three);ok(p3.kind==='prepared'&&p3.pending.command.expected_revision==='3','third_uses_second_receipt');
  await s.importPage(history({items:[detail({revision:'3',...change(2)})]}),historyPending());
  ok((await s.openEdit(C)).reviewed.capture.answers[Q].value===4,'late_second_readback_keeps_third');
  await s.importPage(history({items:[detail({revision:'4',...change(4),updated_by:Q})]}),historyPending());
  ok((await s.read()).records[0].saved_edit.action_id===three,'readback_without_receipt_never_acknowledges');
  await s.consumeEditReceipt(p3.pending,receipt(p3,'4'));
  ok((await s.read()).records[0].saved_edit.action_id===three,'receipt_does_not_reuse_prior_readback');
  await s.importPage(history({items:[detail({revision:'4',...change(4),updated_by:Q})]}),historyPending());
  let row=(await s.read()).records[0];ok(!row.saved_edit&&row.edit_status==='Synced'&&row.baseline.updated_by===Q,'matched_receipt_readback_confirms_server_provenance');
  ok((await actions(s)).find(a=>a.action_id===three).base.revision==='1','immutable_action_base_retained');
  const four=await save(s,5),p4=await s.prepareEdit(four);ok(p4.pending.command.expected_revision==='4','normal_new_save_after_acknowledged_readback');s.close();
  s=await seed('unchanged');const same=await save(s,3),ps=await s.prepareEdit(same);await s.consumeEditReceipt(ps.pending,receipt(ps,'1'));const next=await save(s,1);ok((await s.prepareEdit(next)).pending.command.expected_revision==='1','unchanged_parent_receipt_valid');s.close();
  s=await seed('superseded-readback');const supersededId=await save(s,1),superseded=await s.prepareEdit(supersededId);await s.consumeEditReceipt(superseded.pending,receipt(superseded,'2'));await s.importPage(history({items:[detail({revision:'3',...change(5),updated_by:Q})]}),historyPending());row=(await s.read()).records[0];ok(!row.saved_edit&&row.edit_status==='Synced'&&row.baseline.answers[Q].value===5&&row.baseline.updated_by===Q,'newer_authoritative_readback_retires_only_acknowledged_latest_overlay');ok((await s.openEdit(C)).reviewed.capture.answers[Q].value===5,'readback_never_claims_current_equals_older_snapshot');s.close();
  s=await seed('remote');const rid=await save(s,1),rp=await s.prepareEdit(rid);await s.consumeEditReceipt(rp.pending,receipt(rp,'2'));await save(s,2);await s.importPage(history({items:[detail({revision:'3',...change(5)})]}),historyPending());
  ok((await s.saveEdit((await s.openEdit(C)).reviewed,uuid(),change(2))).kind==='needs_attention','unrelated_remote_revision_never_rebases');s.close();
  s=await seed('conflict');one=await save(s,1);two=await save(s,2);const cp=await s.prepareEdit(one),conflict={kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'2'};
  ok((await s.consumeEditConflict(cp.pending,conflict)).kind==='reconciled','exact_conflict_consumed');ok((await s.consumeEditConflict(cp.pending,conflict)).kind==='reconciled','duplicate_conflict_idempotent');
  ok((await s.consumeEditReceipt(cp.pending,receipt(cp,'2'))).kind==='invalid','receipt_cannot_contradict_conflict');ok((await s.prepareEdit(two)).kind==='blocked','conflict_blocks_descendant');
  await s.importPage(history({items:[detail({revision:'2',...change(5)})]}),historyPending());row=(await s.read()).records[0];const retained=await actions(s);ok(row.saved_edit.action_id===two&&retained.length===2&&retained[0].delivery.serialized===cp.serialized&&retained[0].delivery.conflict.current_revision==='2','conflict_readback_retains_attempt_proposal_base_descendants');s.close();
  s=await seed('known-remote');const unprepared=await save(s,1);await s.importPage(history({items:[detail({revision:'2',...change(5)})]}),historyPending());ok((await s.prepareEdit(unprepared)).kind==='blocked'&&(await s.read()).records[0].edit_status==='Needs attention','known_unrelated_remote_blocks_new_preparation');s.close();
  s=await seed('frozen-remote');const frozenId=await save(s,1),frozenBefore=await s.prepareEdit(frozenId);await s.importPage(history({items:[detail({revision:'2',...change(5)})]}),historyPending());ok(JSON.stringify(await s.prepareEdit(frozenId))===JSON.stringify(frozenBefore),'unrelated_readback_preserves_frozen_unknown_command');s.close();
  s=await seed('unsupported');one=await save(s,1);two=await save(s,2);await mutate('unsupported','edit_actions',st=>{const q=st.get(A+'/'+O+'/'+one);q.onsuccess=()=>st.put({...q.result,version:2});});ok((await s.prepareEdit(one)).kind==='blocked'&&(await s.prepareEdit(two)).kind==='blocked','unsupported_intent_preserved_blocks_descendant');s.close();
  s=await seed('rollback');one=await save(s,1);let before=JSON.stringify(await actions(s));const put=IDBObjectStore.prototype.put;
  IDBObjectStore.prototype.put=function(...args){if(this.name==='edit_actions'){this.transaction.abort();throw new DOMException('quota','QuotaExceededError');}return put.apply(this,args);};
  try{ok((await s.prepareEdit(one)).kind==='unavailable','prepare_quota_no_success');}finally{IDBObjectStore.prototype.put=put;}
  ok(JSON.stringify(await actions(s))===before,'prepare_quota_rollback');const rollbackPrepared=await s.prepareEdit(one);before=JSON.stringify(await actions(s));
  IDBObjectStore.prototype.put=function(...args){if(this.name==='edit_actions'){this.transaction.abort();throw Error('receipt failure');}return put.apply(this,args);};
  try{ok((await s.consumeEditReceipt(rollbackPrepared.pending,receipt(rollbackPrepared,'2'))).kind==='unavailable','receipt_storage_failure_no_success');}finally{IDBObjectStore.prototype.put=put;}
  ok(JSON.stringify(await actions(s))===before,'receipt_atomic_rollback');
  const aborted=new AbortController();aborted.abort();ok((await s.prepareEdit(one,{signal:aborted.signal})).kind==='unavailable','abort_preparation');ok((await s.consumeEditReceipt(rollbackPrepared.pending,receipt(rollbackPrepared,'2'),{isCurrent:()=>false})).kind==='unavailable','account_change_outcome_fence');
  await s.denyEdit();ok((await s.prepareEdit(one)).kind==='denied','edit_denial_blocks_repreparation');ok((await s.consumeEditReceipt(rollbackPrepared.pending,receipt(rollbackPrepared,'2'))).kind==='reconciled','edit_denial_preserves_receipt_consumption');
  await s.importPage(history({items:[detail({revision:'2',...change(1)})]}),historyPending());ok(!(await s.read()).records[0].saved_edit&&(await s.openEdit(C)).kind==='denied','readback_does_not_renew_edit_authority');s.close();
  s=await seed('completion');one=await save(s,1);const transact=IDBDatabase.prototype.transaction;let current=true;
  IDBDatabase.prototype.transaction=function(...args){const tx=transact.apply(this,args);tx.addEventListener('complete',()=>{current=false;},{once:true});return tx;};
  try{ok((await s.prepareEdit(one,{isCurrent:()=>current})).kind==='unavailable','completion_session_no_stale_prepared_success');}finally{IDBDatabase.prototype.transaction=transact;}
  ok((await s.prepareEdit(one)).pending.command.operation_id===one,'late_completion_retains_original_identity');
  const preparedBeforeExpiry=await s.prepareEdit(one);now=Date.parse('2026-11-02T10:00:00Z');tick+=now-Date.parse('2026-10-26T10:00:01Z');ok((await s.prepareEdit(one)).kind==='expired'&&(await s.consumeEditReceipt(preparedBeforeExpiry.pending,receipt(preparedBeforeExpiry,'2'))).kind==='expired','independent_read_edit_expiry');s.close();
  now=Date.parse('2026-10-27T10:00:01Z');tick=1;s=await openHistoryStore(scope,options('edit-only-expiry'));
  const independent=context(),freshRead={...observation(),checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};independent.read_observation=freshRead;await s.importEditContext(independent,pin);one=await save(s,1);const independentPrepared=await s.prepareEdit(one);
  tick+=Date.parse('2026-11-02T10:00:00Z')-now;now=Date.parse('2026-11-02T10:00:00Z');ok((await s.prepareEdit(one)).kind==='expired','edit_only_expiry_blocks_preparation');ok((await s.consumeEditReceipt(independentPrepared.pending,receipt(independentPrepared,'2'))).kind==='reconciled','fresh_read_consumes_after_edit_expiry');s.close();
  return checks;
 });checks.push(...observed);
 // Both realms request the first freeze before any delivery metadata exists.
 await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q,detail,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const s=window.raceStore=await openHistoryStore({account_id:A,org_id:O},{database:'competing-first-freeze',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});await s.importEditContext({capture:detail(),editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'}},{account_id:A,org_id:O,capture_id:C});
  for(const [action,value] of [['55555555-5555-4555-8555-000000000001',1],['55555555-5555-4555-8555-000000000002',2]])await s.saveEdit((await s.openEdit(C)).reviewed,action,{observation_date:'2026-10-25',answers:{[Q]:{value}}});
 });
 const raceOther=await browserContext.newPage();await raceOther.goto(origin);await raceOther.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');window.raceStore=await openHistoryStore({account_id:A,org_id:O},{database:'competing-first-freeze',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});
 });
 const competing=await Promise.all([page,raceOther].map(realm=>realm.evaluate(async()=>window.racePrepared=await window.raceStore.prepareEdit('55555555-5555-4555-8555-000000000001'))));
 assert.equal(competing[0].kind,'prepared');assert.deepEqual(competing[0],competing[1]);checks.push('competing_first_preparations_one_identical_committed_freeze');
 const interleaved=await Promise.all([
  page.evaluate(async()=>{const {C}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');return window.raceStore.consumeEditReceipt(window.racePrepared.pending,{kind:'committed',receipt:{operation_id:window.racePrepared.pending.command.operation_id,command_type:'capture.edit',status:'committed',command_version:1,result:{capture_id:C,revision:'2'}}});}),
  raceOther.evaluate(async()=>window.raceStore.consumeEditConflict(window.racePrepared.pending,{kind:'error',status:409,error_id:'kdg_capture.capture_revision_conflict',current_revision:'2'})),
  page.evaluate(async()=>{const {Q,detail,page,pending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');return window.raceStore.importPage(page({items:[detail({revision:'2',observation_date:'2026-10-25',answers:{[Q]:{value:1}}})]}),pending());})
 ]);
 assert.deepEqual(interleaved.slice(0,2).map(x=>x.kind).sort(),['invalid','reconciled']);assert.equal(interleaved[2].kind,'committed');checks.push('receipt_conflict_import_interleaving_one_noncontradictory_outcome');
 const raced=await page.evaluate(async()=>{const {C}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const a=(await window.raceStore.readEditActions()).actions,row=(await window.raceStore.read()).records[0];return {a,row};});
 assert.equal(raced.a[0].delivery.serialized,competing[0].serialized);assert.equal(raced.a[0].base.revision,'1');assert.equal(raced.a[1].base.revision,'1');assert.equal(raced.row.saved_edit.action_id,'55555555-5555-4555-8555-000000000002');assert.equal(Boolean(raced.a[0].delivery.receipt)!==Boolean(raced.a[0].delivery.conflict),true);checks.push('interleaved_outcome_and_readback_preserve_newer_overlay_ids_bases_and_frozen_command');
 await page.evaluate(()=>window.raceStore.close());await raceOther.evaluate(()=>window.raceStore.close());await raceOther.close();
 // A separate page executes another realm's preparation; reload removes all old handles.
 await page.evaluate(async()=>{const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');window.chain=await openHistoryStore({account_id:A,org_id:O},{database:'ordered',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});window.frozen=(await window.chain.readEditActions()).actions.find(a=>a.delivery?.pending.command.expected_revision==='4');});
 const other=await browserContext.newPage();await other.goto(origin);const cross=await other.evaluate(async()=>{const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'ordered',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});const action=(await s.readEditActions()).actions.find(a=>a.delivery?.pending.command.expected_revision==='4');const p=await s.prepareEdit(action.action_id);s.close();return JSON.stringify(p);});
 assert.equal(cross,await page.evaluate(async()=>JSON.stringify(await window.chain.prepareEdit(window.frozen.action_id))));checks.push('cross_tab_identical_frozen_preparation');await page.evaluate(()=>window.chain.close());await page.reload();
 assert.equal(cross,await page.evaluate(async()=>{const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'ordered',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});const a=(await s.readEditActions()).actions.find(a=>a.delivery?.pending.command.expected_revision==='4');const p=await s.prepareEdit(a.action_id);s.close();return JSON.stringify(p);}));checks.push('reload_identical_frozen_preparation');await other.close();passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}finally{
 if(browser)await browser.close();if(server){const done=new Promise(r=>server.close(r));for(const s of sockets)s.destroy();await done;}
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,checks,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limits:['synthetic Chromium IndexedDB only','no physical persistence, eviction or at-rest claim','restart checks persist wall watermark; monotonic anchor exists only within process']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));if(!record.passed)process.exitCode=1;
}
