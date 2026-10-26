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
const proof=join(root,'platform/deployment/.local/kdg-local-create-save-20261026/save-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/tests/local-create-save.types.ts','web/src/history-store.ts','web/src/create.ts','contracts/create-generated/types.gen.ts','web/src/own-observation.ts','web/src/provision.ts','web/src/edit-context.ts','web/src/history.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','web/offline-tools/idb.ts','contracts/edit-context-generated/types.gen.ts','contracts/history-generated/types.gen.ts','contracts/read-generated/types.gen.ts','contracts/generated/types.gen.ts','contracts/provision-generated/types.gen.ts','web/tests/read-fixture.mjs','web/tests/provision-fixture.mjs','web/tests/local-create-save-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({compilerOptions:{strict:true,target:'ES2022',module:'ESNext',moduleResolution:'Bundler',skipLibCheck:true,lib:['ES2022','DOM','DOM.Iterable'],rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[join(capsule,owner,'web/src/history-store.ts'),join(capsule,owner,'web/tests/local-create-save.types.ts')]}));
let passed=false,browser,server;const checks=[],sockets=new Set();
try{
 const compiled=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),compiled.stdout+compiled.stderr);assert.equal(compiled.status,0,'strict_types_failed');
 server=createServer((req,res)=>{let path=new URL(req.url,'http://local').pathname;res.setHeader('Content-Type',path.endsWith('.js')||path.endsWith('.mjs')?'text/javascript':'text/html');if(path==='/')res.end('<!doctype html><title>Isolated IDB proof</title>');else try{res.end(readFileSync(join(capsule,path)));}catch{res.writeHead(404).end();}});server.on('connection',s=>{sockets.add(s);s.once('close',()=>sockets.delete(s));});server.listen(0,'127.0.0.1');await once(server,'listening');
 const require=createRequire(join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/package.json'));const {chromium}=require('@playwright/test');
 browser=await chromium.launch({executablePath:join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'),headless:true});
 const browserContext=await browser.newContext();const page=await browserContext.newPage();const origin='http://127.0.0.1:'+server.address().port;await page.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());await page.goto(origin);
 const out=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');
  const {A,O,C,Q,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
  const {validateDetail}=await import('/compiled/web/src/read-validation.js');const {detail}=await import('/apps/kdg-capture/web/tests/read-fixture.mjs');
  ok(validateDetail(detail(),{account_id:A,org_id:O,capture_id:C}).answers[Q].value===3,'characterize_original_rating');
  for(const answers of [{},{[Q]:{value:0}},{[Q]:{value:false}}]){let bad=false;try{validateDetail(detail({answers}),{account_id:A,org_id:O,capture_id:C});}catch{bad=true;}ok(bad,'characterize_invalid_original_answers');}
  const scope={account_id:A,org_id:O},opts={database:'create-save',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1};let s=await openHistoryStore(scope,opts);
  ok(typeof s.beginSetupRefresh==='function','setup_refresh_api');
  const t=await s.beginSetupRefresh();ok(t.kind==='started','refresh_started');
  ok((await s.importProvision(provision(),t.ticket)).kind==='committed','setup_imported');ok((await s.importProvision(provision(),t.ticket)).kind==='denied','published_setup_ticket_consumed');
  const opened=await s.openCreate(C);ok(opened.kind==='opened','original_create_opened');
  const ids={capture_id:'88888888-8888-4888-8888-888888888888',operation_id:'99999999-9999-4999-8999-999999999999'},input={observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value:1}}};
  ok((await s.saveCreate(opened.reviewed,ids,input)).kind==='saved_locally','atomic_create_saved');s.close();s=await openHistoryStore(scope,opts);
  const actions=await s.readCreateActions();ok(actions.kind==='available'&&actions.actions.length===1,'reopened_one_create_action');
  ok(actions.actions[0].pending.command.operation_id===ids.operation_id&&actions.actions[0].pending.command.answers[Q].value===1,'original_generated_create_command');
  const history=await s.read();ok(history.records.length===1&&!history.records[0].baseline&&history.records[0].local_capture.answers[Q].value===1,'local_content_without_server_provenance');
  const pendingEdit=await s.openEdit(ids.capture_id);ok(pendingEdit.kind==='opened'&&pendingEdit.reviewed.version===2&&pendingEdit.reviewed.base_kind==='local_create'&&!Object.hasOwn(pendingEdit.reviewed.base,'revision')&&!Object.hasOwn(pendingEdit.reviewed.base,'created_at')&&!Object.hasOwn(pendingEdit.reviewed.base,'created_by')&&!history.records[0].baseline,'pending_create_local_edit_without_server_facts');
  ok((await s.saveCreate(opened.reviewed,ids,input)).kind==='saved_locally'&&(await s.readCreateActions()).actions.length===1,'same_attempt_retry_after_reopen');
  ok((await s.saveCreate(opened.reviewed,ids,{...input,answers:{[Q]:{value:2}}})).kind==='action_id_reused','changed_retry_refused');s.close();return checks;
 });checks.push(...out);
 const edges=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};let serial=1,now=Date.parse('2026-10-26T10:00:02Z'),tick=1;
  const ids=()=>({capture_id:`66666666-6666-4666-8666-${String(++serial).padStart(12,'0')}`,operation_id:`77777777-7777-4777-8777-${String(serial).padStart(12,'0')}`}),input=value=>({observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value}}}),scope={account_id:A,org_id:O};
  const open=name=>openHistoryStore(scope,{database:'edge-'+name,wall:()=>now,monotonic:()=>tick});
  const setup=async(s,p=provision())=>{const t=await s.beginSetupRefresh();return s.importProvision(p,t.ticket);};
  const inspect=async(name)=>{const d=await new Promise(resolve=>{const q=indexedDB.open('edge-'+name);q.onsuccess=()=>resolve(q.result);});const out=await new Promise(resolve=>{const tx=d.transaction(['records','create_actions','definitions'],'readonly'),r=tx.objectStore('records').getAll(),a=tx.objectStore('create_actions').getAll(),v=tx.objectStore('definitions').getAll();tx.oncomplete=()=>resolve({records:r.result,actions:a.result,definitions:v.result});});d.close();return out;};
  for(const mode of ['ordering','pinned','invalid','boolean','atomic','expiry','loss','clock','denial_failure','multiplicity','bounds','mutation','identity','readonly','collision','completion']){
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;let s=await open(mode),p=provision();
   if(mode==='boolean')p.questionnaire.definition={schema_version:1,questions:[{id:Q,type:'boolean',label:'Boolean',required:true,default:false,details_enabled:true,details_label:'Details'}]};
   if(mode==='readonly')p.edit_observation=null;
   ok((await setup(s,p)).kind==='committed',mode+'_setup');const r=(await s.openCreate(C)).reviewed;
   if(mode==='ordering'){
    const first=await s.beginSetupRefresh(),second=await s.beginSetupRefresh(),denied={...provision(),create_assigned_observation:null,children:[],create_state:'not_permitted'};
    ok((await s.importProvision(denied,second.ticket)).kind==='committed','newer_denial_imported');ok((await s.importProvision(provision(),first.ticket)).kind==='denied','late_older_setup_cannot_restore_denial');ok((await s.saveCreate(r,ids(),input(1))).kind==='denied','known_create_denial_blocks_old_form');ok((await s.read()).kind==='available','create_denial_preserves_read');
   }
   if(mode==='pinned'){
    const refreshed=provision();refreshed.questionnaire={...refreshed.questionnaire,questionnaire_version_id:A,questionnaire_version:'2'};refreshed.children[0].child_eligibility_ref='b'.repeat(43);await setup(s,refreshed);
    ok((await s.saveCreate(r,ids(),input(1))).kind==='saved_locally','opened_questionnaire_survives_refresh');const a=(await s.readCreateActions()).actions[0];ok(a.pending.command.questionnaire_version_id===Q&&a.pending.command.child_eligibility_ref==='a'.repeat(43),'original_definition_and_reference_pinned');
   }
   if(mode==='invalid')for(const bad of [input(0),input(true),{...input(1),answers:{}},{...input(1),answers:{[A]:{value:1}}},{...input(1),observation_date:'2026-02-30'},{...input(1),captured_at:'invalid'}])ok((await s.saveCreate(r,ids(),bad)).kind==='invalid','invalid_complete_form_refused');
   if(mode==='boolean'){const change=input(false);change.answers[Q].details='hidden';ok((await s.saveCreate(r,ids(),change)).kind==='saved_locally','required_false_saved');const a=(await s.readCreateActions()).actions[0];ok(!Object.hasOwn(a.pending.command.answers[Q],'details')&&!a.content.includes('hidden')&&change.answers[Q].details==='hidden','hidden_details_removed_before_identity_without_mutating_caller');}
   if(mode==='atomic'){
    const before=JSON.stringify(await inspect(mode)),add=IDBObjectStore.prototype.add;IDBObjectStore.prototype.add=function(...a){if(this.name==='records'){this.transaction.abort();throw new DOMException('synthetic quota','QuotaExceededError');}return add.apply(this,a);};
    try{ok((await s.saveCreate(r,ids(),input(1))).kind==='unavailable','failed_record_after_action_never_acknowledges');}finally{IDBObjectStore.prototype.add=add;}ok(JSON.stringify(await inspect(mode))===before,'record_action_atomic_rollback');
    const abort=new AbortController();abort.abort();ok((await s.saveCreate(r,ids(),input(1),{signal:abort.signal})).kind==='unavailable','already_aborted_save_refused');ok((await s.saveCreate(r,ids(),input(1),{isCurrent:()=>false})).kind==='unavailable','account_replacement_save_refused');
   }
   if(mode==='expiry'){
    now=Date.parse('2026-11-02T10:00:00Z');tick+=now-Date.parse('2026-10-26T10:00:02Z');ok((await s.saveCreate(r,ids(),input(1))).kind==='expired','earliest_original_read_create_expiry_blocks_save');
   }
   if(mode==='loss'){const changed=provision();changed.children[0].assignment.assignment_revision='2';await setup(s,changed);ok((await s.saveCreate(r,ids(),input(1))).kind==='denied','current_assignment_revision_loss_blocks_old_form');}
   if(mode==='clock'){now--;ok((await s.saveCreate(r,ids(),input(1))).kind==='unavailable','clock_rollback_blocks_save');}
   if(mode==='denial_failure'){
    const t=await s.beginSetupRefresh(),put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(...a){if(this.name==='partitions'){this.transaction.abort();throw Error('synthetic failure');}return put.apply(this,a);};
    try{const denied={...provision(),create_assigned_observation:null,children:[],create_state:'not_permitted'};ok((await s.importProvision(denied,t.ticket)).kind==='unavailable','denial_write_failure_reported');}finally{IDBObjectStore.prototype.put=put;}
    s.close();s=await open(mode);ok((await s.saveCreate(r,ids(),input(1))).kind==='denied','failed_denial_process_latch_survives_handle_reopen');
   }
   if(mode==='multiplicity'){ok((await s.saveCreate(r,ids(),input(1))).kind==='saved_locally'&&(await s.saveCreate(r,ids(),input(1))).kind==='saved_locally'&&(await s.read()).records.length===2,'same_child_date_distinct_records_allowed');}
   if(mode==='bounds'){for(let i=0;i<3;i++)await s.saveCreate(r,ids(),input(1));const a=await s.readCreateActions({limit:1}),b=await s.readCreateActions({limit:1,after:a.next_key});ok(a.actions.length===1&&b.actions.length===1&&a.actions[0].action_id!==b.actions[0].action_id,'bounded_partition_action_pagination');ok((await s.readCreateActions({limit:101})).kind==='unavailable'&&(await s.readCreateActions({after:'foreign'})).kind==='unavailable','invalid_action_bounds_refused');}
   if(mode==='mutation'){const change=input(1),saving=s.saveCreate(r,ids(),change);change.answers[Q].value=5;ok((await saving).kind==='saved_locally'&&(await s.readCreateActions()).actions[0].pending.command.answers[Q].value===1,'save_snapshots_input_before_await');}
   if(mode==='identity'){const id=ids();await s.saveCreate(r,id,input(1));const r2=(await s.openCreate(C)).reviewed;ok((await s.saveCreate(r2,{...ids(),capture_id:id.capture_id},input(1))).kind==='capture_id_reused','capture_identity_collision_refused');ok((await s.saveCreate(r2,{capture_id:id.operation_id,operation_id:id.capture_id},input(1))).kind==='action_id_reused','cross_capture_action_identity_collision_refused');}
   if(mode==='readonly')ok((await s.saveCreate(r,ids(),input(1))).kind==='saved_locally','initial_create_does_not_require_edit');
   if(mode==='collision'){const changed=provision();changed.questionnaire.definition.questions[0].label='Changed';ok((await setup(s,changed)).kind==='unavailable','immutable_definition_collision_rolls_back');ok((await s.saveCreate(r,ids(),input(1))).kind==='saved_locally','old_setup_preserved_after_collision');}
   if(mode==='completion'){const tx=IDBDatabase.prototype.transaction;let current=true;IDBDatabase.prototype.transaction=function(...a){const t=tx.apply(this,a);t.addEventListener('complete',()=>{current=false;},{once:true});return t;};const id=ids();try{ok((await s.saveCreate(r,id,input(1),{isCurrent:()=>current})).kind==='unavailable','completion_fence_never_false_saved');}finally{IDBDatabase.prototype.transaction=tx;}ok((await s.saveCreate(r,id,input(1))).kind==='saved_locally'&&(await s.readCreateActions()).actions.length===1,'unconfirmed_commit_recovers_original_identity');}
   s.close();
  }
  return checks;
 });checks.push(...edges);
 const extra=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);};let now=Date.parse('2026-10-26T10:00:02Z'),tick=1,n=0;
  const scope={account_id:A,org_id:O},opts=database=>({database,wall:()=>now,monotonic:()=>tick}),ids=()=>({capture_id:`88888888-8888-4888-8888-${String(++n).padStart(12,'0')}`,operation_id:`99999999-9999-4999-8999-${String(n).padStart(12,'0')}`});
  const setup=async(s,p)=>{const t=await s.beginSetupRefresh();return s.importProvision(p,t.ticket);};
  for(const mode of ['unicode','size','read','create','child','oldtoken']){
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts('extra-'+mode)),p=provision();
   if(mode==='unicode'||mode==='size')p.questionnaire.definition={schema_version:1,questions:Array.from({length:mode==='size'?10:1},(_,i)=>({id:`55555555-5555-4555-8555-${String(i).padStart(12,'0')}`,type:'text',label:'Text',required:true}))};
   if(mode==='read')p.read_observation={...p.read_observation,checked_at:'2026-10-25T10:00:00Z',expires_at:'2026-11-01T10:00:00Z'};
   if(mode==='create')p.create_assigned_observation={...p.create_assigned_observation,checked_at:'2026-10-25T10:00:00Z',expires_at:'2026-11-01T10:00:00Z'};
   if(mode==='child')p.children[0]={...p.children[0],checked_at:'2026-10-25T10:00:00Z',expires_at:'2026-11-01T10:00:00Z'};
   await setup(s,p);const r=(await s.openCreate(C)).reviewed;
   const input=answers=>({observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers});
   if(mode==='unicode')for(const value of ['bad\u0000','bad\ud800'])ok((await s.saveCreate(r,ids(),input({[r.questionnaire.definition.questions[0].id]:{value}}))).kind==='invalid','invalid_wire_unicode_refused');
   if(mode==='size'){
    const answers=Object.fromEntries(r.questionnaire.definition.questions.map(q=>[q.id,{value:'x'}])),id=ids(),bytes=()=>new TextEncoder().encode(JSON.stringify({operation_id:id.operation_id,command_version:1,capture_id:id.capture_id,child_id:C,questionnaire_version_id:Q,child_eligibility_ref:'a'.repeat(43),...input(answers)})).byteLength;
    let remaining=131072-bytes();for(const answer of Object.values(answers)){const count=Math.min(4999,Math.floor(remaining/4));answer.value+='😀'.repeat(count);remaining-=count*4;}Object.values(answers).at(-1).value+='a'.repeat(remaining);
    ok(bytes()===131072&&(await s.saveCreate(r,id,input(answers))).kind==='saved_locally','exact_create_utf8_limit_supported');Object.values(answers).at(-1).value+='a';ok((await s.saveCreate(r,ids(),input(answers))).kind==='invalid','create_utf8_limit_plus_one_refused');
   }
   if(['read','create','child'].includes(mode)){const next=Date.parse('2026-11-01T10:00:00Z');tick+=next-now;now=next;ok((await s.saveCreate(r,ids(),input({[Q]:{value:1}}))).kind==='expired',mode+'_independent_expiry');}
   if(mode==='oldtoken'){now=Date.parse('2026-10-27T10:00:02Z');tick+=86400000;const fresh=provision();for(const slot of ['read_observation','edit_observation','create_assigned_observation'])fresh[slot]={...fresh[slot],checked_at:'2026-10-27T10:00:00Z',expires_at:'2026-11-03T10:00:00Z'};fresh.children[0]={...fresh.children[0],checked_at:'2026-10-27T10:00:01Z',expires_at:'2026-11-03T10:00:01Z'};await setup(s,fresh);const next=Date.parse('2026-11-02T10:00:00Z');tick+=next-now;now=next;ok((await s.saveCreate(r,ids(),input({[Q]:{value:1}}))).kind==='expired'&&(await s.read()).kind==='available','refresh_never_extends_original_token_expiry');}
   s.close();
  }
  for(const version of [1,2]){const name='legacy-create-'+version,db=await new Promise(resolve=>{const q=indexedDB.open(name,version);q.onupgradeneeded=()=>{for(const table of ['records','definitions','partitions','downloads',...(version===2?['edit_actions']:[])])q.result.createObjectStore(table,{keyPath:'key'});};q.onsuccess=()=>resolve(q.result);});
   await new Promise(resolve=>{const tx=db.transaction(['records','definitions','downloads',...(version===2?['edit_actions']:[])],'readwrite');tx.objectStore('definitions').put({key:A+'/'+O+'/retained-definition',value:{legacy:true}});tx.objectStore('downloads').put({key:A+'/'+O+'/retained-download',partition:A+'/'+O,status:'partial',opaque_cursor:'retained'});if(version===2)tx.objectStore('edit_actions').put({key:A+'/'+O+'/retained-edit',partition:A+'/'+O,version:99,opaque:true});tx.objectStore('records').put({key:A+'/'+O+'/'+C,partition:A+'/'+O,pending:{opaque:true},conflict:{unknown_version:99}});tx.oncomplete=resolve;});db.close();now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts(name));await setup(s,provision());const history=await s.read();ok(history.records[0].pending.opaque&&history.records[0].conflict.unknown_version===99&&history.downloads[0].opaque_cursor==='retained','populated_v'+version+'_opaque_rows_preserved');const retained=await new Promise(resolve=>{const q=indexedDB.open(name);q.onsuccess=()=>{const d=q.result,t=d.transaction(['definitions',...(version===2?['edit_actions']:[])]),v=t.objectStore('definitions').get(A+'/'+O+'/retained-definition'),a=version===2?t.objectStore('edit_actions').get(A+'/'+O+'/retained-edit'):null;t.oncomplete=()=>{d.close();resolve(v.result.value.legacy&&(!a||a.result.opaque));};};});ok(retained,'populated_v'+version+'_definitions_and_edit_actions_preserved');s.close();
  }
  const versioned=await openHistoryStore(scope,opts('versioned-create'));await setup(versioned,provision());
  const next=await new Promise(resolve=>{const q=indexedDB.open('versioned-create',4);q.onsuccess=()=>resolve(q.result);});
  ok((await versioned.openCreate(C)).kind==='unavailable','stale_handle_refuses_after_versionchange');next.close();versioned.close();
  let refused=false;try{await openHistoryStore(scope,opts('versioned-create'));}catch{refused=true;}ok(refused,'unknown_newer_local_schema_never_reset');
  window.setupStore=await openHistoryStore(scope,opts('cross-create'));const begun=await window.setupStore.beginSetupRefresh();window.oldSetupTicket=begun.ticket;
  return checks;
 });checks.push(...extra);
 const other=await browserContext.newPage();await other.goto(origin);
 await other.evaluate(async()=>{const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'cross-create',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1}),t=await s.beginSetupRefresh(),p=provision();p.create_assigned_observation=null;p.children=[];p.create_state='not_permitted';if((await s.importProvision(p,t.ticket)).kind!=='committed')throw Error('cross_new_denial');s.close();});
 checks.push(...await page.evaluate(async()=>{const {provision,C}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');if((await window.setupStore.importProvision(provision(),window.oldSetupTicket)).kind!=='denied'||(await window.setupStore.openCreate(C)).kind!=='denied')throw Error('cross_stale_restore');window.setupStore.close();return ['cross_realm_refresh_generation_blocks_older_positive_after_denial'];}));await other.close();
 const reviewedChecks=await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const {detail}=await import('/apps/kdg-capture/web/tests/read-fixture.mjs');
  const checks=[],ok=(v,n)=>{if(!v)throw Error(n);checks.push(n);},scope={account_id:A,org_id:O};let now=Date.parse('2026-10-26T10:00:02Z'),tick=1,n=0;const opts=database=>({database,wall:()=>now,monotonic:()=>tick});
  const ids=()=>({capture_id:`aaaaaaaa-aaaa-4aaa-8aaa-${String(++n).padStart(12,'0')}`,operation_id:`bbbbbbbb-bbbb-4bbb-8bbb-${String(n).padStart(12,'0')}`}),input={observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value:1}}};
  const setup=async(s,p=provision())=>{const t=await s.beginSetupRefresh();return s.importProvision(p,t.ticket);};
  const mutate=async(database,table,work)=>{const db=await new Promise(resolve=>{const q=indexedDB.open(database);q.onsuccess=()=>resolve(q.result);});await new Promise((resolve,reject)=>{const tx=db.transaction(table,'readwrite');work(tx.objectStore(table));tx.oncomplete=resolve;tx.onabort=reject;});db.close();};
  const edit=async(s)=>{const p=provision(),capture=detail({owner_actor_id:p.actor_id,created_by:p.actor_id});await s.importEditContext({capture,editable_fields:['observation_date','answers'],read_observation:p.read_observation,edit_observation:p.edit_observation},{...scope,capture_id:C});return (await s.openEdit(C)).reviewed;};
  {
   const s=await openHistoryStore(scope,opts('review-collision'));await setup(s);const e=await edit(s),eid=ids().operation_id;ok((await s.saveEdit(e,eid,{observation_date:input.observation_date,answers:input.answers})).kind==='saved_locally','review_edit_identity_setup');const r=(await s.openCreate(C)).reviewed;
   ok((await s.saveCreate(r,{...ids(),capture_id:eid},input)).kind==='action_id_reused','create_capture_cannot_reuse_edit_operation');
   const ci=ids();await s.saveCreate(r,ci,input);ok((await s.saveEdit(e,ci.operation_id,{observation_date:input.observation_date,answers:input.answers})).kind==='action_id_reused','edit_operation_cannot_reuse_create_operation');s.close();
  }
  {
   const name='review-denial-ticket',s=await openHistoryStore(scope,opts(name));await setup(s);const t=await s.beginSetupRefresh();ok((await s.denySetup(t.ticket)).kind==='locked','current_ticket_denial_committed');s.close();const reopened=await openHistoryStore(scope,opts(name));ok((await reopened.denySetup(t.ticket)).kind==='superseded','committed_denial_ticket_replay_refused');reopened.close();
  }
  for(const identity of ['actor_id','membership_id']){
   const name='review-binding-'+identity,s=await openHistoryStore(scope,opts(name)),p=provision();for(const slot of ['read_observation','edit_observation','create_assigned_observation'])p[slot]={...p[slot],checked_at:'2026-10-26T10:00:01Z',expires_at:'2026-11-02T10:00:01Z'};await setup(s,p);
   const changed=provision();changed[identity]=identity==='actor_id'?C:'8';for(const slot of ['read_observation','edit_observation','create_assigned_observation'])changed[slot][identity]=changed[identity];ok((await setup(s,changed)).kind==='committed','new_'+identity+'_setup');const r=(await s.openCreate(C)).reviewed;
   ok(r.create_observation[identity]===changed[identity]&&r.read_observation[identity]===changed[identity],'merged_'+identity+'_binding_preserved');s.close();
  }
  {
   const s=await openHistoryStore(scope,opts('review-current-read-binding'));await setup(s);const r=(await s.openCreate(C)).reviewed,p=provision(),observation={...p.read_observation,membership_id:'8',checked_at:'2026-10-26T10:00:01Z',expires_at:'2026-11-02T10:00:01Z'},bounds={...scope,from_date:'2026-10-01',to_date:'2026-10-26',limit:2};
   ok((await s.importPage({...bounds,observation,items:[],next_cursor:null},bounds)).kind==='committed','new_history_membership_observed');ok((await s.saveCreate(r,ids(),input)).kind==='denied','current_read_membership_change_blocks_pinned_create');s.close();
  }
  for(const field of ['child_revision','assignment']){
   const s=await openHistoryStore(scope,opts('review-revision-'+field)),p=provision();p.children[0].checked_at='2026-10-26T10:00:02Z';p.children[0].expires_at='2026-11-02T10:00:02Z';await setup(s,p);const r=(await s.openCreate(C)).reviewed,changed=provision();if(field==='assignment')changed.children[0].assignment.assignment_revision='2';else changed.children[0].child_revision='2';await setup(s,changed);
   ok((await s.saveCreate(r,ids(),input)).kind==='denied','older_timestamp_changed_'+field+'_never_restores_old_eligibility');s.close();
  }
  for(const direction of ['all','assigned']){
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts('review-transition-'+direction));const all=()=>{const p=provision();p.create_all_observation={...p.create_assigned_observation,permission:'kdg_capture.capture.create.all'};p.children[0].create_permission='kdg_capture.capture.create.all';p.children[0].assignment=null;return p;};
   await setup(s,direction==='all'?provision():all());const r=(await s.openCreate(C)).reviewed;const changed=direction==='all'?all():provision();now+=2000;tick+=2000;for(const slot of ['read_observation','edit_observation','create_all_observation','create_assigned_observation'])if(changed[slot]){changed[slot].checked_at='2026-10-26T10:00:03Z';changed[slot].expires_at='2026-11-02T10:00:03Z';}await setup(s,changed);ok((await s.saveCreate(r,ids(),input)).kind==='denied','selected_create_'+direction+'_transition_refuses_old_handle');ok((await s.saveCreate((await s.openCreate(C)).reviewed,ids(),input)).kind==='saved_locally','selected_create_'+direction+'_transition_new_handle');s.close();
  }
  {
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const name='review-unsupported',s=await openHistoryStore(scope,opts(name));await setup(s);await s.saveCreate((await s.openCreate(C)).reviewed,ids(),input);const good=(await s.readCreateActions()).actions[0];
   for(const patch of [{version:99},{serialized:'{}'},{foreign:true},{capture_id:C}]){const action=ids().operation_id,pending=structuredClone(good.pending);pending.command.operation_id=action;const identity=JSON.parse(good.content);identity.pending=pending;const row={...good,key:A+'/'+O+'/'+action,action_id:action,pending,serialized:JSON.stringify(pending.command),content:JSON.stringify(identity),result:{...good.result,operation_id:action},...patch};if(row.foreign){delete row.foreign;row.pending.account_id=C;}await mutate(name,'create_actions',store=>store.put(row));}
   const out=await s.readCreateActions({limit:100});ok(out.actions.length===1&&out.actions[0].action_id===good.action_id,'unsupported_corrupt_create_rows_withheld');s.close();
   const db=await new Promise(resolve=>{const q=indexedDB.open(name);q.onsuccess=()=>resolve(q.result);});const count=await new Promise(resolve=>{const tx=db.transaction('create_actions'),q=tx.objectStore('create_actions').count();tx.oncomplete=()=>resolve(q.result);});db.close();ok(count===5,'unsupported_create_rows_retained');
  }
  {
   const name='review-partitions',s=await openHistoryStore(scope,opts(name)),foreign=await openHistoryStore({account_id:C,org_id:O},opts(name));await setup(s);const fp=provision();fp.account_id=C;for(const slot of ['read_observation','edit_observation','create_assigned_observation']){fp[slot].account_id=C;fp[slot].resource_scope.account_id=C;}await setup(foreign,fp);const t=await s.beginSetupRefresh();ok((await foreign.importProvision(fp,t.ticket)).kind==='invalid','foreign_setup_ticket_refused');const r=(await s.openCreate(C)).reviewed;ok((await foreign.saveCreate(r,ids(),input)).kind==='invalid','foreign_create_handle_refused');const identity=ids();await s.saveCreate(r,identity,input);ok((await foreign.saveCreate((await foreign.openCreate(C)).reviewed,identity,input)).kind==='saved_locally','same_uuid_isolated_in_distinct_partition');ok((await foreign.readCreateActions({after:A+'/'+O+'/'+identity.operation_id})).kind==='unavailable','foreign_create_cursor_refused');s.close();foreign.close();
  }
  {
   const s=await openHistoryStore(scope,opts('review-fresh-realm'));await setup(s);const identity=ids();await s.saveCreate((await s.openCreate(C)).reviewed,identity,input);s.close();
  }
  {
   const s=await openHistoryStore(scope,opts('review-edit-denial-collision'));await setup(s);const e=await edit(s),p=provision();p.edit_observation=null;p.questionnaire.definition.questions[0].label='Collision';ok((await setup(s,p)).kind==='unavailable','definition_collision_with_edit_denial_refused');ok((await s.saveEdit(e,ids().operation_id,{observation_date:input.observation_date,answers:input.answers})).kind==='denied','collision_preserves_current_edit_denial_latch');ok((await s.read()).kind==='available','edit_denial_collision_preserves_read');s.close();
  }
  for(const failed of [false,true]){
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts('review-child-loss-'+failed));await setup(s);const r=(await s.openCreate(C)).reviewed,p=provision();p.children=[];p.create_state='no_eligible_children';const ticket=await s.beginSetupRefresh(),put=IDBObjectStore.prototype.put;
   if(failed)IDBObjectStore.prototype.put=function(...args){if(this.name==='setups'){this.transaction.abort();throw Error('synthetic child loss write');}return put.apply(this,args);};
   try{ok((await s.importProvision(p,ticket.ticket)).kind===(failed?'unavailable':'committed'),'child_omission_'+failed+'_observed');}finally{IDBObjectStore.prototype.put=put;}
   ok((await s.saveCreate(r,ids(),input)).kind==='denied','child_omission_'+failed+'_old_handle_blocked');const reopened=await openHistoryStore(scope,opts('review-child-loss-'+failed));ok((await reopened.openCreate(C)).kind==='denied','child_omission_'+failed+'_new_handle_cannot_bypass_loss');reopened.close();ok((await s.read()).kind==='available','child_omission_'+failed+'_preserves_own_read');ok((await setup(s)).kind==='denied','child_omission_'+failed+'_older_positive_refused');
   now+=2000;tick+=2000;const newer=provision();newer.children[0].checked_at='2026-10-26T10:00:03Z';newer.children[0].expires_at='2026-11-02T10:00:03Z';ok((await setup(s,newer)).kind==='committed','child_omission_'+failed+'_newer_restores_future_open');ok((await s.saveCreate(r,ids(),input)).kind==='denied','child_omission_'+failed+'_original_handle_remains_invalid');ok((await s.saveCreate((await s.openCreate(C)).reviewed,ids(),input)).kind==='saved_locally','child_omission_'+failed+'_new_handle_saves');s.close();
  }
  for(const completion of [false,true]){
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts('review-expiry-recovery-'+completion)),p=provision();p.create_assigned_observation.checked_at='2026-10-25T10:00:00Z';p.create_assigned_observation.expires_at='2026-11-01T10:00:00Z';await setup(s,p);const r=(await s.openCreate(C)).reviewed,identity=ids(),tx=IDBDatabase.prototype.transaction;
   if(completion)IDBDatabase.prototype.transaction=function(...args){const transaction=tx.apply(this,args);transaction.addEventListener('complete',()=>{const end=Date.parse('2026-11-01T10:00:00Z');tick+=end-now;now=end;},{once:true});return transaction;};
   try{ok((await s.saveCreate(r,identity,input)).kind===(completion?'expired':'saved_locally'),'create_expiry_'+completion+'_initial_completion');}finally{IDBDatabase.prototype.transaction=tx;}
   if(!completion){const end=Date.parse('2026-11-01T10:00:00Z');tick+=end-now;now=end;}
   ok((await s.saveCreate(r,identity,input)).kind==='saved_locally'&&(await s.readCreateActions()).actions.length===1,'create_expiry_'+completion+'_exact_committed_result_recovers');ok((await s.saveCreate(r,ids(),input)).kind==='expired','create_expiry_'+completion+'_new_write_still_requires_original_authority');s.close();
  }
  {
   now=Date.parse('2026-10-26T10:00:02Z');tick=1;const s=await openHistoryStore(scope,opts('review-inflight-current'));await setup(s);const r=(await s.openCreate(C)).reviewed,get=IDBObjectStore.prototype.get;let current=true;
   IDBObjectStore.prototype.get=function(...args){const request=get.apply(this,args);if(this.name==='create_actions')request.addEventListener('success',()=>{current=false;},{once:true});return request;};
   try{ok((await s.saveCreate(r,ids(),input,{isCurrent:()=>current})).kind==='unavailable','inflight_account_predicate_change_aborts_save');}finally{IDBObjectStore.prototype.get=get;}ok((await s.readCreateActions()).actions.length===0,'inflight_account_change_leaves_no_action');s.close();
  }
  {
   const name='review-malformed-reference',s=await openHistoryStore(scope,opts(name));await setup(s);await s.saveCreate((await s.openCreate(C)).reviewed,ids(),input);const original=(await s.readCreateActions()).actions[0];
   for(const ref of ['', 'a'.repeat(42),'a'.repeat(44),'!'.repeat(43)]){const row=structuredClone(original);row.pending.command.child_eligibility_ref=ref;row.serialized=JSON.stringify(row.pending.command);const identity=JSON.parse(row.content);identity.pending=row.pending;identity.reviewed.child.child_eligibility_ref=ref;row.content=JSON.stringify(identity);await mutate(name,'create_actions',store=>store.put(row));ok((await s.readCreateActions()).actions.length===0,'malformed_retained_reference_'+ref.length+'_withheld');}s.close();
  }
  {
   const s=await openHistoryStore(scope,opts('review-unsupported'));let after,seen=[],pages=0;do{const out=await s.readCreateActions({limit:1,...(after?{after}:{})});seen.push(...out.actions);after=out.next_key;pages++;if(pages>10)throw Error('pagination_loop');}while(after);ok(pages===5&&seen.length===1,'small_limit_pagination_advances_through_unsupported_rows');s.close();
  }
  return checks;
 });checks.push(...reviewedChecks);
 const fresh=await browserContext.newPage();await fresh.goto(origin);checks.push(...await fresh.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-fresh-realm',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1});const a=(await s.readCreateActions()).actions[0],r=JSON.parse(a.content).reviewed,c=a.pending.command;
  if((await s.saveCreate(r,{capture_id:c.capture_id,operation_id:c.operation_id},{observation_date:c.observation_date,captured_at:c.captured_at,answers:c.answers})).kind!=='saved_locally'||(await s.readCreateActions()).actions.length!==1)throw Error('fresh_realm_retry');const view=await s.read();if(view.records[0].baseline||view.records[0].local_capture.capture_id!==c.capture_id)throw Error('fresh_realm_local_capture');s.close();return ['fresh_realm_reopen_recovers_original_content_and_identity'];
 }));await fresh.close();
 await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-denial',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1}),t=await s.beginSetupRefresh();await s.importProvision(provision(),t.ticket);window.crossDenialStore=s;window.crossDenialReviewed=(await s.openCreate(C)).reviewed;
 });
 const denialRealm=await browserContext.newPage();await denialRealm.goto(origin);await denialRealm.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-denial',wall:()=>Date.parse('2026-10-26T10:00:02Z'),monotonic:()=>1}),t=await s.beginSetupRefresh();if((await s.denySetup(t.ticket)).kind!=='locked')throw Error('second_realm_ticket_denial');s.close();
 });
 checks.push(...await page.evaluate(async()=>{const {Q}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=window.crossDenialStore;if((await s.read()).kind==='available'||(await s.saveCreate(window.crossDenialReviewed,{capture_id:'cccccccc-cccc-4ccc-8ccc-cccccccccccc',operation_id:'dddddddd-dddd-4ddd-8ddd-dddddddddddd'},{observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value:1}}})).kind==='saved_locally')throw Error('cross_realm_full_denial_not_seen');return ['second_realm_full_ticket_denial_blocks_open_form_and_read'];}));
 await denialRealm.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-denial',wall:()=>Date.parse('2026-10-26T10:00:04Z'),monotonic:()=>1}),t=await s.beginSetupRefresh(),p=provision();for(const slot of ['read_observation','edit_observation','create_assigned_observation']){p[slot].checked_at='2026-10-26T10:00:03Z';p[slot].expires_at='2026-11-02T10:00:03Z';}if((await s.importProvision(p,t.ticket,{restoreDenied:true})).kind!=='committed')throw Error('cross_realm_explicit_restore');s.close();
 });
 checks.push(...await page.evaluate(async()=>{const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');window.crossDenialStore.close();const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-denial',wall:()=>Date.parse('2026-10-26T10:00:04Z'),monotonic:()=>1});if((await s.read()).kind!=='available'||(await s.openCreate(C)).kind!=='opened')throw Error('cross_realm_restore_not_visible');s.close();return ['second_realm_explicit_newer_restore_visible_after_reopen'];}));await denialRealm.close();
 await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');window.childRestoreNow=Date.parse('2026-10-26T10:00:02Z');window.childRestoreTick=1;
  const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-child-restore',wall:()=>window.childRestoreNow,monotonic:()=>window.childRestoreTick});let t=await s.beginSetupRefresh();await s.importProvision(provision(),t.ticket);window.childRestoreStore=s;window.childRestoreReviewed=(await s.openCreate(C)).reviewed;
  const lost=provision();lost.children=[];lost.create_state='no_eligible_children';t=await s.beginSetupRefresh();if((await s.importProvision(lost,t.ticket)).kind!=='committed')throw Error('first_page_child_loss');
 });
 const childRestoreRealm=await browserContext.newPage();await childRestoreRealm.goto(origin);await childRestoreRealm.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,provision}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');const s=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-child-restore',wall:()=>Date.parse('2026-10-26T10:00:04Z'),monotonic:()=>1}),t=await s.beginSetupRefresh(),p=provision();p.children[0].checked_at='2026-10-26T10:00:03Z';p.children[0].expires_at='2026-11-02T10:00:03Z';if((await s.importProvision(p,t.ticket)).kind!=='committed')throw Error('second_page_child_restore');s.close();
 });
 checks.push(...await page.evaluate(async()=>{
  const {openHistoryStore}=await import('/compiled/web/src/history-store.js');const {A,O,C,Q}=await import('/apps/kdg-capture/web/tests/provision-fixture.mjs');window.childRestoreNow+=2000;window.childRestoreTick+=2000;const old=window.childRestoreStore;
  if((await old.saveCreate(window.childRestoreReviewed,{capture_id:'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',operation_id:'ffffffff-ffff-4fff-8fff-ffffffffffff'},{observation_date:'2026-10-25',captured_at:'2026-10-26T10:00:02Z',answers:{[Q]:{value:1}}})).kind==='saved_locally')throw Error('second_page_child_restore_revived_pre_loss_form');old.close();
  const reopened=await openHistoryStore({account_id:A,org_id:O},{database:'review-cross-child-restore',wall:()=>window.childRestoreNow,monotonic:()=>window.childRestoreTick});try{if((await reopened.openCreate(C)).kind!=='opened')throw Error('second_page_child_restore_must_override_equal_process_latch');}finally{reopened.close();}return ['second_page_child_restore_invalidates_pre_loss_form','second_page_child_restore_allows_reopened_fresh_create'];
 }));await childRestoreRealm.close();
passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n');throw error;}finally{
 if(browser)await browser.close();if(server){const done=new Promise(r=>server.close(r));for(const s of sockets)s.destroy();await done;}
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,checks,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limits:['synthetic Chromium IndexedDB only','no physical persistence, eviction or at-rest claim','restart checks persist wall watermark; monotonic anchor exists only within process']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));if(!record.passed)process.exitCode=1;
}
