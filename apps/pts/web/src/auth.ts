import {createClient, type AuthChangeEvent, type Session} from '@supabase/supabase-js';
import {revokeOriginalSession,type RefreshedCleanupIdentity} from './sessionRevocation';
export const configured=Boolean(import.meta.env.VITE_SUPABASE_URL && import.meta.env.VITE_SUPABASE_ANON_KEY);
export const microsoftEnabled=import.meta.env.VITE_MICROSOFT_SIGN_IN_ENABLED==='true';
export type PasswordFlow='invite'|'recovery';
// Capture before Supabase consumes and removes the callback fragment.
const callback=new URLSearchParams(location.hash.slice(1));
const callbackType=callback.get('type');
let pendingFlow:PasswordFlow|null=Boolean(callback.get('access_token'))&&(callbackType==='invite'||callbackType==='recovery')?callbackType:null;
const flowKey='pts-password-flow';
const authStorageKey='pts-auth';
const superseded=()=>Object.assign(new Error('file_cleanup_superseded'),{code:'file_cleanup_superseded'});
/** Negative operation freshness only; provider evidence still identifies sessions. */
export type AuthCleanupObservation={raw:string|null};
export function observeCleanupAuth():AuthCleanupObservation{return {raw:localStorage.getItem(authStorageKey)};}
export function authCleanupIsCurrent(observation:AuthCleanupObservation){try{return localStorage.getItem(authStorageKey)===observation.raw;}catch{return false;}}
type MutationGuard={observation:AuthCleanupObservation;owner?:AuthCleanupObservation;current:()=>boolean;claimsOnly:boolean;parent?:MutationGuard};
const mutationGuards=new Set<MutationGuard>();
let logoutOwner:{identity:Identity|null;current:()=>boolean;guard:MutationGuard}|null=null;
function requireAuthMutation(guard?:MutationGuard){
 for(const active of guard?[guard]:mutationGuards)if(!active.current()||!authCleanupIsCurrent(active.observation))throw superseded();
}
function recordAuthMutation(raw:string|null){
 // Only this call and its explicitly enclosing SDK operation own the write.
 // An unrelated older call retains its snapshot even with a shared owner.
 const guard=[...mutationGuards].at(-1);
 for(let owner=guard;owner;owner=owner.parent){owner.observation.raw=raw;if(owner.owner)owner.owner.raw=raw;}
}
// The SDK remains the sole session owner. Every still-active negative scope is
// checked so a newer overlapping call cannot hide an obsolete request's guard.
const authStorage={
 getItem:(key:string)=>localStorage.getItem(key),
 setItem(key:string,value:string){if(key===authStorageKey){requireAuthMutation();if([...mutationGuards].some(guard=>guard.claimsOnly))throw superseded();}localStorage.setItem(key,value);if(key===authStorageKey)recordAuthMutation(value);},
 removeItem(key:string){if(key===authStorageKey)requireAuthMutation();localStorage.removeItem(key);if(key===authStorageKey)recordAuthMutation(null);},
};
async function guardedAuthMutation<T>(current:(()=>boolean)|undefined,operation:(guard?:MutationGuard)=>Promise<T>,observation?:AuthCleanupObservation,claimsOnly=false,parent?:MutationGuard):Promise<T>{
 if(!current)return operation();
 if(observation&&!authCleanupIsCurrent(observation))throw superseded();
 const guard={observation:observeCleanupAuth(),owner:observation,current,claimsOnly,parent};requireAuthMutation(guard);
 mutationGuards.add(guard);
 try{const result=await operation(guard);requireAuthMutation(guard);return result;}finally{mutationGuards.delete(guard);}
}
function guardedClaims(token:string,current:()=>boolean=()=>true,observation?:AuthCleanupObservation,parent?:MutationGuard){return guardedAuthMutation(current,()=>auth.getClaims(token),observation,true,parent);}
const authFetch:typeof fetch=async(input,init)=>{
 const deadline=AbortSignal.timeout(15000);
 const caller=init?.signal||(input instanceof Request?input.signal:undefined);
 const owner=logoutOwner,requestUrl=input instanceof Request?input.url:String(input),path=new URL(requestUrl).pathname;
 const profile=path.endsWith('/user')&&(init?.method||(input instanceof Request?input.method:'GET')).toUpperCase()==='GET';
 // Keep the request's physical observation independent of mutable operation
 // handoffs. The SDK may remove storage even for an explicit old-token error.
 const profileObservation=profile?observeCleanupAuth():null;
 if(owner&&new URL(requestUrl).pathname.endsWith('/logout')){
  if(!owner.identity)throw superseded();
  const token=new Headers(init?.headers||(input instanceof Request?input.headers:undefined)).get('Authorization')?.replace(/^Bearer /,'');
  if(!token)throw superseded();
  const {data,error}=await guardedClaims(token,owner.current,owner.guard.owner,owner.guard);
  if(error||data?.claims.sub!==owner.identity.id||data.claims.session_id!==owner.identity.sessionId||!owner.current())throw superseded();
  requireAuthMutation();
 }
 const response=await fetch(input,{...init,signal:caller?AbortSignal.any([caller,deadline]):deadline});
 if(profileObservation){
  if(!authCleanupIsCurrent(profileObservation))throw superseded();
  if(!response.ok&&profileObservation.raw!==null){
   const token=new Headers(init?.headers||(input instanceof Request?input.headers:undefined)).get('Authorization')?.replace(/^Bearer /,'');
   let stored;try{stored=JSON.parse(profileObservation.raw);}catch{throw superseded();}
   if(!token||stored?.access_token!==token)throw superseded();
  }
 }
 if(owner&&new URL(requestUrl).pathname.endsWith('/logout')){if(!owner.current())throw superseded();requireAuthMutation();}
 return response;
};
export const auth=createClient(import.meta.env.VITE_SUPABASE_URL || 'https://unconfigured.invalid',import.meta.env.VITE_SUPABASE_ANON_KEY || 'unconfigured',{auth:{storageKey:authStorageKey,storage:authStorage},global:{fetch:authFetch}}).auth;
let authObservation=0;
/** Observe the existing app subscription even while its UI transition is held. */
export function observeAuthChange(event:AuthChangeEvent){if(event!=='INITIAL_SESSION')authObservation++;}
export type Identity={id:string;token:string;refreshToken?:string;sessionId?:string;revocationToken?:string};
/** Session identity comes from the existing auth owner's verified claims. The
 * callback event and account ID alone cannot distinguish a refresh from login.
 */
export async function verifiedSessionIdentity(session:Session,isCurrent:()=>boolean):Promise<Identity>{
 const {data,error}=await guardedClaims(session.access_token,isCurrent);
 if(!isCurrent())throw new Error('file_cleanup_superseded');
 if(error||data?.claims.sub!==session.user.id||typeof data.claims.session_id!=='string'||!data.claims.session_id)throw new Error('cleanup_session_mismatch');
 return {id:session.user.id,token:session.access_token,refreshToken:session.refresh_token,sessionId:data.claims.session_id};
}
/** Negative local freshness only, never authentication or file authority.
 * Inspect the sole SDK's configured persisted session synchronously. Loading an
 * SDK session here could refresh a short-lived credential and restart preparation.
 * This check can also run inside the final storage-only mutation after queueing.
 */
export function filePreparationIsCurrent(identity:Identity):boolean{
 try{
  const session=JSON.parse(localStorage.getItem(authStorageKey)||'null');
  return session?.user?.id===identity.id&&session.access_token===identity.token&&(identity.refreshToken===undefined||session.refresh_token===identity.refreshToken);
 }catch{return false;}
}
export function clearPasswordFlow(){pendingFlow=null;sessionStorage.removeItem(flowKey);}
export function passwordFlowFor(session:Session|null,event?:AuthChangeEvent):PasswordFlow|null{
 if(event==='SIGNED_OUT'){clearPasswordFlow();return null;}
 if(!session)return null;
 if(event==='PASSWORD_RECOVERY')pendingFlow='recovery';
 if(pendingFlow){
  sessionStorage.setItem(flowKey,JSON.stringify({actor:session.user.id,flow:pendingFlow}));
  pendingFlow=null;
 }
 try{
  const saved=JSON.parse(sessionStorage.getItem(flowKey)||'null');
  if(saved?.actor===session.user.id && (saved.flow==='invite'||saved.flow==='recovery'))return saved.flow;
 }catch{/* Invalid local UI state never establishes a session. */}
 sessionStorage.removeItem(flowKey);return null;
}
export function authError(error:unknown,action:'login'|'reset'|'password'|'oauth'){
 const code=(error as {code?:string})?.code;
 if((error as {name?:string})?.name==='AuthRetryableFetchError'&&(error as {status?:number})?.status===0)return 'We could not reach the sign-in service. Check your connection and try again.';
 if(code==='over_email_send_rate_limit'||code==='over_request_rate_limit')return 'Too many attempts. Please wait a little and try again.';
 if(action==='login'&&code==='invalid_credentials')return 'Check your email and password, then try again.';
 if(action==='login'&&code==='email_not_confirmed')return 'Confirm your email using your invitation or confirmation link, then sign in.';
 if(action==='password'&&code==='weak_password')return 'Choose a stronger password that meets your account’s password requirements.';
 if(action==='password'&&code==='same_password')return 'Choose a password different from your current password.';
 if(action==='password'&&(code==='session_not_found'||code==='session_expired'||code==='reauthentication_needed'))return 'Your session has expired. Request a new password reset link.';
 return action==='login'?'We could not sign you in. Please try again.':action==='reset'?'We could not send a reset link. Please try again.':action==='password'?'We could not save your password. Please try again.':'Microsoft sign-in is unavailable. Use email and password or try again.';
}

const returnKey='pts-password-return';
const contextFields=['view','poem','search','availability','source','genre','origin','dialect','status'];
function safeContext(params:URLSearchParams){
 const safe=new URLSearchParams();
 for(const name of contextFields){
  const value=params.get(name);
  if(!value||value.length>300)continue;
  safe.set(name,value);
 }
 return safe;
}
export function rememberPasswordReturn(){
 const actor=sessionStorage.getItem('pts-last-user');
 if(!actor)return;
 const params=safeContext(new URLSearchParams(location.search));
 try{localStorage.setItem(returnKey,JSON.stringify({actor,query:params.toString(),expires:Date.now()+3600000}));}catch{/* Return context is optional when storage is unavailable. */}
}
export function consumePasswordReturn(actor:string):URLSearchParams|null{
 try{
  const saved=JSON.parse(localStorage.getItem(returnKey)||'null');
  localStorage.removeItem(returnKey);
  if(saved?.actor===actor&&typeof saved.query==='string'&&saved.expires>Date.now())return safeContext(new URLSearchParams(saved.query));
 }catch{/* Invalid saved context never controls a destination or identity. */}
 return null;
}

/** Confirm provider-local revocation before completing file logout/account switch. */
export async function revokeLocalSession(identity:Identity,retain:(original:Identity,refreshed:RefreshedCleanupIdentity)=>Promise<void>=async()=>{},recover=true,isCurrent?:()=>boolean,observation?:AuthCleanupObservation){
 const attempt=async(original:Identity)=>{const {error}=await auth.admin.signOut(original.revocationToken||original.token,'local');if(error)throw error;};
 // A private write failure cannot gate the independent provider attempt. Use
 // only known original credentials; session loading/refresh can rotate a current
 // replacement and is unsafe when its recovery cannot be persisted.
 if(!recover){await attempt(identity);return;}
 let current;
 try{current=await currentOriginalCleanup(identity,retain,isCurrent,observation);}
 catch(error){
  if(['file_cleanup_replacement_unavailable','file_cleanup_superseded'].includes((error as {code?:string})?.code||'')){
   try{await attempt(identity);}catch{/* The stable custody failure stays visible. */}
  }
  throw error;
 }
 if(current?.persistenceError){
  // This token has already been verified as the exact original by the sole auth
  // owner. Preserve its SDK pair, attempt revoke, and never start another refresh
  // after private persistence failed. Local cleanup still has to recover.
  try{await attempt(current.identity);}finally{throw current.persistenceError;}
 }
 const original=current?.identity||identity;
 await revokeOriginalSession(original,{
  async revoke(token){const {error}=await auth.admin.signOut(token,'local');if(error)throw error;},
  async refresh(refresh_token){const {data,error}=await guardedAuthMutation(isCurrent,()=>auth.refreshSession({refresh_token}),observation);if(error)throw error;if(!data.session)throw new Error('cleanup_session_mismatch');return {id:data.session.user.id,token:data.session.access_token,refreshToken:data.session.refresh_token};},
  async claims(token){const {data,error}=await guardedClaims(token,isCurrent,observation);if(error)throw error;if(!data)throw new Error('cleanup_session_mismatch');return data.claims;},
  retain,
 });
}

/** Use the auth owner's current exact original pair before an explicit old refresh.
 * The SDK may rotate storage while loading a session, even for refreshSession(old).
 */
async function currentOriginalCleanup(identity:Identity,retain:(original:Identity,refreshed:RefreshedCleanupIdentity)=>Promise<void>,isCurrent?:()=>boolean,observation?:AuthCleanupObservation):Promise<{identity:Identity;persistenceError?:unknown}|null>{
 if(!identity.sessionId)return null;
  let snapshot;try{snapshot=await guardedAuthMutation(isCurrent,()=>auth.getSession(),observation);}catch(error){
   // A failed awaited replacement observation must keep cleanup pending instead
   // of falling through to successful original revocation and stale restoration.
   if(['file_cleanup_replacement_unavailable','file_cleanup_superseded'].includes((error as {code?:string})?.code||''))throw error;
   return null;
  }
  const session=snapshot.data.session;
  if(snapshot.error||!session||session.user.id!==identity.id)return null;
  const observed=authObservation;
  let verification;try{verification=await guardedClaims(session.access_token,isCurrent,observation);}catch{return null;}
  if(verification.error||verification.data?.claims.sub!==identity.id||verification.data.claims.session_id!==identity.sessionId||observed!==authObservation)return null;
  const current={...identity,revocationToken:session.access_token,refreshToken:session.refresh_token};
  try{await retain(identity,{id:identity.id,token:session.access_token,refreshToken:session.refresh_token});}
  catch(persistenceError){return {identity:current,persistenceError};}
  return {identity:current};
}

/** Finish only this operation's verified original through the existing SDK.
 * Fetch checks protect token selection; storage checks protect SDK removal after
 * its provider await. Neither local observation supplies read authority.
 */
export async function finishOriginalAuthLogout(identity:Identity|null,isCurrent:()=>boolean,observation?:AuthCleanupObservation){
 return guardedAuthMutation(isCurrent,async guard=>{
  let original=identity;
  if(!original&&localStorage.getItem(authStorageKey)!==null)throw superseded();
  // A confirmed previous cleanup may leave no SDK session. Its ordinary retry
  // has no provider token to select, so an expired obsolete token is irrelevant.
  // The operation/storage guards still refuse a newly arriving SDK session.
  const removedMissingSession=(error:unknown)=>(error as {name?:string})?.name==='AuthSessionMissingError'&&localStorage.getItem(authStorageKey)===null;
  const failed=()=>Object.assign(new Error('ordinary_auth_logout_failed'),{code:'ordinary_auth_logout_failed'});
  if(original&&!original.sessionId&&localStorage.getItem(authStorageKey)!==null){
   const {data,error}=await guardedClaims(original.token,isCurrent,observation,guard);
   if(error){if(!removedMissingSession(error))throw error;}
   else{if(data?.claims.sub!==original.id||typeof data.claims.session_id!=='string')throw superseded();original.sessionId=data.claims.session_id;}
  }
  // Observe the sole SDK before its final signOut selects a token. A genuine
  // profile session-missing response removes its own session through the guarded
  // adapter; signOut can then complete normally without a redundant revoked-token
  // request. Other refresh/provider errors retain the ordinary retry contract.
  const snapshot=await auth.getSession();requireAuthMutation(guard);
  if(snapshot.error&&!removedMissingSession(snapshot.error))throw failed();
  if(snapshot.data.session){
   const {data,error}=await guardedClaims(snapshot.data.session.access_token,isCurrent,observation,guard);
   if(error){if(!removedMissingSession(error))throw failed();}
   else if(!original||data?.claims.sub!==original.id||data.claims.session_id!==original.sessionId)throw superseded();
  }
  requireAuthMutation();
  const owner={identity:original,current:isCurrent,guard:guard!};logoutOwner=owner;
  try{const result=await auth.signOut({scope:'local'});if(result.error)throw failed();}
  finally{if(logoutOwner===owner)logoutOwner=null;}
 },observation);
}
export function restoreCleanupSession(identity:Identity,isCurrent:()=>boolean,observation?:AuthCleanupObservation){return guardedAuthMutation(isCurrent,()=>auth.setSession({access_token:identity.token,refresh_token:identity.refreshToken!}),observation);}
/** A retry observes current SDK state without permitting its implicit refresh to
 * overwrite a later tab's session while that observation is awaited. */
export function currentCleanupSession(){return guardedAuthMutation(()=>true,()=>auth.getSession());}

/** Keep existing-owner rotation recoverable while file cleanup remains pending. */
export async function retainCurrentCleanup(identity:Identity,original:Identity,retain:(original:Identity,refreshed:RefreshedCleanupIdentity)=>Promise<void>,isCurrent:()=>boolean){
 if(!identity.refreshToken||!original.sessionId||identity.id!==original.id)return;
 const {data,error}=await guardedClaims(identity.token,isCurrent);
 if(!isCurrent())throw new Error('file_cleanup_superseded');
 if(error||data?.claims.sub!==original.id||data.claims.session_id!==original.sessionId)throw new Error('cleanup_session_mismatch');
 await retain(original,{id:identity.id,token:identity.token,refreshToken:identity.refreshToken});
}
