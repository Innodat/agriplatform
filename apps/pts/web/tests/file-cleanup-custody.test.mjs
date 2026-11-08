import test from 'node:test';
import assert from 'node:assert/strict';
import {registerHooks} from 'node:module';

// Execute the actual browser module. Only origin configuration, browser storage
// and the HTTP owner are substituted; the custody/ordering code is unchanged.
globalThis.location={origin:'https://pts.fixture.test'};
const storage=new Map();
globalThis.localStorage={getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)};
let prepare;
globalThis.ptsCleanupTransport={prepare:identity=>prepare(identity)};
// Model the browser's shared lock queue independently of either module instance.
let lock=Promise.resolve();
Object.defineProperty(globalThis,'navigator',{configurable:true,value:{locks:{request(_name,_options,operation){const result=lock.then(operation);lock=result.catch(()=>{});return result;}}}});
registerHooks({
 resolve(specifier,context,next){
  if(specifier==='./auth'&&new URL(context.parentURL).pathname.endsWith('/src/fileTransport.ts'))return {url:'data:text/javascript,export function filePreparationIsCurrent(){return globalThis.ptsPreparationCurrent!==false}',shortCircuit:true};
  if(specifier==='@platform/ui-business')return {url:'data:text/javascript,export function createNativeFileClient(){return globalThis.ptsCleanupTransport}',shortCircuit:true};
  return next(specifier,context);
 },
 load(url,context,next){
  const loaded=next(url,context);
  if(new URL(url).pathname.endsWith('/src/fileTransport.ts'))return {...loaded,source:'import.meta.env={VITE_PTS_FILE_ORIGIN:"https://files.pts.fixture.test"};\n'+loaded.source};
  return loaded;
 },
});
const custody=await import('../src/fileTransport.ts');
// Separate module instances model two loaded app clients; their only shared
// state is the browser's storage (no storage event delivery is needed).
const otherTab=await import('../src/fileTransport.ts?other-tab');
const original={id:'account',token:'original',refreshToken:'original-refresh',sessionId:'session'};
const newer={...original,token:'newer',refreshToken:'newer-refresh'};
const pair={account_id:'account',session_id:'session'};
const deferred=()=>{let resolve;const promise=new Promise(done=>{resolve=done;});return {promise,resolve};};

test('delayed old preparation cannot replace a newer same-session auth observation',async()=>{
 await custody.forgetFileCleanup();const delayed=deferred();
 prepare=identity=>identity.token==='original'?delayed.promise:Promise.resolve(pair);
 const old=custody.prepareFileCleanup(original).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 await custody.prepareFileCleanup(newer);
 delayed.resolve(pair);await old;
 const saved=custody.pendingFileIdentity();
 assert(saved.refreshToken===newer.refreshToken,'delayed original response downgraded current refresh custody');
});

test('delayed preparation cannot overwrite verified cleanup rotation',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const delayed=deferred();prepare=()=>delayed.promise;
 const old=custody.prepareFileCleanup(original).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 await custody.beginFileCleanup();
 await custody.retainFileCleanupRefresh(original,{id:'account',token:'rotated',refreshToken:'rotated-refresh'});
 delayed.resolve(pair);await old;
 const saved=custody.pendingFileIdentity();
 assert(saved.refreshToken==='rotated-refresh','delayed response downgraded verified cleanup rotation');
 assert(saved.revocationToken==='rotated','verified revocation credential was lost');
 assert(saved.pending===true,'cleanup must remain visibly incomplete');
});

test('forgotten custody cannot be recreated by a delayed preparation',async()=>{
 await custody.forgetFileCleanup();const delayed=deferred();prepare=()=>delayed.promise;
 const old=custody.prepareFileCleanup(original).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 await custody.forgetFileCleanup();delayed.resolve(pair);await old;
 assert.equal(custody.pendingFileIdentity(),null);
});

test('verified same-account replacement survives original cleanup and delayed preparation',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const delayed=deferred();prepare=()=>delayed.promise;
 const late=custody.prepareFileCleanup(original).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 const replacement={id:'account',sessionId:'replacement-session',token:'replacement-token',refreshToken:'replacement-refresh'};
 await custody.beginFileCleanup(replacement);delayed.resolve(pair);await late;
 const saved=custody.pendingFileIdentity();
 assert.equal(saved.pending,true);
 assert.equal(saved.sessionId,original.sessionId);
 assert.deepEqual(saved.replacement,replacement,'replacement credentials must survive cleanup/reload');
 await assert.rejects(()=>custody.prepareFileCleanup(replacement),/required/);
});

for(const initiallyRetained of [false,true])test('another tab completed cleanup supersedes delayed preparation '+(initiallyRetained?'with original and replacement custody':'from no retained record'),async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;
 if(initiallyRetained){await custody.prepareFileCleanup(original);await custody.beginFileCleanup({...newer,sessionId:'replacement-session'});}
 const delayed=deferred();prepare=()=>delayed.promise;
 const late=custody.prepareFileCleanup(original,true).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 await otherTab.beginFileCleanup();await otherTab.forgetFileCleanup();
 delayed.resolve(pair);const result=await late;
 assert.equal(result.message,'file_cleanup_superseded');
 assert.equal(custody.pendingFileIdentity(),null,'completed cleanup regained original/replacement credentials');
 const raw=JSON.parse(storage.get('pts-file-cleanup-v1')||'null');
 assert(!raw||(!raw.token&&!raw.refreshToken&&!raw.revocationToken&&!raw.replacement),'cleared storage contains credentials');
});

test('another tab new valid custody survives an older preparation after completed clear',async()=>{
 await custody.forgetFileCleanup();const delayed=deferred();prepare=identity=>identity.token===original.token?delayed.promise:Promise.resolve(pair);
 const late=custody.prepareFileCleanup(original).catch(error=>error);
 await new Promise(resolve=>setImmediate(resolve));
 await otherTab.forgetFileCleanup();await otherTab.prepareFileCleanup(newer);
 delayed.resolve(pair);await late;
 const saved=custody.pendingFileIdentity();
 assert.equal(saved.token,newer.token);assert.equal(saved.refreshToken,newer.refreshToken);
});

test('cleared marker is secret-free and never means pending cleanup or authority',async()=>{
 await custody.forgetFileCleanup();
 assert.equal(custody.pendingFileIdentity(),null);
 const marker=JSON.parse(storage.get('pts-file-cleanup-v1'));
 assert.deepEqual(Object.keys(marker).sort(),['cleared','revision','version']);
 assert.equal(marker.cleared,true);
});

test('existing valid v1 recovery remains readable and rotates without losing its original or replacement',async()=>{
 const replacement={...newer,sessionId:'replacement-session'};
 storage.set('pts-file-cleanup-v1',JSON.stringify({version:1,...original,pending:true,replacement}));
 assert.equal(custody.pendingFileIdentity().token,original.token);
 await custody.retainFileCleanupRefresh(original,{id:original.id,token:newer.token,refreshToken:newer.refreshToken});
 const record=custody.pendingFileIdentity();
 assert.equal(record.token,original.token);assert.equal(record.revocationToken,newer.token);
 assert.equal(record.refreshToken,newer.refreshToken);assert.deepEqual(record.replacement,replacement);
});

test('unavailable locks or failed storage refuse native custody without losing valid recovery',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const saved=storage.get('pts-file-cleanup-v1'),locks=navigator.locks,setItem=localStorage.setItem;
 try{
  navigator.locks=undefined;
  await assert.rejects(()=>custody.prepareFileCleanup(newer),/file_cleanup_recovery_unavailable/);
  assert.equal(storage.get('pts-file-cleanup-v1'),saved);
  navigator.locks=locks;localStorage.setItem=()=>{throw new Error('fixture_storage_failed');};
  await assert.rejects(()=>custody.forgetFileCleanup(),/fixture_storage_failed/);
  assert.equal(storage.get('pts-file-cleanup-v1'),saved);
 }finally{navigator.locks=locks;localStorage.setItem=setItem;}
});

test('successful owner preparation with failed final persistence retains cleanup-only recovery until retry',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;
 const setItem=localStorage.setItem;let writes=0;
 localStorage.setItem=(key,value)=>{if(++writes===2)throw new Error('fixture_final_write_failed');return setItem(key,value);};
 try{await assert.rejects(()=>custody.prepareFileCleanup(original),/fixture_final_write_failed/);}finally{localStorage.setItem=setItem;}
 const pending=custody.pendingFileIdentity();assert(pending?.token===original.token&&pending.pending===true,'receipted preparation lost recovery after failed persistence');
 await custody.beginFileCleanup();assert.equal(custody.pendingFileIdentity().token,original.token);
});

test('failed pending writes keep latest verified replacement and rotation without superseding another tab clear',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const setItem=localStorage.setItem;
 const first={...newer,sessionId:'replacement-session'},latest={...first,token:'latest-replacement',refreshToken:'latest-replacement-refresh'};
 localStorage.setItem=()=>{throw new Error('fixture_storage_failed');};
 try{
  await assert.rejects(()=>custody.beginFileCleanup(first));
  await assert.rejects(()=>custody.beginFileCleanup(latest));
  assert.equal(custody.pendingFileIdentity()?.replacement?.refreshToken,latest.refreshToken,'failed writes discarded verified replacement rotation');
  await assert.rejects(()=>custody.retainFileCleanupRefresh(original,{id:original.id,token:newer.token,refreshToken:newer.refreshToken}));
  assert.equal(custody.pendingFileIdentity()?.revocationToken,newer.token,'failed write discarded verified original rotation');
 }finally{localStorage.setItem=setItem;}
 await otherTab.forgetFileCleanup();assert.equal(custody.pendingFileIdentity(),null,'volatile failed-write custody survived another tab completed clear');
});

for(const operation of ['replacement','original-rotation'])test('queued same-tab '+operation+' mutations preserve newest verified credentials behind held lock',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const held=deferred(),entered=deferred();
 const blocker=navigator.locks.request('pts-file-cleanup-v1',{},async()=>{entered.resolve();await held.promise;});
 await entered.promise;
 const first=operation==='replacement'?custody.beginFileCleanup({...newer,sessionId:'replacement-session'}):custody.retainFileCleanupRefresh(original,{id:original.id,token:'first-rotation',refreshToken:'first-refresh'});
 const latest=operation==='replacement'?custody.beginFileCleanup({...newer,sessionId:'replacement-session',token:'latest-replacement',refreshToken:'latest-refresh'}):custody.retainFileCleanupRefresh(original,{id:original.id,token:'latest-rotation',refreshToken:'latest-refresh'});
 // Attach rejection handling before releasing either queued write.
 const outcomes=Promise.allSettled([first,latest]);held.resolve();await blocker;await outcomes;
 const saved=custody.pendingFileIdentity();
 assert.equal(operation==='replacement'?saved.replacement?.refreshToken:saved.refreshToken,'latest-refresh','queued earlier mutation displaced latest verified credentials');
 const durable=JSON.parse(storage.get('pts-file-cleanup-v1'));
 assert.equal(operation==='replacement'?durable.replacement?.refreshToken:durable.refreshToken,'latest-refresh','latest verified credentials are not durable after lock release');
});


test('SDK freshness rejection at final queued write cannot recreate volatile cleanup custody',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;globalThis.ptsPreparationCurrent=true;
 const request=navigator.locks.request,entered=deferred(),release=deferred();let calls=0;
 navigator.locks.request=(name,options,operation)=>request(name,options,++calls===2?async()=>{entered.resolve();await release.promise;return operation();}:operation);
 try{
  const pending=custody.prepareFileCleanup(original).catch(error=>error);await entered.promise;
  globalThis.ptsPreparationCurrent=false;release.resolve();await pending;
  assert.equal(custody.pendingFileIdentity(),null,'stale final preparation recreated volatile original custody');
  const raw=JSON.parse(storage.get('pts-file-cleanup-v1'));assert(!raw.token&&!raw.refreshToken&&!raw.replacement,'stale final preparation recreated durable credentials');
 }finally{navigator.locks.request=request;globalThis.ptsPreparationCurrent=true;}
});

test('ordinary empty-only completion cannot erase native custody that appeared during provider logout',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;
 await otherTab.prepareFileCleanup(original);
 await assert.rejects(()=>custody.forgetFileCleanup(true),/file_cleanup_required/);
 assert.equal(custody.pendingFileIdentity()?.token,original.token,'ordinary completion erased unconfirmed native cleanup');
 assert.equal(custody.pendingFileIdentity()?.pending,true,'known incomplete native work lost its durable reload notice');
});

for(const action of ['clear','replacement'])test('operation-owned '+action+' refuses another tab newer custody after original completion',async()=>{
 await custody.forgetFileCleanup();prepare=async()=>pair;await custody.prepareFileCleanup(original);
 const observed=custody.observeFileCleanup();
 await otherTab.forgetFileCleanup();await otherTab.prepareFileCleanup(newer);
 const before=storage.get('pts-file-cleanup-v1');
 await assert.rejects(()=>action==='clear'?custody.forgetFileCleanup(false,observed):custody.beginFileCleanup({...newer,sessionId:'other-session'},observed),/superseded/);
 assert.equal(storage.get('pts-file-cleanup-v1'),before,'stale current-owner mutation changed newer custody');
});

for(const supersession of ['custody','auth'])test('delayed clear401 cannot prepare or mutate after newer '+supersession+' observation',async()=>{
 await custody.forgetFileCleanup();let preparations=0,current=true;
 prepare=async()=>{preparations++;return pair;};await custody.prepareFileCleanup(original);
 const observation={...custody.observeFileCleanup(),current:()=>current},delayed=deferred();let clears=0;
 globalThis.ptsCleanupTransport.clear=async()=>{if(++clears===1){await delayed.promise;throw {status:401};}return {provider_session:'absent'};};
 const clearing=custody.clearFiles(original,observation).catch(error=>error);
 if(supersession==='custody'){await otherTab.forgetFileCleanup();await otherTab.prepareFileCleanup(newer);}else current=false;
 const before=storage.get('pts-file-cleanup-v1'),preparedBefore=preparations;
 delayed.resolve();await clearing;
 assert.equal(preparations,preparedBefore,'stale clear401 made a new receipt preparation request');
 assert.equal(storage.get('pts-file-cleanup-v1'),before,'stale clear401 changed current recovery custody');
});

test('current clear401 recovery hands off its own revisions and completes the genuine retry',async()=>{
 await custody.forgetFileCleanup();let preparations=0,clears=0;
 prepare=async()=>{preparations++;return pair;};await custody.prepareFileCleanup(original);
 const observation={...custody.observeFileCleanup(),current:()=>true};
 globalThis.ptsCleanupTransport.clear=async()=>{if(++clears===1)throw {status:401};return {provider_session:'absent'};};
 const proof=await custody.clearFiles(original,observation);
 assert.equal(proof.provider_session,'absent');assert.equal(preparations,2);assert.equal(clears,2);
 assert.equal(observation.raw,storage.get('pts-file-cleanup-v1'),'current recovery lost its own accepted revision');
 assert.equal(custody.pendingFileIdentity()?.token,original.token);
});
