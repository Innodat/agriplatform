// Owner Microsoft PKCE adapter. No password or app-visible synthetic login.
import {createClient,type SupabaseClient} from '@supabase/supabase-js';
import {createSessionLifecycle,protectSessionStorage,createOAuthController,createReturnSelection,type EntryState,type Session,type OAuthFlow,type ExecutionLease} from './auth/lifecycle';
import {createEntryNavigation} from './leave-controller';
import {createLeaveClient,type Organizations} from './api/leave';
import {fetchProviderResponse} from './auth-provider-transport';
export const leaveClient=createLeaveClient();
export const leaveNavigation=createEntryNavigation();
export type Snapshot=Readonly<{revision:number;state:EntryState<Organizations>}>;
export function createLeaveSession(environment:{url?:string;key?:string},storage?:Storage,flowStorage?:Storage){
 let sdk:SupabaseClient|null=null,lifecycle:ReturnType<typeof createSessionLifecycle<Organizations>>|null=null;
 let provider:AbortController|null=null,boundary:AbortController|null=null,revision=0;
 let disposed=false,departedForOAuth=false;
 let snapshot:Snapshot=Object.freeze({revision,state:{kind:'checking' as const}});
 const listeners=new Set<()=>void>();
 const publish=(state:EntryState<Organizations>)=>{if(state.kind==='authentication_required')leaveNavigation.suspend();if(state.kind==='access_denied'||state.kind==='signed_out')leaveNavigation.clear();snapshot=Object.freeze({revision:++revision,state});for(const notify of listeners)notify();};
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
  lifecycle=createSessionLifecycle<Organizations>({auth:sdk.auth,publish,beginSignIn:async()=>{},createBoundary:()=>({clear(){boundary?.abort();boundary=null;},dispose(){boundary?.abort();boundary=null;},async check(session){if(!session)return{kind:'signed_out'};boundary=new AbortController();return admit(session,boundary.signal);}})});
  return lifecycle;
 };
 let oauth:ReturnType<typeof createOAuthController<Organizations>>|null=null;
 let configureOAuth:((selectAccount:boolean)=>void)|null=null;
 let signingIn:Promise<void>|null=null,starting:Promise<void>|null=null,callbackActive=false,callbackReturn:unknown=null;
 try{
  const url=new URL(environment.url??'');
  if(!environment.url||!environment.key||environment.key.trim()!==environment.key||url.username||url.password||url.search||url.hash||url.pathname!=='/'||!(url.protocol==='https:'||url.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(url.hostname)))throw Error();
  sdk=createClient(url.origin,environment.key,{global:{fetch:(input,init)=>provider?fetchProviderResponse(fetch,input,init,provider.signal):fetch(input,init)},auth:{flowType:'pkce',detectSessionInUrl:false,storageKey:'leave-auth-v1',storage:protectSessionStorage(storage??globalThis.localStorage,'leave-auth-v1'),persistSession:true,autoRefreshToken:true}});
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
   oauth?.invalidate();oauth?.dispose();configureOAuth?.(selectAccount);callbackReturn=null;
   signingIn=(async()=>{const result=await oauth?.launch();if(result&&result.kind!=='launched'&&result.kind!=='authorized')publish({kind:result.kind==='authentication_required'?'authentication_required':'authorization_unavailable'});})().finally(()=>{signingIn=null;});
   return signingIn;
  },
  retry:()=>startLifecycle()?.retry(),
  acquire:():ExecutionLease<Organizations>|null=>lifecycle?.acquireExecution()??null,
  captureReturn(org:string){const lease=lifecycle?.acquireExecution();if(!lease)return;try{returns.capture('/',{account_id:lease.session.account_id,scope_id:org});}finally{lease.release();}},
  async restoreReturn(org:string){const lease=lifecycle?.acquireExecution();if(!lease)return false;try{return(await returns.restore(async()=>{const result=await leaveClient.organizations(lease.session.access_token,lease.signal);return result.ok&&result.value.organizations.some(o=>o.org_id===org)?{account_id:lease.session.account_id,scope_id:org}:null;})).kind==='restored';}finally{lease.release();}},
  async signOut(){leaveNavigation.clear();returns.clear();oauth?.invalidate();provider?.abort();await startLifecycle()?.signOut();},
  dispose(){disposed=true;globalThis.removeEventListener('pageshow',onPageShow);stop();returns.dispose();oauth?.dispose();listeners.clear();},
 };
}
export const leaveSession=createLeaveSession({url:import.meta.env.VITE_LEAVE_AUTH_URL,key:import.meta.env.VITE_LEAVE_AUTH_ANON_KEY});
