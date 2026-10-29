/** KDG owns presentation, local partition selection and foreground execution; existing owners own contracts. */
import {createAuthEntry,type EntryAuth} from './auth-entry';
import {getCurrentContext,type EntryState} from './entry';
import {openHistoryStore,phoneHistoryDates,type OwnRecord,type ReviewedCreate,type ReviewedEdit} from './history-store';
import {loadProvision} from './provision';
import {loadEditContext} from './edit-context';
import {downloadOwnHistory} from './history-download';
import {deliverSavedCreate} from './create-delivery';
import {deliverSavedEdit} from './edit-delivery';
import {adminHistoryCaptures} from './admin-history';
import {id,strictJSON,object,freeze} from './read-validation';
import type {Provision} from '../../contracts/provision-generated/types.gen';
export const OWN_SIGNOUT='kdg-own-explicit-signout-v1';
export function acceptOwnSignIn(storage:Pick<Storage,'getItem'|'removeItem'>,org:string,account:string){if(!id(org)||!id(account))throw Error('scope');const raw=storage.getItem(OWN_SIGNOUT);if(raw!==null){const v=object(strictJSON(raw),['version','org_id'],['account_id']);if(v.version!==1||!id(v.org_id)||v.account_id!==undefined&&!id(v.account_id))throw Error('signout');if(v.org_id===org)storage.removeItem(OWN_SIGNOUT);}}
export const OWN_SELECTOR='kdg-own-partition-v1';
/** Synchronous negative fences are independent attempts; one failed write must not skip the durable lock. */
export async function invalidateOwnSelection(storage:Pick<Storage,'getItem'|'setItem'|'removeItem'>,org:string,affectedAccount?:string,onFailure?:(account?:string)=>void,removeSelection=true,captured?:Selector){
 let pin:Selector|null=captured??null,failed=false;const failure=()=>{failed=true;onFailure?.(affectedAccount??pin?.account_id);};
 if(!id(org)||affectedAccount!==undefined&&!id(affectedAccount)||captured!==undefined&&(captured.version!==1||captured.org_id!==org||!id(captured.account_id)||affectedAccount!==undefined&&captured.account_id!==affectedAccount)){failure();return Object.freeze({kind:'unavailable' as const});}
 try{const selected=ownSelection(storage,org);if(selected&&(!affectedAccount||selected.account_id===affectedAccount))pin=selected;}catch{failure();}
 try{storage.setItem(OWN_SIGNOUT,JSON.stringify({version:1,org_id:org,...(affectedAccount?{account_id:affectedAccount}:pin?{account_id:pin.account_id}:{})}));}catch{failure();}
 if(pin&&removeSelection)try{const selected=ownSelection(storage,org);if(selected?.account_id===pin.account_id)storage.removeItem(OWN_SELECTOR);}catch{failure();}
 // A captured prior selection remains the durable target if another tab publishes B.
 // No selected/captured partition means no IndexedDB work, including an all-only portal.
 if(pin){let saved:Awaited<ReturnType<typeof openHistoryStore>>|undefined;
  try{saved=await openHistoryStore(pin);const locked=await saved.deny();if(locked.kind!=='locked'&&(await saved.confirmLocked()).kind!=='locked')failure();}catch{failure();}finally{saved?.close();}
 }
 return Object.freeze({kind:failed?'unavailable' as const:'locked' as const});
}
function ownSelection(storage:Pick<Storage,'getItem'>,org:string):Selector|null{const raw=storage.getItem(OWN_SELECTOR);if(raw===null)return null;const v=object(strictJSON(raw),['version','account_id','org_id']);if(v.version!==1||!id(v.account_id)||!id(v.org_id))throw Error('selector');return v.org_id===org?v as Selector:null;}
export function hasExplicitOwnSignout(storage:Pick<Storage,'getItem'>,org:string,account:string){const raw=storage.getItem(OWN_SIGNOUT);if(raw===null)return false;const v=object(strictJSON(raw),['version','org_id'],['account_id']);if(v.version!==1||!id(v.org_id)||v.account_id!==undefined&&!id(v.account_id))throw Error('signout');return v.org_id===org&&(!v.account_id||v.account_id===account);}
/** A provider account observation can only remove prior local authority, never grant it. */
export function observeOwnAccount(storage:Pick<Storage,'getItem'|'setItem'|'removeItem'>,org:string,account:string|null,onFailure?:(account?:string)=>void,previousAccount?:string){
 try{const pin=ownSelection(storage,org);if(pin&&(account===null||pin.account_id!==account)&&(!previousAccount||pin.account_id===previousAccount))return invalidateOwnSelection(storage,org,pin.account_id,onFailure,false,pin);return Promise.resolve(Object.freeze({kind:'locked' as const}));}catch{onFailure?.(account??undefined);return Promise.resolve(Object.freeze({kind:'unavailable' as const}));}
}

type Selector=Readonly<{version:1;account_id:string;org_id:string}>;
type Store=Awaited<ReturnType<typeof openHistoryStore>>;
export type OwnForm=Readonly<{kind:'create';reviewed:ReviewedCreate}>|Readonly<{kind:'edit';reviewed:ReviewedEdit}>;
export type WorkspaceState=Readonly<{kind:'checking'|'ready'|'setup_required'|'locked'|'storage_error'|'signed_out'|'unavailable';account_id?:string;records:readonly OwnRecord[];children:readonly Provision['children'][number][];next_key:string|null;online:boolean;syncing:boolean;loadingMore?:boolean;canAdmin:boolean;notice:string}>;
type Options=Readonly<{org:string;auth?:EntryAuth;online:boolean;request?:typeof fetch;beginSignIn:()=>Promise<void>;publish(state:WorkspaceState):void;shellReady():Promise<boolean>;updatePending?:()=>boolean;selectedCapture?:()=>string|null;storage?:Pick<Storage,'getItem'|'setItem'|'removeItem'>;openStore?:typeof openHistoryStore}>;
export function createOwnWorkspace(options:Options){
 const storage=options.storage??localStorage,open=options.openStore??openHistoryStore,owner=crypto.randomUUID();
 let authOwner=options.auth;let online=options.online,disposed=false,fatal=false,admissionBlocked=false,generation=0,store:Store|undefined,account:string|undefined,lastAccount:string|undefined,entry:ReturnType<typeof createAuthEntry>|undefined;
 let accessExpiresAt=0,authorityTimer:ReturnType<typeof setTimeout>|undefined,viewVersion=0,paging:Promise<void>|undefined;
 let active:AbortController|undefined,running:Promise<void>|undefined,rerun=false,locked:Promise<void>=Promise.resolve();
 let state:WorkspaceState=freeze({kind:'checking',records:[],children:[],next_key:null,online,syncing:false,canAdmin:false,notice:''});
 const publish=(patch:Partial<WorkspaceState>)=>{if(!disposed){state=freeze({...state,...patch,online});options.publish(state);}};
 const clear=(kind:WorkspaceState['kind'],notice='')=>{viewVersion++;clearTimeout(authorityTimer);publish({kind,records:[],children:[],next_key:null,canAdmin:false,syncing:false,loadingMore:false,notice});};
 const selected=():Selector|null=>{const raw=storage.getItem(OWN_SELECTOR);if(raw===null)return null;const v=object(strictJSON(raw),['version','account_id','org_id']);if(v.version!==1||!id(v.account_id)||!id(v.org_id))throw Error('selector');return v as Selector;};
 const signedOut=()=>{const raw=storage.getItem(OWN_SIGNOUT);if(raw===null)return false;const v=object(strictJSON(raw),['version','org_id'],['account_id']);if(v.version!==1||!id(v.org_id)||v.account_id!==undefined&&!id(v.account_id))throw Error('signout');if(v.org_id!==options.org)return false;const pin=selected();return !v.account_id||!pin||pin.org_id!==options.org||pin.account_id===v.account_id;};
 const remove=(affected?:string)=>{const pin=selected();if(pin?.org_id===options.org&&(!affected||pin.account_id===affected))storage.removeItem(OWN_SELECTOR);};
 const stop=()=>{generation++;active?.abort();active=undefined;};
 const isCurrent=(n:number)=>!disposed&&!fatal&&generation===n;
 const storageGuidance=(error:unknown)=>error instanceof Error&&error.message==='storage_update_blocked'?'Close other KDG Capture windows to update, then Retry. Saved work is retained.':error instanceof Error&&error.message==='storage_update_unavailable'?'App update could not complete. Saved work is retained. Retry.':'Saved work could not be opened. Check device storage and Retry; keep any unsaved input open.';
 async function fence(notice:string,preserveSelector=true){
  if(disposed)return;admissionBlocked=true;stop();clear('locked',notice);const affected=store;store=undefined;const prior=account??lastAccount;account=undefined;
  // A negative observation in another tab must not race that tab's new selector.
  // Explicit Sign out removes its own selection; other fences lock only the bound partition.
  try{if(!preserveSelector&&prior)remove(prior);}catch{fatal=true;}
  locked=locked.then(async()=>{let target:Store|undefined;try{affected?.close();const targetAccount=prior;if(targetAccount)target=await open({account_id:targetAccount,org_id:options.org});if(target&&(await target.deny()).kind!=='locked'&&(await target.confirmLocked()).kind!=='locked')fatal=true;}catch{fatal=true;}finally{target?.close();}if(fatal)clear('storage_error','Could not lock saved work. Keep this window closed to capture and check device storage before retrying.');});
  await locked;void prior;
 }
 function armAuthority(){clearTimeout(authorityTimer);if(accessExpiresAt){const remaining=accessExpiresAt-Date.now();authorityTimer=setTimeout(()=>{void local(generation,true);},Math.min(30000,remaining>0?remaining:30000));}}
 function storageUnavailable(error?:unknown){
  // A failed read cannot establish renewal beyond this last guarded deadline.
  if(accessExpiresAt&&Date.now()>=accessExpiresAt){clear('locked','Online verification is required to open saved work.');return;}
  clear('storage_error',storageGuidance(error));armAuthority();
 }
 async function local(n=generation,preservePage=false,focusCapture=options.selectedCapture?.()){
  if(admissionBlocked)return;
  try{
   if(signedOut()){clear(online?'signed_out':'setup_required','Sign in explicitly to reopen saved work.');return;}
   // Bind the pending open before its first await, so negative events fence A rather
   // than a later B selector. The selector itself still grants no read authority.
   let requireSelection=!online||selected()!==null;
   if(!store){const pin=selected();if(!pin||pin.org_id!==options.org){if(isCurrent(n))clear(online?'signed_out':'setup_required','Connect and complete setup on this device.');return;}
    if(lastAccount&&lastAccount!==pin.account_id){await fence('Account selection changed. Sign in again to reopen saved work.');return;}
    account=pin.account_id;lastAccount=account;requireSelection=true;
    const opened=await open(pin);if(!isCurrent(n)){opened.close();return;}store=opened;
   }
   const expected=account,saved=store;
   const current=()=>{try{const pin=selected();return isCurrent(n)&&!admissionBlocked&&account===expected&&!!expected&&!hasExplicitOwnSignout(storage,options.org,expected)&&(!pin?!requireSelection:pin.org_id===options.org&&pin.account_id===expected);}catch{return false;}};
   const checked=()=>{if(current())return true;if(isCurrent(n))void fence('Account selection changed. Sign in again to reopen saved work.');return false;};
   if(!checked())return;
   const view=await saved.workspace({}, {isCurrent:current});if(!checked())return;
   if(view.kind==='setup_required'){clear('setup_required','Complete online setup before observations are available.');return;}
   if(view.kind==='unavailable'){storageUnavailable();return;}
   if(view.kind!=='available'){clear('locked','Online verification is required to open saved work.');return;}
   let records=view.records;
   if((!preservePage||state.kind!=='ready')&&focusCapture&&!records.some(row=>row.capture.capture_id===focusCapture)){
    const focused=await saved.workspace({capture_id:focusCapture,limit:1},{isCurrent:current});if(!checked())return;
    if(focused.kind==='unavailable'){storageUnavailable();return;}
    if(focused.kind!=='available'){clear('locked','Online verification is required to open saved work.');return;}
    records=[...records,...focused.records];
   }
   if(!preservePage||state.kind!=='ready'){viewVersion++;publish({kind:'ready',account_id:account,records,children:view.setup?.children??[],next_key:view.next_key,loadingMore:false});}
   // Re-read through the store's authority guard at expiry and while this view remains open.
   accessExpiresAt=Date.parse(view.access_expires_at);armAuthority();
  }catch(error){if(isCurrent(n))storageUnavailable(error);}
 }

 function makeEntry(){
  entry?.dispose();if(!authOwner||!online||disposed||fatal)return;
  const auth=authOwner;
  try{if(signedOut()){clear('signed_out','Sign in explicitly to reopen saved work.');return;}}catch{fatal=true;clear('storage_error','Device storage is unavailable.');return;}
  if(admissionBlocked){clear('locked','Sign in again or Retry to verify access before reopening saved work.');return;}
  const guarded:EntryAuth={getSession:()=>auth.getSession(),refreshSession:()=>auth.refreshSession(),signOut:v=>auth.signOut(v),onAuthStateChange:callback=>auth.onAuthStateChange((event,value)=>{
   // A routing hint is not a bound session. Initial verified B is handled by onEntry;
   // an unexpected change while A is bound (including a pending local open) still fences A.
   const prior=account;
   if(event==='SIGNED_OUT'||value&&prior&&value.user.id!==prior){void fence('Sign in again to reopen your saved work.');}
   callback(event,value);
  })};
  entry=createAuthEntry({org:options.org,auth:guarded,online:true,request:options.request,beginSignIn:options.beginSignIn,publish:onEntry});void entry.start();
 }
 function onEntry(value:EntryState){
  if(disposed||fatal)return;
  if(value.kind==='checking'){stop();clear('checking');return;}
  if(value.kind==='authorized'){
   if(admissionBlocked)return;const authorized=value.context.account_id,observedGeneration=generation;
   void (async()=>{await locked;if(!isCurrent(observedGeneration)||admissionBlocked)return;let previous:string|undefined=account;try{previous??=selected()?.account_id;}catch{fatal=true;clear('storage_error','Device storage is unavailable.');return;}
    if(previous&&previous!==authorized){await fence('The previous account’s saved work is locked.');if(!fatal&&entry?.state()===value)admissionBlocked=false;}
    if(disposed||fatal||entry?.state()!==value)return;
    if(account!==authorized){store?.close();store=undefined;account=authorized;lastAccount=authorized;}
    trigger();})();return;
  }
  if(value.kind==='access_denied'||value.kind==='actor_setup_required'){void fence('Current access is unavailable for this account. Saved work is retained.');return;}
  // Expiry/outage is not a known access denial and cannot erase a valid local window.
  if(value.kind==='signed_out'||value.kind==='authentication_required'||value.kind==='authorization_unavailable'||value.kind==='invalid_response'){
   const notice=value.kind==='signed_out'||value.kind==='authentication_required'?'Sign in again to sync.':'Could not check access. Saved work can be used within its local access window.',n=generation;void local(n).then(()=>{if(isCurrent(n)&&state.kind!=='storage_error')publish({notice});});
  }
 }
 async function cycle(){
  const lease=entry?.acquireExecution();if(!lease||!online||fatal||disposed)return;
  const n=generation,controller=new AbortController(),abort=()=>controller.abort(),deadline=performance.now()+30000;
  active=controller;lease.signal.addEventListener('abort',abort,{once:true});const timer=setTimeout(abort,30000);
  const current=()=>isCurrent(n)&&online&&!controller.signal.aborted&&lease.isCurrent()&&performance.now()<deadline;
  const execution={signal:controller.signal,isCurrent:current};
  const phase=()=>({...execution,request:options.request,timeoutMs:Math.min(10000,Math.max(1,deadline-performance.now()))});
  publish({syncing:true,notice:'Checking setup and synchronizing saved observations…'});
  try{
   await locked;if(!current())return;
   if(!store){const opened=await open({account_id:lease.session.account_id,org_id:options.org});if(!current()){opened.close();return;}store=opened;account=lease.session.account_id;lastAccount=account;}
   const saved=store,pin={account_id:lease.session.account_id,org_id:options.org};
   const begun=await saved.beginSetupRefresh(execution);if(!current())return;
   if(begun.kind!=='started')throw Error('setup');
   const provision=await loadProvision(lease.session,pin,phase());if(!current())return;
   if(provision.kind==='error'&&provision.error_id==='access_denied'){await saved.denySetup(begun.ticket,execution);await fence('Current access was denied. Saved work is retained.');return;}
   if(provision.kind!=='loaded'){await local(n);if(current())publish({notice:'Could not refresh setup. Saved work remains on this device.'});return;}
   const imported=await saved.importProvision(provision.provision,begun.ticket,{...execution,restoreDenied:true});if(!current())return;
   if(imported.kind!=='committed')throw Error('provision');
   const ready=await options.shellReady();if(!current())return;
   if(ready)storage.setItem(OWN_SELECTOR,JSON.stringify({version:1,...pin}));
   await local(n);if(!current())return;
   if(!ready)publish({notice:'Setup data is saved. Offline shell setup is not complete; connect and Retry setup.'});
   if(options.updatePending?.()){publish({notice:'App update available. Save or cancel open input, then update before synchronizing.'});return;}
   const attempted:string[]=[];
   while(current()&&!options.updatePending?.()&&attempted.length<100){
    const claim=await saved.claimDelivery(owner,attempted,execution);if(!current()||claim.kind!=='claimed')break;
    attempted.push(claim.action_id);
    try{
     const send={store:saved,...execution,request:options.request,timeoutMs:Math.min(30000,Math.max(1,deadline-performance.now()))};
     const result=claim.type==='capture.create'?await deliverSavedCreate(lease.session,{...pin,action_id:claim.action_id},send):await deliverSavedEdit(lease.session,{...pin,action_id:claim.action_id},send);
     if(!current())return;
     if(result.kind==='authentication_required'){publish({notice:'Sign in again to sync. Saved observations remain on this device.'});break;}
     if(result.kind==='denied'){const view=await saved.workspace();if(view.kind!=='available'){await fence('Current access was denied. Saved work is retained.');return;}}
    }finally{if(current())await saved.releaseDelivery(claim,execution);}
   }
   const history=current()&&!options.updatePending?.()?await downloadOwnHistory(saved,lease.session,{...pin,...phoneHistoryDates()},phase()):undefined;
   if(!current())return;
   await local(n);if(state.kind==='storage_error')return;if(state.kind!=='ready'){await fence('Online verification is required to open saved work.');return;}
   // This separate online probe supplies navigation visibility only, never retained authority.
   const admin=await adminHistoryCaptures(lease.session,{...pin,...phoneHistoryDates(),limit:1},phase());
   if(current())publish({canAdmin:admin.kind==='loaded',notice:!ready?'Setup data is saved. Offline shell setup is not complete; connect and Retry setup.':history?.kind!=='complete'?'Observation history is incomplete or unavailable. Downloaded observations and saved work are retained. Retry setup.':state.records.some(r=>r.status==='Pending')?'Saved on this phone; waiting to sync':state.records.some(r=>r.status==='Needs attention')?'Needs attention: saved changes require review.':ready?'Offline setup complete.':''});
  }catch(error){if(current()){if(error instanceof Error&&error.message.startsWith('storage_update_'))clear('storage_error',storageGuidance(error));else{await local(n);publish({notice:'Could not complete synchronization. Keep unsaved input open and Retry; saved observations are retained.'});}}}
  finally{clearTimeout(timer);lease.signal.removeEventListener('abort',abort);lease.release();controller.abort();if(active===controller)active=undefined;if(isCurrent(n))publish({syncing:false});}
 }
 function trigger(){
  if(disposed||fatal||admissionBlocked||!online)return;
  if(running){rerun=true;return;}
  if(entry?.state().kind!=='authorized'){if(entry?.state().kind!=='checking')void entry?.retry();return;}
  running=cycle().finally(()=>{running=undefined;if(rerun){rerun=false;trigger();}});
 }
 return{
  state:()=>state,
  start(){try{const pin=selected();if(pin?.org_id===options.org)lastAccount=pin.account_id;}catch{storageUnavailable();return;}if(online&&authOwner)makeEntry();else void local();},
  setAuth(value:EntryAuth|undefined){if(value===authOwner)return;entry?.dispose();entry=undefined;authOwner=value;if(online&&authOwner)makeEntry();},
  setOnline(value:boolean){if(value===online)return;online=value;stop();entry?.dispose();entry=undefined;publish({syncing:false,canAdmin:false});if(online&&authOwner)makeEntry();else void local();},
  sync(){void local(generation,true).then(()=>{if(state.kind==='ready'||online)trigger();});},
  partitionChanged(){try{const pin=selected(),affected=account??lastAccount;if(affected&&(hasExplicitOwnSignout(storage,options.org,affected)||!pin||pin.account_id!==affected||pin.org_id!==options.org))void fence('Account selection changed. Sign in again to reopen saved work.');}catch{void fence('Device storage is unavailable.');}},
  async retry(){await locked;if(fatal)return;admissionBlocked=false;if(online&&authOwner){if(entry)await entry.retry();else makeEntry();}else await local();},
  async signIn(){stop();clear('signed_out');await options.beginSignIn();},
  async signOut(){const current=entry;try{storage.setItem(OWN_SIGNOUT,JSON.stringify({version:1,org_id:options.org,...((account??selected()?.account_id)?{account_id:account??selected()?.account_id}:{})}));}catch{fatal=true;}await fence('Saved work is locked on this device.',false);if(current)void current.signOut();else if(authOwner)void authOwner.signOut({scope:'local'}).catch(()=>{});clear(fatal?'storage_error':'signed_out',fatal?'Device storage must be checked before reopening.':'Sign in to continue.');},
  async openCreate(child:string){if(state.kind!=='ready'||!store)return null;const r=await store.openCreate(child);return r.kind==='opened'?Object.freeze({kind:'create' as const,reviewed:r.reviewed}):null;},
  async openEdit(capture_id:string){
   if(state.kind!=='ready'||!store)return null;const saved=store,n=generation;
   if(online){const lease=entry?.acquireExecution();if(lease)try{const pin={account_id:lease.session.account_id,org_id:options.org,capture_id};const loaded=await loadEditContext(lease.session,pin,{signal:lease.signal,isCurrent:()=>isCurrent(n)&&lease.isCurrent(),request:options.request});if(isCurrent(n)&&lease.isCurrent()&&loaded.kind==='loaded')await saved.importEditContext(loaded.context,pin,{signal:lease.signal,isCurrent:()=>isCurrent(n)&&lease.isCurrent(),restoreDenied:true});else if(isCurrent(n)&&lease.isCurrent()&&loaded.kind==='error'&&loaded.status===403){await saved.denyEdit(pin);const probe=await getCurrentContext(lease.session,options.org,{signal:lease.signal,request:options.request});if(isCurrent(n)&&lease.isCurrent()&&probe.kind==='access_denied')await fence('Current access was denied. Saved work is retained.');}}finally{lease.release();}}
   if(!isCurrent(n)||state.kind!=='ready')return null;const r=await saved.openEdit(capture_id);return r.kind==='opened'?Object.freeze({kind:'edit' as const,reviewed:r.reviewed}):null;
  },
  async save(form:OwnForm,ids:Readonly<{capture_id:string;operation_id:string}>,input:unknown){
   if(!['ready','storage_error'].includes(state.kind)||!store||form.reviewed.account_id!==account)return Object.freeze({kind:'unavailable'});
   const n=generation,execution={isCurrent:()=>isCurrent(n)&&['ready','storage_error'].includes(state.kind)},saved=store;
   const result=form.kind==='create'?await saved.saveCreate(form.reviewed,ids,input,execution):await saved.saveEdit(form.reviewed,ids.operation_id,input,execution);
   if(!isCurrent(n))return Object.freeze({kind:'unavailable'});if(result.kind==='saved_locally'||result.kind==='needs_attention'){await local(n,false,ids.capture_id);trigger();}return result;
  },
  more(){
   if(paging)return paging;if(!store||!state.next_key||state.kind!=='ready')return Promise.resolve();
   const saved=store,n=generation,version=viewVersion,key=state.next_key,current=()=>isCurrent(n)&&saved===store&&viewVersion===version&&state.kind==='ready'&&state.next_key===key;
   publish({loadingMore:true});paging=(async()=>{try{
    const next=await saved.workspace({after:key},{isCurrent:current});if(!current())return;
    if(next.kind==='unavailable'){storageUnavailable();return;}
    if(next.kind!=='available'){clear('locked','Online verification is required to open saved work.');return;}
    const seen=new Set(state.records.map(row=>row.capture.capture_id));publish({records:[...state.records,...next.records.filter(row=>!seen.has(row.capture.capture_id))],next_key:next.next_key});
   }finally{paging=undefined;if(isCurrent(n))publish({loadingMore:false});}})();return paging;
  },
  dispose(){if(disposed)return;disposed=true;clearTimeout(authorityTimer);stop();rerun=false;entry?.dispose();store?.close();store=undefined;},
 };
}
