// Owner Microsoft PKCE adapter. No password or app-visible synthetic login.
import {createClient,isAuthApiError,isAuthSessionMissingError,type SupabaseClient} from '@supabase/supabase-js';
import {createSessionLifecycle,protectSessionStorage,createOAuthController,createReturnSelection,type EntryState,type Session,type OAuthFlow,type ExecutionLease} from './auth/lifecycle';
import {createEntryNavigation} from './leave-controller';
import {createLeaveClient,draftId,type Organizations} from './api/leave';
import {fetchProviderResponse} from './auth-provider-transport';
export const leaveClient=createLeaveClient();
export const leaveNavigation=createEntryNavigation();
type DraftOpening=Awaited<ReturnType<typeof leaveClient.editorOpen>>;
type DraftRecoveryStatus='checking'|'unavailable'|'authentication_required';
type DraftRecovery={account:string;org:string;draft:string;complete:(result:DraftOpening)=>void;work?:Promise<void>};
type OpenedDraft=NonNullable<ReturnType<typeof leaveNavigation.openedDraft>>;
type RejectedRefresh={opened:OpenedDraft;expiresAt:number};
export type Snapshot=Readonly<{revision:number;state:EntryState<Organizations>;draftRecovery?:DraftRecoveryStatus}>;
const authStorageKey='leave-auth-v1';
const rejectedCode=(code:unknown)=>typeof code==='string'&&
 ['session_not_found','session_expired','refresh_token_not_found','refresh_token_already_used','bad_jwt'].includes(code);
const credentialRejected=(error:unknown)=>isAuthSessionMissingError(error)||isAuthApiError(error)&&
 rejectedCode(error.code);
export function createLeaveSession(environment:{url?:string;key?:string},storage?:Storage,flowStorage?:Storage){
 let sdk:SupabaseClient|null=null,lifecycle:ReturnType<typeof createSessionLifecycle<Organizations>>|null=null;
 let provider:AbortController|null=null,boundary:AbortController|null=null,revision=0;
 let refreshProvider:AbortController|null=null,refreshWork:ReturnType<SupabaseClient['auth']['refreshSession']>|null=null;
 let disposed=false,departedForOAuth=false;
 let draftRecovery:DraftRecovery|null=null;
 let rejectedRefresh:RejectedRefresh|null=null,locallyRemoved:OpenedDraft|null=null,passivePrompt=false;
 let removedDuringRenewal=false;
 let snapshot:Snapshot=Object.freeze({revision,state:{kind:'checking' as const}});
 const listeners=new Set<()=>void>();
 const clearPriorScope=()=>{
  const previous=leaveNavigation.returnIntent();
  if(previous){
   const scope='/organizations/'+previous.scope_id;
   if(location.pathname===scope||location.pathname.startsWith(scope+'/'))history.replaceState(null,'','/');
  }
  leaveNavigation.clear();
 };
 const notify=()=>{for(const listener of listeners)listener();};
 const publish=(state:EntryState<Organizations>)=>{
  if(draftRecovery){
   if(state.kind==='authorized'){
    const lease=lifecycle?.acquireExecution();
    const sameScope=lease?.session.account_id===draftRecovery.account&&
     state.context.organizations.some(org=>org.org_id===draftRecovery?.org);
    lease?.release();
    if(sameScope)return;
    clearPriorScope();
   }else if(state.kind!=='signed_out'&&state.kind!=='access_denied')return;
   draftRecovery=null;
   provider?.abort();
   refreshProvider?.abort();
  }
  if(state.kind==='authentication_required')leaveNavigation.suspend();
  if(state.kind==='access_denied'||state.kind==='signed_out')clearPriorScope();
  snapshot=Object.freeze({revision:++revision,state,...(passivePrompt&&state.kind==='authentication_required'?{draftRecovery:'authentication_required' as const}:{})});
  notify();
 };
 const showRecovery=(kind:DraftRecoveryStatus)=>{
  snapshot=Object.freeze({...snapshot,draftRecovery:kind});
  notify();
 };
 const returns=createReturnSelection({routes:['/'],safePath:'/'});
 const admit=async(session:Session,signal:AbortSignal):Promise<EntryState<Organizations>>=>{
  const result=await leaveClient.organizations(session.access_token,signal);
  if(result.ok)return{kind:'authorized',context:result.value};
  const kind=result.error_id==='authentication_required'?'authentication_required':['access_denied','service_access_denied','identity.verification_required'].includes(result.error_id)?'access_denied':result.error_id==='cancelled'?'cancelled':'authorization_unavailable';
  return{kind};
 };
 const stop=(preserveReturn=false)=>{lifecycle?.dispose();lifecycle=null;boundary?.abort();provider?.abort();publish({kind:preserveReturn?'checking':'signed_out'});};
 const startLifecycle=()=>{
  if(!sdk||disposed)return null;
  if(lifecycle)return lifecycle;
  const auth=sdk.auth;
  lifecycle=createSessionLifecycle<Organizations>({auth:{
   getSession:()=>auth.getSession(),onAuthStateChange:callback=>auth.onAuthStateChange((event,session)=>{
    const expired=event==='SIGNED_OUT'&&locallyRemoved&&locallyRemoved===leaveNavigation.openedDraft(location);
    const opened=locallyRemoved;
    const renewalRemoval=event==='SIGNED_OUT'&&removedDuringRenewal;
    rejectedRefresh=null;locallyRemoved=null;removedDuringRenewal=false;
    if(renewalRemoval)callback('RENEWAL_SESSION_REMOVED',null);
    else if(expired&&opened){
     leaveNavigation.suspend(opened.draft);
     passivePrompt=true;
     try{callback('SESSION_EXPIRED',null);}finally{passivePrompt=false;}
    }else{
     if(event==='SIGNED_OUT'&&snapshot.state.kind==='authentication_required'&&snapshot.draftRecovery)publish({kind:'signed_out'});
     callback(event,session);
    }
   }),
   signOut:options=>auth.signOut(options),
   refreshSession:()=>{
    if(refreshWork)return refreshWork;
    const execution=new AbortController();
    refreshProvider=execution;
    const deadline=setTimeout(()=>execution.abort(),9000);
    // Keep the refresh transport aborted until the SDK itself stops retrying.
    // A lifecycle timeout by itself does not settle the SDK's refresh promise.
    refreshWork=auth.refreshSession().finally(()=>{
     clearTimeout(deadline);execution.abort();refreshProvider=null;refreshWork=null;
    });
    return refreshWork;
   },
  },publish,beginSignIn:async()=>{},createBoundary:()=>({clear(){boundary?.abort();boundary=null;},dispose(){boundary?.abort();boundary=null;},async check(session){if(!session)return{kind:'signed_out'};boundary=new AbortController();return admit(session,boundary.signal);}})});
  return lifecycle;
 };
 async function renewDraft(attempt:DraftRecovery){
  const current=startLifecycle();if(!current)return;
  showRecovery('checking');
  await current.renew(attempt.account,credentialRejected);
  if(draftRecovery!==attempt)return;
  const state=current.state();
  if(state.kind==='authentication_required'){showRecovery('authentication_required');return;}
  if(state.kind!=='authorized'){showRecovery('unavailable');return;}
  const lease=current.acquireExecution();
  if(!lease){showRecovery('unavailable');return;}
  let result:DraftOpening;
  try{
   if(lease.session.account_id!==attempt.account||!lease.context.organizations.some(org=>org.org_id===attempt.org)){
    draftRecovery=null;clearPriorScope();publish(state);return;
   }
   result=await leaveClient.editorOpen(lease.session.access_token,lease.signal,attempt.org,attempt.draft);
   if(draftRecovery!==attempt)return;
   if(!lease.isCurrent()){showRecovery('unavailable');return;}
  }finally{lease.release();}
  if(!result.ok&&result.error_id==='authentication_required'){showRecovery('authentication_required');return;}
  if(!result.ok&&!['access_denied','identity.verification_required','resource_not_found','leave.setup_required'].includes(result.error_id)){
   showRecovery('unavailable');return;
  }
  draftRecovery=null;
  // Keep the current editor generation alive only after fresh account,
  // organization and draft checks. Its controller owns unsaved memory.
  attempt.complete(result);
  snapshot=Object.freeze({revision:snapshot.revision,state});notify();
 }
 const retryDraft=(attempt:DraftRecovery)=>attempt.work??=renewDraft(attempt)
  .catch(()=>{if(draftRecovery===attempt)showRecovery('unavailable');})
  .finally(()=>{attempt.work=undefined;});
 let oauth:ReturnType<typeof createOAuthController<Organizations>>|null=null;
 let configureOAuth:((selectAccount:boolean)=>void)|null=null;
 let signingIn:Promise<void>|null=null,starting:Promise<void>|null=null,callbackActive=false,callbackReturn:unknown=null;
 try{
  const url=new URL(environment.url??'');
  if(!environment.url||!environment.key||environment.key.trim()!==environment.key||url.username||url.password||url.search||url.hash||url.pathname!=='/'||!(url.protocol==='https:'||url.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(url.hostname)))throw Error();
  const authStorage=protectSessionStorage(storage??globalThis.localStorage,authStorageKey);
  const expiryOf=(draft:OpenedDraft):number|null=>{
   try{
    const value=JSON.parse(authStorage.getItem(authStorageKey)??'null');
    return value?.user?.id===draft.account&&typeof value.expires_at==='number'&&Number.isFinite(value.expires_at)?value.expires_at:null;
   }catch{return null;}
  };
  sdk=createClient(url.origin,environment.key,{global:{fetch:async(input,init)=>{
   const target=new URL(input instanceof Request?input.url:input,url.origin);
   const refresh=target.origin===url.origin&&target.pathname==='/auth/v1/token'&&target.searchParams.get('grant_type')==='refresh_token';
   const scoped=refresh&&refreshProvider?refreshProvider:provider;
   if(scoped)return fetchProviderResponse(fetch,input,init,scoped.signal);
   const opened=refresh&&!draftRecovery?leaveNavigation.openedDraft(location):null;
   const lease=opened?lifecycle?.acquireExecution():null;
   const watching=opened&&lease?.session.account_id===opened.account;
   lease?.release();
   const expiresAt=watching?expiryOf(opened):null;
   if(expiresAt===null||!opened)return fetch(input,init);
   const response=await fetchProviderResponse(fetch,input,init,AbortSignal.timeout(9000));
   // Only an expired session rejected by this document's own refresh can
   // qualify when the SDK subsequently removes that same local session.
   if([400,401,403].includes(response.status)&&expiresAt*1000<=Date.now()){
    try{
     const error=await response.clone().json();
     const version=response.headers.get('X-Supabase-Api-Version');
     const modern=version&&/^2\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(version)&&version>='2024-01-01';
     if(rejectedCode(modern?error.code:error.error_code)&&opened===leaveNavigation.openedDraft(location)&&expiryOf(opened)===expiresAt){
      rejectedRefresh={opened,expiresAt};
     }
    }catch{/* Let the SDK classify an unusable response. */}
   }
   return response;
  }},auth:{flowType:'pkce',detectSessionInUrl:false,storageKey:authStorageKey,storage:{
   getItem:key=>authStorage.getItem(key),
   setItem(key,value){
    if(key===authStorageKey){rejectedRefresh=null;locallyRemoved=null;removedDuringRenewal=false;}
    authStorage.setItem(key,value);
   },
   removeItem(key){
    if(key!==authStorageKey){authStorage.removeItem(key);return;}
    const rejected=rejectedRefresh;
    rejectedRefresh=null;locallyRemoved=null;removedDuringRenewal=false;
    const opened=rejected?.opened;
    const owned=opened&&opened===leaveNavigation.openedDraft(location)&&rejected.expiresAt===expiryOf(opened);
    authStorage.removeItem(key);
    if(owned)locallyRemoved=opened;
    removedDuringRenewal=Boolean(draftRecovery&&refreshProvider&&!refreshProvider.signal.aborted);
   },
  },persistSession:true,autoRefreshToken:true}});
  const fs=flowStorage??globalThis.sessionStorage,key='leave.oauth.v1';
  // Return identity travels only inside this tab's one-use OAuth transaction.
  // It is a navigation hint: the neutral guard and current account/scope must
  // validate it after the callback before a new audited selection can run.
  const stored=():unknown=>{const raw=fs.getItem(key);return raw?JSON.parse(raw):null;};
  const flowOnly=(raw:unknown):unknown=>{if(!raw||typeof raw!=='object'||Array.isArray(raw))return raw;const {return_intent:_,...flow}=raw as Record<string,unknown>;return flow;};
  const store={read(){return flowOnly(stored());},write(flow:OAuthFlow){const intent=leaveNavigation.returnIntent();fs.setItem(key,JSON.stringify({...flow,...(intent?{return_intent:intent}:{})}));},take(){const raw=stored();fs.removeItem(key);callbackReturn=raw&&typeof raw==='object'&&!Array.isArray(raw)?(raw as Record<string,unknown>).return_intent:null;return flowOnly(raw);}};
  const callbackUrl=globalThis.location.origin+'/auth/callback';
  const authorizeUrl=url.origin+'/auth/v1/authorize';
  configureOAuth=selectAccount=>{
   const prompt=selectAccount?'select_account':undefined;
   oauth=createOAuthController<Organizations>({authorizeUrl,callbackUrl,provider:'azure',scopes:'email',prompt,store,pause:()=>{leaveNavigation.suspend();stop(true);},navigate:url=>{globalThis.location.assign(url);departedForOAuth=true;},scrub:()=>globalThis.history.replaceState(null,'','/'),
    begin:async()=>{const execution=new AbortController();provider=execution;const deadline=setTimeout(()=>execution.abort(),9000);try{const result=await sdk!.auth.signInWithOAuth({provider:'azure',options:{redirectTo:callbackUrl,scopes:'email',...(prompt?{queryParams:{prompt}}:{}),skipBrowserRedirect:true}});return{url:result.data.url,flowId:result.data.flowId??null,error:result.error};}finally{clearTimeout(deadline);execution.abort();if(provider===execution)provider=null;}},
    exchange:async(code,flowId)=>{const execution=new AbortController();provider=execution;const deadline=setTimeout(()=>execution.abort(),9000);try{const result=await sdk!.auth.exchangeCodeForSession(code,{flowId});return{session:result.data.session,error:result.error};}finally{clearTimeout(deadline);execution.abort();if(provider===execution)provider=null;}},admit});
  };
  // The pending binding selects one of two fixed policies, never arbitrary URL
  // parameters. The controller still validates/consumes the whole transaction.
  let selectedAccountFlow=false;
  if(globalThis.location.pathname==='/auth/callback'){
   try{selectedAccountFlow=(store.read() as Partial<OAuthFlow>|null)?.binding===JSON.stringify([authorizeUrl,callbackUrl,'azure','email','select_account']);}catch{/* Callback guard scrubs and refuses broken storage. */}
  }
  configureOAuth(selectedAccountFlow);
 }catch{sdk=null;publish({kind:'invalid_response'});}
 // Browser Back can resume this paused heap without mounting App again. Start
 // fresh session/admission work; never republish the cached protected context.
 const onPageShow=(event:PageTransitionEvent)=>{
  if(!event.persisted||!departedForOAuth||disposed||callbackActive)return;
  departedForOAuth=false;starting=null;void startLifecycle()?.start();
 };
 globalThis.addEventListener('pageshow',onPageShow);
 return{
  configured:!!sdk,subscribe:(f:()=>void)=>{listeners.add(f);return()=>{listeners.delete(f);};},snapshot:()=>snapshot,
  start(){
   if(starting)return starting;
   starting=(async()=>{
   if(globalThis.location.pathname==='/auth/callback'){
    callbackActive=true;
    try{
     publish({kind:'checking'});const result=await oauth?.callback(globalThis.location.href);
     if(result?.kind==='authorized'){leaveNavigation.resume(callbackReturn);callbackReturn=null;await startLifecycle()?.start();}
     else {callbackReturn=null;leaveNavigation.clear();publish({kind:result?.kind==='authentication_required'?'authentication_required':'invalid_response'});}
    }finally{callbackActive=false;}
   }else await startLifecycle()?.start();
   })();return starting;
  },
  signIn(selectAccount=false){
   if(disposed)return Promise.resolve();
   if(signingIn)return signingIn;if(callbackActive)return Promise.resolve();
   // A new explicit attempt supersedes abandoned/expired owner flow state.
   // Calls during this attempt share its promise; callback execution stays exclusive.
   if(draftRecovery){
    if(snapshot.draftRecovery!=='authentication_required')return Promise.resolve();
    leaveNavigation.suspend(draftRecovery.draft);draftRecovery=null;refreshProvider?.abort();
   }
   oauth?.invalidate();oauth?.dispose();configureOAuth?.(selectAccount);callbackReturn=null;
   signingIn=(async()=>{const result=await oauth?.launch();if(result&&result.kind!=='launched'&&result.kind!=='authorized')publish({kind:result.kind==='authentication_required'?'authentication_required':'authorization_unavailable'});})().finally(()=>{signingIn=null;});
   return signingIn;
  },
  recoverDraft(org:string,draft:string,complete:DraftRecovery['complete'],renew=true){
   if(disposed||draftRecovery||!draftId(draft))return;
   const intent=leaveNavigation.returnIntent(),lease=lifecycle?.acquireExecution();
   if(!lease)return;
   try{
    if(!intent||intent.scope_id!==org||intent.account_id!==lease.session.account_id)return;
    draftRecovery={account:lease.session.account_id,org,draft,complete};
    if(renew)void retryDraft(draftRecovery);
    else showRecovery('authentication_required');
   }finally{lease.release();}
  },
  retry:()=>draftRecovery?retryDraft(draftRecovery):startLifecycle()?.retry(),
  acquire:():ExecutionLease<Organizations>|null=>draftRecovery?null:lifecycle?.acquireExecution()??null,
  captureReturn(org:string){const lease=lifecycle?.acquireExecution();if(!lease)return;try{returns.capture('/',{account_id:lease.session.account_id,scope_id:org});}finally{lease.release();}},
  async restoreReturn(org:string){const lease=lifecycle?.acquireExecution();if(!lease)return false;try{return(await returns.restore(async()=>{const result=await leaveClient.organizations(lease.session.access_token,lease.signal);return result.ok&&result.value.organizations.some(o=>o.org_id===org)?{account_id:lease.session.account_id,scope_id:org}:null;})).kind==='restored';}finally{lease.release();}},
  async signOut(){draftRecovery=null;rejectedRefresh=null;locallyRemoved=null;removedDuringRenewal=false;clearPriorScope();returns.clear();oauth?.invalidate();provider?.abort();refreshProvider?.abort();await startLifecycle()?.signOut();},
  dispose(){disposed=true;draftRecovery=null;refreshProvider?.abort();globalThis.removeEventListener('pageshow',onPageShow);stop();returns.dispose();oauth?.dispose();listeners.clear();},
 };
}
export const leaveSession=createLeaveSession({url:import.meta.env.VITE_LEAVE_AUTH_URL,key:import.meta.env.VITE_LEAVE_AUTH_ANON_KEY});
