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
const proof=join(root,'platform/deployment/.local/kdg-offline-history-20261026/store-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/tests/history-store.types.ts','web/src/history-download.ts','web/offline-tools/idb.ts','web/src/history-store.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','web/tests/history-fixture.mjs','web/tests/read-fixture.mjs','web/tests/history-store-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[...['history-store','history-download'].map(x=>join(capsule,owner,'web/src/'+x+'.ts')),join(capsule,owner,'web/tests/history-store.types.ts')]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const out=await page.evaluate(async()=>{
  const {openHistoryStore,HISTORY_DATABASE,phoneHistoryDates}=await import('/compiled/web/src/history-store.js');
  const {page,pending,detail,A,O,C,Q,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const checks=[],ok=(value,name)=>{if(!value)throw Error(name);checks.push(name);};
  let wall=Date.parse('2026-10-26T10:00:01Z'),tick=100;
  const scope={account_id:A,org_id:O},options={wall:()=>wall,monotonic:()=>tick};
  let store=await openHistoryStore(scope,options);
  ok((await store.importPage(page(),pending())).kind==='committed','initial_import');
  let view=await store.read();ok(view.kind==='available'&&view.records.length===1&&view.downloads[0].status==='complete','complete_baseline_original_definition');
  await store.close();store=await openHistoryStore(scope,options);ok((await store.read()).kind==='available','same_account_reopen');
  // Seed an existing local overlay through raw IDB, never a new queue producer.
  const raw=await new Promise((resolve,reject)=>{const r=indexedDB.open(HISTORY_DATABASE,1);r.onsuccess=()=>resolve(r.result);r.onerror=reject;});
  const local={pending:{operation_id:Q,local_id:C,answers:{[Q]:{value:1}},base_revision:'1',base:detail(),definition_version_id:Q},conflict:{server:detail(),local_id:Q},status:'Pending'};
  await new Promise((resolve,reject)=>{const tx=raw.transaction('records','readwrite'),s=tx.objectStore('records'),r=s.get(A+'/'+O+'/'+C);r.onsuccess=()=>s.put({...r.result,...local});tx.oncomplete=resolve;tx.onabort=reject;});
  ok((await store.importPage(page({items:[detail({revision:'2',answers:{[Q]:{value:4}}})]}),pending())).kind==='committed','newer_revision_import');
  view=await store.read();const record=view.records[0];ok(record.baseline.revision==='2'&&JSON.stringify(Object.fromEntries(Object.keys(local).map(k=>[k,record[k]])))===JSON.stringify(local),'pending_base_ids_conflict_verbatim');
  await store.importPage(page(),pending());ok((await store.read()).records[0].baseline.revision==='2','older_revision_no_regression');
  const before=JSON.stringify(await store.read());
  ok((await store.importPage(page({items:[detail({child_id:A})]}),pending())).kind==='unavailable','immutable_collision_refuses');
  ok((await store.importPage(page({items:[detail({definition:{...detail().definition,questions:[{...detail().definition.questions[0],label:'Changed'}]}})]}),pending())).kind==='unavailable','definition_collision_refuses');
  ok((await store.importPage(page({items:[detail({capture_id:Q}),detail({child_id:A})]}),pending())).kind==='unavailable','later_collision_aborts_earlier_row');
  ok(JSON.stringify(await store.read())===before,'collision_whole_page_unchanged');
  let phase=0;ok((await store.importPage(page({items:[detail({revision:'3'})]}),pending(),{isCurrent:()=>++phase<6})).kind==='unavailable'&&JSON.stringify(await store.read())===before,'session_changes_during_transaction_abort');
  const original=IDBObjectStore.prototype.put;let puts=0;
  IDBObjectStore.prototype.put=function(...args){if(++puts===2){this.transaction.abort();throw new DOMException('Synthetic quota','QuotaExceededError');}return original.apply(this,args);};
  const aborted=await store.importPage(page({items:[detail({revision:'3'})]}),pending());IDBObjectStore.prototype.put=original;
  ok(aborted.kind==='unavailable'&&JSON.stringify(await store.read())===before,'actual_transaction_abort_atomic');
  const partial=page({next_cursor:btoa(JSON.stringify(Object.fromEntries(Object.entries({v:1,org_id:O,account_id:A,permission:'kdg_capture.capture.read.own',from_date:'2026-10-01',to_date:'2026-10-26',limit:2,last_created_at:detail().created_at,last_id:C}).sort(([a],[b])=>a<b?-1:a>b?1:0)))).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'')});
  const partitionKey=A+'/'+O;
  await new Promise((resolve,reject)=>{const tx=raw.transaction('downloads','readwrite');tx.objectStore('downloads').clear();tx.oncomplete=resolve;tx.onabort=reject;});
  ok((await store.importPage(partial,pending())).kind==='committed'&&(await store.read()).downloads[0].status==='partial','partial_progress');
  ok((await store.importPage(page({items:[]}),pending({cursor:partial.next_cursor}))).kind==='committed'&&(await store.read()).downloads[0].status==='complete'&&(await store.read()).records.length===1,'empty_final_complete_no_deletion');
  const emptyScope=pending({from_date:'2026-09-01',to_date:'2026-09-02'});
  ok((await store.importPage(page({...emptyScope,items:[]}),emptyScope)).kind==='committed','empty_scope_complete_distinct');
  const controller=new AbortController();controller.abort();ok((await store.importPage(page(),pending(),{signal:controller.signal})).kind==='unavailable','aborted_execution_refused');
  ok((await store.importPage(page(),pending(),{isCurrent:()=>false})).kind==='unavailable','stale_session_refused');
  ok((await store.importPage(page({observation:{...observation(),expires_at:'2026-11-03T10:00:00Z'}}),pending())).kind==='unavailable','no_stronger_observation');
  const foreign=await openHistoryStore({account_id:Q,org_id:O},options);ok((await foreign.read()).kind==='unavailable'&&(await foreign.importPage(page(),pending())).kind==='unavailable','foreign_namespace_refused');
  const ordinary=await openHistoryStore(scope,options);await ordinary.close();ok((await store.read()).kind==='available','ordinary_close_preserves_other_handle');
  const concurrent=await openHistoryStore(scope,options);
  await Promise.all([store.importPage(page({items:[detail({revision:'4'})]}),pending()),concurrent.importPage(page({items:[detail({revision:'5'})]}),pending())]);
  ok((await store.read()).records[0].baseline.revision==='5','concurrent_imports_newer_wins');
  await concurrent.deny();ok((await store.read()).kind==='unavailable'&&(await concurrent.read()).kind==='unavailable','known_denial_all_handles_locked');
  let recovery=await openHistoryStore(scope,options);ok((await recovery.importPage(page(),pending())).kind==='unavailable','denial_requires_explicit_recovery');
  wall+=1000;tick+=1000;const current={...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'};
  ok((await recovery.importPage(page({observation:current}),pending(),{restoreDenied:true})).kind==='committed','current_verified_explicit_recovery');
  ok((await recovery.read()).kind==='available','restored_view');
  for(const mode of ['rollback','monotonic','expiry']){
   let w=Date.parse('2026-10-26T10:00:03Z'),m=1;
   const clockStore=await openHistoryStore(scope,{database:'clock-'+mode,wall:()=>w,monotonic:()=>m});
   await clockStore.importPage(page({observation:current}),pending());
   if(mode==='rollback')w-=1;
   if(mode==='monotonic')m+=120000;
   if(mode==='expiry'){w=Date.parse(current.expires_at);m+=604799000;}
   ok((await clockStore.read()).kind==='unavailable',mode+'_fails_closed');
   await clockStore.close();
  }
  await recovery.close();raw.close();
  ok(phoneHistoryDates(new Date(2026,2,1,12)).from_date==='2026-01-31','phone_calendar_previous29');
  const {downloadOwnHistory}=await import('/compiled/web/src/history-download.js');
  const downloaded=await openHistoryStore(scope,{...options,database:'download-proof'});
  const transport={signal:new AbortController().signal,isCurrent:()=>true,request:async()=>new Response(JSON.stringify(page({observation:current})),{headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}})};
  ok((await downloadOwnHistory(downloaded,{account_id:A,access_token:'synthetic'},pending(),transport)).kind==='complete','connected_download_commits');
  const outage=await downloadOwnHistory(downloaded,{account_id:A,access_token:'synthetic'},pending(),{...transport,request:async()=>{throw Error('synthetic');}});
  ok(outage.kind==='verification_unavailable'&&(await downloaded.read()).kind==='available','outage_retains_cached_access');
  await downloaded.logout();const afterLogout=await openHistoryStore(scope,{...options,database:'download-proof'});
  ok((await afterLogout.read()).kind==='unavailable'&&(await afterLogout.importPage(page({observation:current}),pending())).kind==='unavailable','logout_persists_lock_no_late_unlock');
  await afterLogout.close();
  const restart=await openHistoryStore(scope,{...options,database:'restart-proof'});await restart.importPage(page({observation:current}),pending());await restart.close();
  return checks;
 });checks.push(...out);
 await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,page,pending}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  window.staleStore=await openHistoryStore({account_id:A,org_id:O},{database:'multi-page',wall:()=>Date.parse('2026-10-26T10:00:01Z')});await window.staleStore.importPage(page(),pending());
 });
 const other=await page.context().newPage();await other.goto(origin);
 await other.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const lock=await openHistoryStore({account_id:A,org_id:O},{database:'multi-page',wall:()=>Date.parse('2026-10-26T10:00:01Z')});await lock.deny();
 });
 checks.push(...await page.evaluate(async()=>{
  const {page,pending,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const future={...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'};
  if((await window.staleStore.importPage(page({observation:future}),pending(),{restoreDenied:true})).kind!=='unavailable')throw Error('cross_realm_late_unlock');
  if((await window.staleStore.read()).kind!=='unavailable')throw Error('cross_realm_read');return ['cross_js_realm_durable_epoch_refuses_late_restore','cross_js_realm_denial_view_locked'];
 }));
 checks.push(...await other.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,page,pending,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const fresh=await openHistoryStore({account_id:A,org_id:O},{database:'multi-page',wall:()=>Date.parse('2026-10-26T10:00:02Z')});
  if((await fresh.importPage(page({observation:{...observation(),checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'}}),pending(),{restoreDenied:true})).kind!=='committed')throw Error('fresh_explicit_restore');
  await fresh.close();return ['cross_js_realm_explicit_fresh_restore','logout_durable_epoch'];
 }));await other.close();
 await page.reload();
 const restart=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  let now=Date.parse('2026-10-26T10:00:02Z');const store=await openHistoryStore({account_id:A,org_id:O},{database:'restart-proof',wall:()=>now});
  if((await store.read()).kind!=='available')throw Error('restart_reopen');now-=1;if((await store.read()).kind!=='unavailable')throw Error('restart_rollback');await store.close();return ['new_js_context_reopen','persisted_wall_watermark_restart_rollback'];
 });checks.push(...restart);
 const review=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {downloadOwnHistory}=await import('/compiled/web/src/history-download.js');
  const {validateHistoryPage}=await import('/compiled/web/src/history.js');
  const {A,O,C,Q,page,pending,detail,observation,cursor,response}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  const failures=[],checks=[],expect=(v,n)=>{if(!v)throw Error(n);},test=async(name,fn)=>{try{await fn();checks.push(name);}catch(e){failures.push(name+': '+e.message);}};
  let serial=0;
  const fresh=async(name)=>{let wall=Date.parse('2026-10-26T10:00:01Z'),mono=1;const database='review-'+name+'-'+serial++,options={database,wall:()=>wall,monotonic:()=>mono};const store=await openHistoryStore({account_id:A,org_id:O},options);await store.importPage(page(),pending());return{store,options,setWall:v=>wall=v,setMono:v=>mono=v,open:()=>openHistoryStore({account_id:A,org_id:O},options)};};
  const rawOpen=database=>new Promise((resolve,reject)=>{const r=indexedDB.open(database);r.onsuccess=()=>resolve(r.result);r.onerror=reject;});
  const newer=()=>({...observation(),decision_id:A,checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'});
  for(const mode of ['predicate','signal'])await test('oncomplete_'+mode+'_fence',async()=>{
   const f=await fresh(mode),original=IDBDatabase.prototype.transaction;let arm=true,current=true;const abort=new AbortController();
   IDBDatabase.prototype.transaction=function(...args){const tx=original.apply(this,args);tx.addEventListener('complete',()=>{if(arm){arm=false;current=false;if(mode==='signal')abort.abort();}},{once:true});return tx;};
   let outcome;try{outcome=await f.store.importPage(page({items:[detail({revision:'2'})]}),pending(),{signal:abort.signal,isCurrent:()=>current});}finally{IDBDatabase.prototype.transaction=original;}
   expect(outcome.kind==='unavailable','published committed after completion fence');await f.store.close();
  });
  await test('active_signal_aborts_transaction',async()=>{const f=await fresh('active-signal'),put=IDBObjectStore.prototype.put,abort=new AbortController();let armed=true;IDBObjectStore.prototype.put=function(...args){const result=put.apply(this,args);if(armed&&this.name==='records'){armed=false;abort.abort();}return result;};let outcome;try{outcome=await f.store.importPage(page({items:[detail({revision:'2'})]}),pending(),{signal:abort.signal});}finally{IDBObjectStore.prototype.put=put;}expect(outcome.kind==='unavailable'&&(await f.store.read()).records[0].baseline.revision==='1','active signal did not roll back transaction');await f.store.close();});
  await test('clock_lock_durable_and_explicit_recovery',async()=>{
   const f=await fresh('clock');f.setWall(Date.parse('2026-10-26T10:00:00Z'));expect((await f.store.read()).kind==='unavailable','rollback accepted');
   f.setWall(Date.parse('2026-10-26T10:00:01Z'));await f.store.close();const reopen=await f.open();expect((await reopen.read()).kind==='unavailable','clock correction unlocked cached view');
   const db=await rawOpen(f.options.database),tx=db.transaction('partitions'),done=new Promise((resolve,reject)=>{tx.oncomplete=resolve;tx.onabort=reject;});const meta=await new Promise(resolve=>{const r=tx.objectStore('partitions').get(A+'/'+O);r.onsuccess=()=>resolve(r.result);});await done;db.close();expect(meta.clockLocked===true,'clock lock not persisted');
   f.setWall(Date.parse('2026-10-26T10:00:02Z'));f.setMono(1001);expect((await reopen.importPage(page({observation:newer()}),pending(),{restoreDenied:true})).kind==='committed','fresh verified recovery failed');expect((await reopen.read()).kind==='available','fresh anchors not restored');await reopen.close();
  });
  await test('closed_handle_denial_inert',async()=>{const f=await fresh('stale');await f.store.close();const active=await f.open();await f.store.deny({account_id:A,org_id:O});expect((await active.read()).kind==='available','closed handle invalidated active session');await active.close();});
  await test('wrong_scope_denial_inert',async()=>{const f=await fresh('wrong');await f.store.deny({account_id:Q,org_id:O});expect((await f.store.read()).kind==='available','wrong-scope denial locked cache');await f.store.close();});
  await test('failed_lock_latch_survives_reopen',async()=>{const f=await fresh('lock-failure'),put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(...args){if(this.name==='partitions'){this.transaction.abort();throw Error('synthetic failed lock');}return put.apply(this,args);};let lock;try{lock=await f.store.logout();}finally{IDBObjectStore.prototype.put=put;}expect(lock.kind==='unavailable','failed lock claimed success');const reopened=await f.open();expect((await reopened.read()).kind==='unavailable','failed known lock reopened old cache');f.setWall(Date.parse('2026-10-26T10:00:02Z'));f.setMono(1001);expect((await reopened.importPage(page({observation:newer()}),pending(),{restoreDenied:true})).kind==='committed'&&(await reopened.read()).kind==='available','failed-lock latch could not recover online');await reopened.close();});
  for(const fields of [{answers:{[Q]:{value:4}}},{observation_date:'2026-10-25'},{updated_by:Q},{updated_at:'2026-10-26T10:00:01Z'},{captured_at:'2026-10-26T09:00:00Z'}])await test('revision_collision_'+Object.keys(fields)[0],async()=>{const f=await fresh('revision');expect((await f.store.importPage(page({items:[detail(fields)]}),pending())).kind==='unavailable','contradictory equal revision accepted');await f.store.close();});
  await test('pending_create_only_enriched_without_acknowledgement',async()=>{const f=await fresh('pending-create'),db=await rawOpen(f.options.database),local={pending:{operation_id:Q,local_id:C,command_type:'capture.create',base_revision:null,version_id:Q,base_definition:detail().definition,answers:{[Q]:{value:1}}},status:'Pending',uncertain:true,conflict:{local_id:C}};await new Promise((resolve,reject)=>{const tx=db.transaction('records','readwrite');tx.objectStore('records').put({key:A+'/'+O+'/'+C,partition:A+'/'+O,...local});tx.oncomplete=resolve;tx.onabort=reject;});db.close();expect((await f.store.importPage(page(),pending())).kind==='committed','pending-only import rejected');const record=(await f.store.read()).records[0];expect(record.baseline.capture_id===C&&JSON.stringify(Object.fromEntries(Object.keys(local).map(k=>[k,record[k]])))===JSON.stringify(local),'pending create changed or acknowledged');await f.store.close();});
  await test('bounded_local_pages_125_rows',async()=>{const f=await fresh('bounded'),db=await rawOpen(f.options.database);await new Promise((resolve,reject)=>{const tx=db.transaction(['records','downloads'],'readwrite');tx.objectStore('records').clear();tx.objectStore('downloads').clear();for(let i=0;i<125;i++){const key=A+'/'+O+'/'+String(i).padStart(4,'0');tx.objectStore('records').put({key,partition:A+'/'+O,baseline:detail()});tx.objectStore('downloads').put({key,partition:A+'/'+O,status:'complete'});}tx.oncomplete=resolve;tx.onabort=reject;});db.close();const first=await f.store.read();expect(first.records.length===30&&first.downloads.length===30,'default read unbounded');let after,progressAfter,total=0,progress=0;do{const read=await f.store.read({limit:100,after,progressAfter});expect(read.kind==='available'&&read.records.length<=100&&read.downloads.length<=100,'max read unbounded');total+=read.records.length;progress+=read.downloads.length;after=read.next_key;progressAfter=read.progress_next_key;}while(after||progressAfter);expect(total===125&&progress===125,'local continuation lost or duplicated rows');await f.store.close();});
  await test('initialization_abort_closes_handle',async()=>{const original=IDBDatabase.prototype.transaction,close=IDBDatabase.prototype.close;let closed=0;IDBDatabase.prototype.close=function(){closed++;return close.call(this);};IDBDatabase.prototype.transaction=function(...args){const tx=original.apply(this,args);if(args[1]==='readonly')queueMicrotask(()=>tx.abort());return tx;};try{try{await openHistoryStore({account_id:A,org_id:O},{database:'review-initial-abort'});}catch{}await new Promise(r=>setTimeout(r,0));expect(closed>0,'initial abort leaked open handle');}finally{IDBDatabase.prototype.transaction=original;IDBDatabase.prototype.close=close;}});
  await test('direct_null_limit_refused',async()=>{for(const change of [{limit:null},{limit:undefined},{cursor:undefined},{cursor:null},{cursor:''},{unexpected:'value'}]){let refused=false;try{validateHistoryPage(page({limit:Object.hasOwn(change,'limit')?30:2}),pending(change));}catch{refused=true;}expect(refused,'direct validator normalized '+JSON.stringify(change));}});
  await test('coordinator_two_pages_partial_resume_and_denial',async()=>{
   const f=await fresh('coordinator'),first=page({next_cursor:btoa(JSON.stringify(Object.fromEntries(Object.entries({v:1,org_id:O,account_id:A,permission:'kdg_capture.capture.read.own',from_date:'2026-10-01',to_date:'2026-10-26',limit:2,last_created_at:detail().created_at,last_id:C}).sort(([a],[b])=>a<b?-1:a>b?1:0)))).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'')}),second=page({items:[detail({capture_id:A,created_at:'2026-10-26T09:59:59Z'})]});let requests=[],fail=true;
   const opts={signal:new AbortController().signal,isCurrent:()=>true,request:async url=>{requests.push(url);if(url.includes('cursor=')){if(fail)throw Error('outage');return response(second);}return response(first);}};
   const session={account_id:A,access_token:'synthetic'};expect((await downloadOwnHistory(f.store,session,pending(),opts)).kind==='verification_unavailable','later failure hidden');let view=await f.store.read();expect(view.downloads[0].status==='partial','failed later page falsely complete');fail=false;expect((await downloadOwnHistory(f.store,session,pending({cursor:first.next_cursor}),opts)).kind==='complete','explicit resume failed');expect(requests.length===3&&requests.every(url=>url.includes('from_date=2026-10-01')&&url.includes('to_date=2026-10-26'))&&requests[2].includes('cursor='+encodeURIComponent(first.next_cursor)),'fixed bounds/returned cursor changed');
   view=await f.store.read();expect(view.downloads[0].status==='complete'&&view.records.length===2&&view.records.some(row=>row.baseline.capture_id===A)&&view.records.some(row=>row.baseline.capture_id===C),'second page records/progress not persisted');
   expect((await downloadOwnHistory(f.store,session,pending(),{...opts,request:async()=>response({error:'safe',error_id:'access_denied'},403)})).kind==='error','403 lost');expect((await f.store.read()).kind==='unavailable'&&(await(await f.open()).read()).kind==='unavailable','403 did not lock current/reopened partition');
  });
  await test('coordinator_wrong_scope_denial_inert',async()=>{const f=await fresh('coordinator-wrong'),outcome=await downloadOwnHistory(f.store,{account_id:A,access_token:'synthetic'},pending({org_id:Q}),{signal:new AbortController().signal,isCurrent:()=>true,request:async()=>response({error:'safe',error_id:'access_denied'},403)});expect(outcome.kind==='unavailable'&&(await f.store.read()).kind==='available','coordinator locked wrong partition');await f.store.close();});
  await test('coordinator_stale_denial_inert',async()=>{const f=await fresh('coordinator-stale');let current=true;const outcome=await downloadOwnHistory(f.store,{account_id:A,access_token:'synthetic'},pending(),{signal:new AbortController().signal,isCurrent:()=>current,request:async()=>{current=false;return response({error:'safe',error_id:'access_denied'},403);}});expect(outcome.kind==='superseded'&&(await f.store.read()).kind==='available','stale coordinator denied active partition');await f.store.close();});
  await test('coordinator_predicate_throw_safe',async()=>{const f=await fresh('throw');let calls=0;const opts={signal:new AbortController().signal,isCurrent:()=>{if(++calls>=7)throw Error('caller');return true;},request:async()=>response()};let outcome;try{outcome=await downloadOwnHistory(f.store,{account_id:A,access_token:'synthetic'},pending(),opts);}catch{throw Error('callback escaped');}expect(outcome.kind!=='complete','stale callback published complete');await f.store.close();});
  await test('child_label_separate_mutability',async()=>{const f=await fresh('label');expect((await f.store.importPage(page({items:[detail({child_label:'Updated child label'})]}),pending())).kind==='committed','child label cannot refresh');expect((await f.store.read()).records[0].baseline.child_label==='Updated child label','child label refresh lost');await f.store.close();});
  const reloadClock=await fresh('clock-reload');reloadClock.setWall(Date.parse('2026-10-26T10:00:00Z'));await reloadClock.store.read();await reloadClock.store.close();
  return {checks,failures,clockDatabase:reloadClock.options.database};
 });checks.push(...review.checks);writeFileSync(join(proof,'review-cases.json'),JSON.stringify(review,null,2)+'\n');assert.deepEqual(review.failures,[]);
 await page.reload();
 checks.push(...await page.evaluate(async database=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,page,pending,observation}=await import('/apps/kdg-capture/web/tests/history-fixture.mjs');
  let now=Date.parse('2026-10-26T10:00:01Z');const store=await openHistoryStore({account_id:A,org_id:O},{database,wall:()=>now});
  if((await store.read()).kind!=='unavailable')throw Error('persisted_clock_lock_lost_on_reload');now+=1000;
  const newer={...observation(),decision_id:A,checked_at:'2026-10-26T10:00:02Z',expires_at:'2026-11-02T10:00:02Z'};
  if((await store.importPage(page({observation:newer}),pending(),{restoreDenied:true})).kind!=='committed'||(await store.read()).kind!=='available')throw Error('clock_lock_online_recovery_after_reload');store.close();return ['persisted_clock_lock_after_js_reload','explicit_online_clock_recovery_after_js_reload'];
 },review.clockDatabase));
 passed=true;
}finally{
 if(browser)await browser.close();if(server){const done=new Promise(r=>server.close(r));for(const s of sockets)s.destroy();await done;}
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,checks,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limits:['synthetic Chromium IndexedDB only','no physical persistence, eviction or at-rest claim','restart checks persist wall watermark; monotonic anchor exists only within process']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));
}
