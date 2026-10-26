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
const proof=join(root,'platform/deployment/.local/kdg-local-edit-save-20261026/save-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/src/edit-context.ts','contracts/edit-context-generated/types.gen.ts','web/src/own-observation.ts','web/tests/local-edit-save.types.ts','web/tests/history-store.types.ts','web/src/history-download.ts','web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','web/tests/history-fixture.mjs','web/tests/read-fixture.mjs','web/tests/local-edit-save-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[...['history-store','history-download'].map(x=>join(capsule,owner,'web/src/'+x+'.ts')),...['local-edit-save','history-store'].map(x=>join(capsule,owner,'web/tests/'+x+'.types.ts'))]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const refinements=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,detail,observation,page,pending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const scope={account_id:A,org_id:O},failures=[],checks=[];
  const ok=(v,n)=>{(v?checks:failures).push(n);};let serial=1000;
  const uuid=()=>`66666666-6666-4666-8666-${String(++serial).padStart(12,'0')}`;
  const change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}});
  const ctx=(capture=detail(),obs=observation())=>({capture,editable_fields:['observation_date','answers'],read_observation:obs,edit_observation:{...obs,permission:'kdg_capture.capture.edit.own'}});
  for(const mode of ['characters','size','read_expiry','edit_expiry','late_expiry','denial','read_restore','blockers','mutation','actions']){
   let now=Date.parse('2026-10-26T10:00:01Z'),tick=1;const database='refinement-'+mode,options={database,wall:()=>now,monotonic:()=>tick};let s=await openHistoryStore(scope,options);
   const context=ctx();
   if(mode==='characters')context.capture=detail({definition:{schema_version:1,questions:[{id:Q,type:'text',label:'Text',required:true}]},answers:{[Q]:{value:'old'}}});
   if(mode==='size'){const questions=Array.from({length:10},(_,i)=>({id:`99999999-9999-4999-8999-${String(i+1).padStart(12,'0')}`,type:'text',label:'Text',required:true}));context.capture=detail({definition:{schema_version:1,questions},answers:Object.fromEntries(questions.map(q=>[q.id,{value:'old'}]))});}
   const imported=s.importEditContext(context,{...scope,capture_id:C});if(mode==='mutation')context.capture.answers[Q].value=5;await imported;const r=(await s.openEdit(C)).reviewed;
   if(mode==='characters')for(const value of ['bad\u0000','bad\ud800'])ok((await s.saveEdit(r,uuid(),change(value))).kind==='invalid','invalid_wire_character_'+value.charCodeAt(3));
   if(mode==='size'){const answers=Object.fromEntries(r.base.definition.questions.map(q=>[q.id,{value:'😀'.repeat(5000)}]));ok((await s.saveEdit(r,uuid(),{observation_date:'2026-10-25',answers})).kind==='invalid','oversize_supported_put_refused');
    const bounded=Object.fromEntries(r.base.definition.questions.map(q=>[q.id,{value:'x'}])),action=uuid();
    const bytes=()=>new TextEncoder().encode(JSON.stringify({operation_id:action,command_version:1,expected_revision:'9223372036854775807',observation_date:'2026-10-25',answers:bounded})).byteLength;
    let remaining=131072-bytes();for(const answer of Object.values(bounded)){const emojis=Math.min(4999,Math.floor(remaining/4));answer.value+='😀'.repeat(emojis);remaining-=emojis*4;}
    Object.values(bounded).at(-1).value+='a'.repeat(remaining);
    ok(bytes()===131072&&(await s.saveEdit(r,action,{observation_date:'2026-10-25',answers:bounded})).kind==='saved_locally','max_revision_wire_limit_exactly_supported');
    Object.values(bounded).at(-1).value+='a';ok((await s.saveEdit(r,uuid(),{observation_date:'2026-10-25',answers:bounded})).kind==='invalid','max_revision_wire_limit_plus_one_refused');}
   if(mode==='mutation'){ok(r.capture.answers[Q].value===3,'import_copies_before_await');const input=change(1),saving=s.saveEdit(r,uuid(),input);input.answers[Q].value=5;ok((await saving).kind==='saved_locally'&&(await s.openEdit(C)).reviewed.capture.answers[Q].value===1,'save_copies_before_await');}
   if(mode==='read_expiry'||mode==='edit_expiry'||mode==='late_expiry'){
    const fresh=ctx();fresh.read_observation={...observation(),checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};fresh.edit_observation={...fresh.read_observation,permission:'kdg_capture.capture.edit.own'};
    now=Date.parse('2026-10-27T10:00:01Z');tick+=86400000;await s.importEditContext(fresh,{...scope,capture_id:C});
    // For independent token checks use original read and fresh edit, or vice versa.
    let reviewed=r;
    if(mode!=='late_expiry'){
     const early=ctx();early.read_observation=mode==='read_expiry'?observation():fresh.read_observation;early.edit_observation=mode==='edit_expiry'?{...observation(),permission:'kdg_capture.capture.edit.own'}:fresh.edit_observation;
     s.close();s=await openHistoryStore(scope,{...options,database:database+'-token'});await s.importEditContext(early,{...scope,capture_id:C});reviewed=(await s.openEdit(C)).reviewed;await s.importEditContext(fresh,{...scope,capture_id:C});
    }
    if(mode==='late_expiry'){
     const get=IDBObjectStore.prototype.get;IDBObjectStore.prototype.get=function(...args){const req=get.apply(this,args);if(this.name==='edit_actions')req.addEventListener('success',()=>{const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;});return req;};
     try{ok((await s.saveEdit(reviewed,uuid(),change(1))).kind==='expired','authority_rechecked_after_action_lookup');}finally{IDBObjectStore.prototype.get=get;}
    }else{const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;ok((await s.saveEdit(reviewed,uuid(),change(1))).kind==='expired',mode+'_old_review_independently_expires');}
    ok((await s.read()).kind==='available',mode+'_preserves_fresh_history');
   }
   if(mode==='denial'){
    ok(typeof s.denyEdit==='function','independent_edit_denial_api');if(s.denyEdit){await s.denyEdit();ok((await s.openEdit(C)).kind==='denied'&&(await s.read()).kind==='available','edit_denial_preserves_read');s.close();s=await openHistoryStore(scope,options);ok((await s.openEdit(C)).kind==='denied','edit_denial_durable');now+=1000;tick+=1000;const newer=ctx(undefined,{...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'});ok((await s.importEditContext(newer,{...scope,capture_id:C},{restoreDenied:true})).kind==='committed'&&(await s.openEdit(C)).kind==='opened','explicit_new_context_restores_edit');ok((await s.saveEdit(r,uuid(),change(1))).kind==='denied','old_review_stays_denied_after_restoration');}
   }
   if(mode==='read_restore'){await s.deny();s.close();s=await openHistoryStore(scope,options);now+=1000;tick+=1000;await s.importPage(page({observation:{...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'}}),pending(),{restoreDenied:true});ok((await s.read()).kind==='available'&&(await s.openEdit(C)).kind==='denied','read_restoration_cannot_restore_edit_context');}
   if(mode==='actions'){const id=uuid();await s.saveEdit(r,id,change(1));await s.saveEdit(r,uuid(),change(2));s.close();s=await openHistoryStore(scope,options);ok(typeof s.readEditActions==='function','retained_actions_read_api');if(s.readEditActions){const a=await s.readEditActions({limit:1});const b=await s.readEditActions({limit:1,after:a.next_key});ok(a.kind==='available'&&a.actions.length===1&&b.actions.length===1&&b.actions[0].status==='Needs attention'&&Object.isFrozen(b.actions[0].changes),'bounded_actions_survive_reopen');ok((await s.readEditActions({limit:101})).kind==='unavailable'&&(await s.readEditActions({after:'foreign'})).kind==='unavailable','action_bounds_scope');}}
   if(mode==='blockers')for(const field of ['pending','conflict']){const db=await new Promise(resolve=>{const req=indexedDB.open(database);req.onsuccess=()=>resolve(req.result);});await new Promise(resolve=>{const tx=db.transaction('records','readwrite'),store=tx.objectStore('records'),req=store.get(A+'/'+O+'/'+C);req.onsuccess=()=>store.put({...req.result,pending:undefined,conflict:undefined,[field]:{opaque:true}});tx.oncomplete=resolve;});db.close();ok((await s.saveEdit(r,uuid(),change(1))).kind==='needs_attention',field+'_alone_blocks_overlay');}
   s.close();
  }return {checks,failures};
 });writeFileSync(join(proof,'refinements.json'),JSON.stringify(refinements,null,2));checks.push(...refinements.checks);assert.deepEqual(refinements.failures,[],'refinement_failures');
 const out=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,detail,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
  let wall=Date.parse('2026-10-26T10:00:01Z'),mono=1,serial=0;
  const scope={account_id:A,org_id:O},options={database:'edit-proof',wall:()=>wall,monotonic:()=>mono};
  const context=(capture=detail(),edit={})=>({capture,editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own',...edit}});
  const change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}}),uuid=()=>`66666666-6666-4666-8666-${String(++serial).padStart(12,'0')}`;
  let s=await openHistoryStore(scope,options);
  ok(typeof s.importEditContext==='function','missing_import_edit_context');
  const c=context();ok((await s.importEditContext(c,{...scope,capture_id:C})).kind==='committed','verified_context_commits');
  ok(!Object.isFrozen(c)&&!Object.isFrozen(c.capture),'import_never_freezes_caller');
  let opened=await s.openEdit(C),r=opened.reviewed;
  ok(opened.kind==='opened'&&Object.isFrozen(r.capture.answers[Q]),'offline_immutable_reviewed_original');
  ok(JSON.stringify(r.read_observation)===JSON.stringify(c.read_observation)&&JSON.stringify(r.edit_observation)===JSON.stringify(c.edit_observation),'exact_independent_evidence');
  const id1=uuid(),input=change(1);const saved=await s.saveEdit(r,id1,input);
  ok(saved.kind==='saved_locally','valid_one_saved_only_locally');
  ok(!Object.isFrozen(input)&&input.answers[Q].value===1,'save_never_mutates_caller');
  ok((await s.saveEdit(r,id1,input)).kind==='saved_locally','same_id_identical_replay');
  ok((await s.saveEdit(r,id1,change(2))).kind==='action_id_reused','same_id_changed_snapshot_refuses');
  const inspect=async(database=options.database)=>{const db=await new Promise((resolve,reject)=>{const req=indexedDB.open(database);req.onsuccess=()=>resolve(req.result);req.onerror=reject;});try{return await new Promise((resolve,reject)=>{const tx=db.transaction(['records','edit_actions']),records=tx.objectStore('records').getAll(),actions=tx.objectStore('edit_actions').getAll();tx.oncomplete=()=>resolve({records:records.result,actions:actions.result});tx.onabort=reject;});}finally{db.close();}};
  let state=await inspect();ok(state.actions.length===1&&state.records[0].baseline.answers[Q].value===3&&state.records[0].baseline.updated_at===c.capture.updated_at,'atomic_action_overlay_baseline_attribution_preserved');
  s.close();s=await openHistoryStore(scope,options);opened=await s.openEdit(C);
  ok(opened.reviewed.capture.answers[Q].value===1,'saved_overlay_survives_reopen');
  ok((await s.saveEdit(r,id1,input)).kind==='saved_locally','identical_replay_survives_handle_reopen');
  const r2=opened.reviewed,id2=uuid();ok((await s.saveEdit(r2,id2,change(2))).kind==='saved_locally','sequential_explicit_save');
  state=await inspect();ok(state.actions.length===2&&state.actions[1].predecessor_action_id===id1&&state.actions[1].expected_revision===null&&state.actions[0].expected_revision==='1','serial_predecessor_no_guessed_revision');
  const staleId=uuid();ok((await s.saveEdit(r2,staleId,change(4))).kind==='needs_attention','stale_form_preserved_attention');
  state=await inspect();ok(state.actions.length===3&&state.records[0].saved_edit.action_id===id2&&state.actions.find(a=>a.action_id===staleId).changes.answers[Q].value===4,'stale_completed_proposal_distinct_no_overwrite');
  const before=JSON.stringify(await inspect());const invalid=(await s.openEdit(C)).reviewed;
  ok((await s.saveEdit(invalid,uuid(),change(0))).kind==='invalid','original_rating_rules');
  ok((await s.saveEdit(invalid,uuid(),{observation_date:'2026-10-25',answers:{}})).kind==='invalid','original_required_rules');
  ok(JSON.stringify(await inspect())===before,'invalid_cancel_typing_no_action_or_overlay');
  const put=IDBObjectStore.prototype.add;IDBObjectStore.prototype.add=function(...args){this.transaction.abort();throw new DOMException('synthetic quota','QuotaExceededError');};
  try{ok((await s.saveEdit(invalid,uuid(),change(5))).kind==='unavailable','quota_abort_never_saved');}finally{IDBObjectStore.prototype.add=put;}
  ok(JSON.stringify(await inspect())===before,'quota_atomic_rollback_no_partial');
  const oldPut=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(...args){if(this.name==='records'){this.transaction.abort();throw Error('synthetic overlay failure');}return oldPut.apply(this,args);};
  try{ok((await s.saveEdit(invalid,uuid(),change(5))).kind==='unavailable','overlay_failure_after_intent_never_saved');}finally{IDBObjectStore.prototype.put=oldPut;}
  ok(JSON.stringify(await inspect())===before,'overlay_failure_rolls_back_already_queued_intent');
  const originalTransaction=IDBDatabase.prototype.transaction;let current=true,armed=true;
  IDBDatabase.prototype.transaction=function(...args){const tx=originalTransaction.apply(this,args);tx.addEventListener('complete',()=>{if(armed){armed=false;current=false;}});return tx;};
  try{ok((await s.saveEdit(invalid,uuid(),change(2),{isCurrent:()=>current})).kind==='unavailable','completion_session_fence_never_publishes_saved');}finally{IDBDatabase.prototype.transaction=originalTransaction;}
  // The completion fence may retain committed original-account work; re-open pins it.

  const newRemote=context(detail({revision:'2',answers:{[Q]:{value:5}}}));ok((await s.importEditContext(newRemote,{...scope,capture_id:C})).kind==='committed','new_remote_refresh');
  const refreshed=(await s.openEdit(C)).reviewed;ok(refreshed.base.revision==='1'&&refreshed.capture.answers[Q].value===2,'refresh_pins_reviewed_base_and_local_overlay');
  ok((await s.saveEdit(refreshed,uuid(),change(1))).kind==='needs_attention','unrelated_remote_baseline_never_rebases');
  state=await inspect();ok(state.actions[0].base.revision==='1'&&state.actions[0].changes.answers[Q].value===1,'old_intent_never_mutated');
  const cancelled=new AbortController();cancelled.abort();const snap=JSON.stringify(state);
  ok((await s.saveEdit(refreshed,uuid(),change(1),{signal:cancelled.signal})).kind==='unavailable'&&JSON.stringify(await inspect())===snap,'aborted_save_no_publication_or_write');
  ok((await s.saveEdit(refreshed,uuid(),change(1),{isCurrent:()=>false})).kind==='unavailable','account_replacement_fences_save');
  const wrong=await openHistoryStore({account_id:Q,org_id:O},{...options});ok((await wrong.openEdit(C)).kind==='unavailable','account_isolation');wrong.close();
  await s.logout();s=await openHistoryStore(scope,options);ok((await s.openEdit(C)).kind==='denied','logout_durable_lock');
  ok((await s.saveEdit(refreshed,uuid(),change(1))).kind==='denied','denial_prevents_save_retains_work');s.close();
  for(const mode of ['read','edit','clock','history']){
   let now=wall,tick=1;const database='independent-'+mode,opts={database,wall:()=>now,monotonic:()=>tick};const store=await openHistoryStore(scope,opts);
   let ctx=context();if(mode==='read')ctx.read_observation={...ctx.read_observation,checked_at:'2026-10-25T10:00:00Z',expires_at:'2026-11-01T10:00:00Z'};
   if(mode==='edit'||mode==='history')ctx.edit_observation={...ctx.edit_observation,checked_at:'2026-10-25T10:00:00Z',expires_at:'2026-11-01T10:00:00Z'};
   await store.importEditContext(ctx,{...scope,capture_id:C});const review=(await store.openEdit(C)).reviewed;
   if(mode==='clock'){now-=1;}else{now=Date.parse('2026-11-01T10:00:00Z');tick+=now-wall;}
   if(mode==='history'){const {page,pending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const obs={...observation(),checked_at:'2026-11-01T10:00:00Z',expires_at:'2026-11-08T10:00:00Z'};ok((await store.importPage(page({observation:obs}),pending())).kind==='committed','history_read_refresh_succeeds');}
   ok((await store.saveEdit(review,uuid(),change(1))).kind===(mode==='clock'?'unavailable':'expired'),mode+'_independent_expiry_or_clock_blocks_save');if(mode==='edit'||mode==='history')ok((await store.read()).kind==='available',mode+'_edit_expiry_preserves_read_authority');store.close();
  }
  const boolean=detail({definition:{schema_version:1,questions:[{id:Q,type:'boolean',label:'Boolean',required:true,default:false,details_enabled:true,details_label:'Details'}]},answers:{[Q]:{value:true,details:'old'}}});
  const bs=await openHistoryStore(scope,{...options,database:'boolean'});await bs.importEditContext(context(boolean),{...scope,capture_id:C});const br=(await bs.openEdit(C)).reviewed,bi={observation_date:'2026-10-25',answers:{[Q]:{value:false,details:'hidden'}}};
  ok((await bs.saveEdit(br,uuid(),bi)).kind==='saved_locally','required_false_valid');ok(!Object.hasOwn((await bs.openEdit(C)).reviewed.capture.answers[Q],'details')&&bi.answers[Q].details==='hidden','hidden_details_excluded_input_preserved');ok(!(await inspect('boolean')).actions[0].content.includes('hidden'),'hidden_details_absent_from_durable_identity');bs.close();
  const fresh=await openHistoryStore(scope,{...options,database:'fresh-history'});await fresh.importEditContext(context(),{...scope,capture_id:C});const oldReview=(await fresh.openEdit(C)).reviewed;
  const {page:hp,pending:hb}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');await fresh.importPage(hp({items:[detail({revision:'2',answers:{[Q]:{value:4}}})]}),hb());const freshReview=(await fresh.openEdit(C)).reviewed;
  ok(freshReview.base.revision==='2'&&freshReview.capture.answers[Q].value===4&&oldReview.base.revision==='1','new_form_reviews_latest_history_old_review_pinned');
  ok((await fresh.saveEdit(freshReview,uuid(),change(1))).kind==='saved_locally','newly_reviewed_remote_base_can_save');fresh.close();
  const legacy='legacy-v1';const db=await new Promise((resolve,reject)=>{const q=indexedDB.open(legacy,1);q.onupgradeneeded=()=>{for(const n of ['records','definitions','partitions','downloads'])q.result.createObjectStore(n,{keyPath:'key'});};q.onsuccess=()=>resolve(q.result);q.onerror=reject;});
  await new Promise((resolve,reject)=>{const tx=db.transaction(['records','partitions'],'readwrite');tx.objectStore('records').put({key:A+'/'+O+'/'+C,partition:A+'/'+O,baseline:detail(),pending:{opaque:true}});tx.objectStore('partitions').put({key:A+'/'+O,epoch:0,observation:observation(),wall});tx.oncomplete=resolve;tx.onabort=reject;});db.close();
  const upgraded=await openHistoryStore(scope,{...options,database:legacy});ok((await upgraded.read()).records[0].pending.opaque===true,'v1_upgrade_history_pending_preserved');upgraded.close();
  return checks;
 });checks.push(...out);
 const other=await browserContext.newPage();await other.goto(origin);
 await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,detail,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  window.editStore=await openHistoryStore({account_id:A,org_id:O},{database:'two-tabs',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});
  await window.editStore.importEditContext({capture:detail(),editable_fields:['observation_date','answers'],read_observation:observation(),edit_observation:{...observation(),permission:'kdg_capture.capture.edit.own'}},{account_id:A,org_id:O,capture_id:C});window.review=(await window.editStore.openEdit(C)).reviewed;
 });
 await other.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'two-tabs',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});const r=(await s.openEdit(C)).reviewed;
  if((await s.saveEdit(r,'77777777-7777-4777-8777-777777777777',{observation_date:'2026-10-25',answers:{[Q]:{value:1}}})).kind!=='saved_locally')throw Error('tab_one_save');s.close();
 });
 checks.push(...await page.evaluate(async()=>{
  const {Q}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const result=await window.editStore.saveEdit(window.review,'88888888-8888-4888-8888-888888888888',{observation_date:'2026-10-25',answers:{[Q]:{value:5}}});if(result.kind!=='needs_attention'||(await window.editStore.openEdit(window.review.capture_id)).reviewed.capture.answers[Q].value!==1)throw Error('cross_tab_overwrite');window.editStore.close();return ['cross_js_realm_stale_save_retained_without_overwrite'];
 }));
 const repairs={checks:[],failures:[]};
 const extra=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,detail,observation,page,pending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const checks=[],failures=[],ok=(v,n)=>(v?checks:failures).push(n),scope={account_id:A,org_id:O};let serial=2000;
  const uuid=()=>`66666666-6666-4666-8666-${String(++serial).padStart(12,'0')}`,change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}});
  const context=(capture=detail(),read=observation(),edit={...read,permission:'kdg_capture.capture.edit.own'})=>({capture,editable_fields:['observation_date','answers'],read_observation:read,edit_observation:edit});
  let now=Date.parse('2026-10-26T10:00:01Z'),tick=1;const opts=database=>({database,wall:()=>now,monotonic:()=>tick});
  const history=await openHistoryStore(scope,opts('history-only'));await history.importPage(page(),pending());
  ok((await history.openEdit(C)).kind==='unavailable','history_without_edit_evidence_is_unavailable');history.close();
  const failed=await openHistoryStore(scope,opts('failed-denial'));await failed.importEditContext(context(),{...scope,capture_id:C});const old=(await failed.openEdit(C)).reviewed;
  const put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(...args){if(this.name==='partitions'){this.transaction.abort();throw Error('synthetic denial write failure');}return put.apply(this,args);};
  try{ok((await failed.denyEdit()).kind==='unavailable','failed_denial_reports_storage_failure');}finally{IDBObjectStore.prototype.put=put;}
  ok((await failed.openEdit(C)).kind==='denied'&&(await failed.read()).kind==='available','failed_denial_existing_handle_locked_reads_preserved');
  const reopened=await openHistoryStore(scope,opts('failed-denial'));ok((await reopened.openEdit(C)).kind==='denied'&&(await reopened.read()).kind==='available','failed_denial_reopened_process_handle_locked_reads_preserved');
  now+=1000;tick+=1000;const newer={...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'};
  ok((await reopened.importEditContext(context(undefined,newer),{...scope,capture_id:C},{restoreDenied:true})).kind==='committed','failed_denial_fresh_context_repairs_generation');
  const recovered=await failed.openEdit(C);ok(recovered.kind==='opened','failed_denial_existing_handle_recovers');
  ok((await failed.saveEdit(old,uuid(),change(1))).kind==='denied','failed_denial_old_review_stays_invalid_after_repair');
  if(recovered.kind==='opened')ok((await failed.saveEdit(recovered.reviewed,uuid(),change(1))).kind==='saved_locally','failed_denial_new_review_can_save');failed.close();reopened.close();
  // Force reviewed edit expiry at the transaction completion event, after both writes.
  now=Date.parse('2026-10-27T10:00:01Z');tick=1;const completion=await openHistoryStore(scope,opts('completion-expiry'));
  const freshRead={...observation(),checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};
  await completion.importEditContext(context(undefined,freshRead,{...observation(),permission:'kdg_capture.capture.edit.own'}),{...scope,capture_id:C});const review=(await completion.openEdit(C)).reviewed,id=uuid();
  const transaction=IDBDatabase.prototype.transaction;IDBDatabase.prototype.transaction=function(...args){const tx=transaction.apply(this,args);tx.addEventListener('complete',()=>{const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;},{once:true});return tx;};
  try{ok((await completion.saveEdit(review,id,change(2))).kind==='expired','completion_expiry_never_publishes_save_success');}finally{IDBDatabase.prototype.transaction=transaction;}
  const retained=await completion.readEditActions(),savedHistory=await completion.read();
  ok(retained.kind==='available'&&retained.actions.length===1&&retained.actions[0].action_id===id&&savedHistory.kind==='available'&&savedHistory.records[0].saved_edit.action_id===id,'completion_expiry_retains_original_id_intent_and_overlay_for_own_read');completion.close();
  // Populate three partitions in one database, with independently verified synthetic evidence.
  now=Date.parse('2026-10-26T10:00:01Z');tick=1;const partitions=[];
  for(const [account,org] of [[A,O],[Q,O],[A,Q]]){
   const scoped={account_id:account,org_id:org},s=await openHistoryStore(scoped,opts('action-isolation'));
   const obs={...observation(),account_id:account,actor_id:account,authorization_scope:{kind:'organization',org_id:org},resource_scope:{kind:'own_account',account_id:account}};
   const capture=detail({org_id:org,owner_account_id:account,owner_actor_id:account,created_by:account,updated_by:account});await s.importEditContext(context(capture,obs),{...scoped,capture_id:C});const r=(await s.openEdit(C)).reviewed,id=uuid();await s.saveEdit(r,id,change(1));partitions.push({s,id});
  }
  for(const [i,{s,id}] of partitions.entries()){const actions=await s.readEditActions();ok(actions.kind==='available'&&actions.actions.length===1&&actions.actions[0].action_id===id,'actions_isolated_account_org_partition_'+i);}
  await partitions[0].s.denyEdit();ok((await partitions[0].s.readEditActions()).kind==='available','retained_actions_available_after_edit_only_denial');
  await partitions[1].s.deny();partitions[1].s.close();const denied=await openHistoryStore({account_id:Q,org_id:O},opts('action-isolation'));ok((await denied.readEditActions()).kind==='denied','retained_actions_refused_after_own_read_denial');denied.close();
  const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;ok((await partitions[2].s.readEditActions()).kind==='expired','retained_actions_refused_after_own_read_expiry');for(const {s} of partitions)s.close();
  // Keep an already-open handle and original token in this realm while another tab denies.
  let crossNow=Date.parse('2026-10-26T10:00:01Z'),crossTick=1;
  window.crossStore=await openHistoryStore(scope,{database:'generation-cross-realm',wall:()=>crossNow,monotonic:()=>crossTick});
  window.crossAdvance=()=>{crossNow+=1000;crossTick+=1000;};
  await window.crossStore.importEditContext(context(),{...scope,capture_id:C});window.crossReview=(await window.crossStore.openEdit(C)).reviewed;
  return {checks,failures};
 });repairs.checks.push(...extra.checks);repairs.failures.push(...extra.failures);
 await other.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const s=await openHistoryStore({account_id:A,org_id:O},{database:'generation-cross-realm',wall:()=>Date.parse('2026-10-26T10:00:01Z'),monotonic:()=>1});await s.denyEdit();s.close();
 });
 const cross=await page.evaluate(async()=>{
  const {A,O,C,Q,detail,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const checks=[],failures=[],ok=(v,n)=>(v?checks:failures).push(n),s=window.crossStore;
  window.crossAdvance();const obs={...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'};
  const imported=await s.importEditContext({capture:detail(),editable_fields:['observation_date','answers'],read_observation:obs,edit_observation:{...obs,permission:'kdg_capture.capture.edit.own'}},{account_id:A,org_id:O,capture_id:C},{restoreDenied:true});
  ok(imported.kind==='committed','cross_realm_denial_restoration_commits_on_already_open_handle');
  const opened=await s.openEdit(C);ok(opened.kind==='opened','cross_realm_generation_synchronized_for_existing_handle');
  const change=value=>({observation_date:'2026-10-25',answers:{[Q]:{value}}});
  ok((await s.saveEdit(window.crossReview,'77777777-7777-4777-8777-000000000001',change(1))).kind==='denied','cross_realm_restoration_old_token_refused');
  if(opened.kind==='opened'){await s.saveEdit(opened.reviewed,'77777777-7777-4777-8777-000000000002',change(2));await s.saveEdit(opened.reviewed,'77777777-7777-4777-8777-000000000003',change(4));}s.close();return {checks,failures};
 });repairs.checks.push(...cross.checks);repairs.failures.push(...cross.failures);
 await page.reload();
 const reloaded=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');const checks=[],failures=[],ok=(v,n)=>(v?checks:failures).push(n);
  const s=await openHistoryStore({account_id:A,org_id:O},{database:'generation-cross-realm',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1});const opened=await s.openEdit(C),actions=await s.readEditActions();
  ok(!window.crossReview&&opened.kind==='opened'&&opened.reviewed.capture.answers[Q].value===2,'fresh_js_realm_recovers_saved_overlay_without_old_tokens');
  ok(actions.kind==='available'&&actions.actions.length===2&&actions.actions[1].status==='Needs attention'&&actions.actions[1].changes.answers[Q].value===4,'fresh_js_realm_recovers_retained_proposal');s.close();return {checks,failures};
 });repairs.checks.push(...reloaded.checks);repairs.failures.push(...reloaded.failures);
 writeFileSync(join(proof,'repairs.json'),JSON.stringify(repairs,null,2));checks.push(...repairs.checks);assert.deepEqual(repairs.failures,[],'review_repair_failures');
 await other.close();passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}finally{
 if(browser)await browser.close();if(server){const done=new Promise(r=>server.close(r));for(const s of sockets)s.destroy();await done;}
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,checks,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limits:['synthetic Chromium IndexedDB only','no physical persistence, eviction or at-rest claim','restart checks persist wall watermark; monotonic anchor exists only within process']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));
}
