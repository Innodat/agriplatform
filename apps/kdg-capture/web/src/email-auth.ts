import {validateKdgEmailAuthConfig} from './auth-public-input.js';
import {createClient,type SupabaseClient} from '@supabase/supabase-js';
import {protectSessionStorage,type SessionStoragePort} from './auth/lifecycle.js';
/** Numeric email codes only; no redirect handling, signup or additional token store. */
export function createKdgEmailAuth(options:Readonly<{url:string;publicKey:string;storage:SessionStoragePort;request?:typeof fetch}>):SupabaseClient['auth'] {
 const {url,publicKey,storage,request=fetch}=options;
 validateKdgEmailAuthConfig({url,publicKey});
 const selected=protectSessionStorage(storage,'kdg-capture-auth');
 const bounded:typeof fetch=(input,init)=>{
  const caller=init?.signal??(input instanceof Request?input.signal:undefined),deadline=AbortSignal.timeout(10000);
  return request(input,{...init,signal:caller?AbortSignal.any([caller,deadline]):deadline});
 };
 return createClient(url,publicKey,{auth:{storageKey:'kdg-capture-auth',storage:selected,persistSession:true,autoRefreshToken:true,flowType:'implicit',detectSessionInUrl:false,debug:false},global:{fetch:bounded}}).auth;
}
