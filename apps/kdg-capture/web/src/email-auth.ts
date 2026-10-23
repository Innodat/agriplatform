import {createClient,type SupabaseClient} from '@supabase/supabase-js';
import {protectSessionStorage,type SessionStoragePort} from './auth/lifecycle.js';
/** Numeric email codes only; no redirect handling, signup or additional token store. */
export function createKdgEmailAuth(options:Readonly<{url:string;publicKey:string;storage:SessionStoragePort;request?:typeof fetch}>):SupabaseClient['auth'] {
 const {url,publicKey,storage,request=fetch}=options;
 try{
  const parsed=new URL(url);
  if(parsed.username||parsed.password||parsed.pathname!=='/'||parsed.search||parsed.hash||!(parsed.protocol==='https:'||(parsed.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(parsed.hostname))))throw new Error();
  let publicOnly=/^sb_publishable_[A-Za-z0-9_-]{10,}$/.test(publicKey);
  if(!publicOnly){const parts=publicKey.split('.');publicOnly=parts.length===3&&JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/'))).role==='anon';}
  if(!publicOnly)throw new Error();
 }catch{throw new Error('auth_configuration_invalid');}
 const selected=protectSessionStorage(storage,'kdg-capture-auth');
 const bounded:typeof fetch=(input,init)=>{
  const caller=init?.signal??(input instanceof Request?input.signal:undefined),deadline=AbortSignal.timeout(10000);
  return request(input,{...init,signal:caller?AbortSignal.any([caller,deadline]):deadline});
 };
 return createClient(url,publicKey,{auth:{storageKey:'kdg-capture-auth',storage:selected,persistSession:true,autoRefreshToken:true,flowType:'implicit',detectSessionInUrl:false,debug:false},global:{fetch:bounded}}).auth;
}
