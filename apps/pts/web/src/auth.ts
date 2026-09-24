import {createClient, type AuthChangeEvent, type Session} from '@supabase/supabase-js';
export const configured=Boolean(import.meta.env.VITE_SUPABASE_URL && import.meta.env.VITE_SUPABASE_ANON_KEY);
export const microsoftEnabled=import.meta.env.VITE_MICROSOFT_SIGN_IN_ENABLED==='true';
export type PasswordFlow='invite'|'recovery';
// Capture before Supabase consumes and removes the callback fragment.
const callback=new URLSearchParams(location.hash.slice(1));
const callbackType=callback.get('type');
let pendingFlow:PasswordFlow|null=Boolean(callback.get('access_token'))&&(callbackType==='invite'||callbackType==='recovery')?callbackType:null;
const flowKey='pts-password-flow';
export const auth=createClient(import.meta.env.VITE_SUPABASE_URL || 'https://unconfigured.invalid',import.meta.env.VITE_SUPABASE_ANON_KEY || 'unconfigured',{auth:{storageKey:'pts-auth'}}).auth;
export type Identity={id:string;token:string};
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
 if(code==='over_email_send_rate_limit'||code==='over_request_rate_limit')return 'Too many attempts. Please wait a little and try again.';
 if(action==='login'&&code==='invalid_credentials')return 'Check your email and password, then try again.';
 if(action==='login'&&code==='email_not_confirmed')return 'Confirm your email using your invitation or confirmation link, then sign in.';
 if(action==='password'&&code==='weak_password')return 'Choose a stronger password that meets your organization’s password requirements.';
 if(action==='password'&&code==='same_password')return 'Choose a password different from your current password.';
 if(action==='password'&&(code==='session_not_found'||code==='session_expired'||code==='reauthentication_needed'))return 'Your session has expired. Request a new password reset link.';
 return action==='login'?'We could not sign you in. Please try again.':action==='reset'?'We could not send a reset link. Please try again.':action==='password'?'We could not save your password. Please try again.':'Microsoft sign-in is unavailable. Use email and password or try again.';
}

const returnKey='pts-password-return';
const contextFields=['org','poem','search','availability','source','genre','origin','dialect','status'];
function safeContext(params:URLSearchParams){
 const safe=new URLSearchParams();
 for(const name of contextFields){
  const value=params.get(name);
  if(!value||value.length>300)continue;
  if(name==='org'&&!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value))continue;
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
