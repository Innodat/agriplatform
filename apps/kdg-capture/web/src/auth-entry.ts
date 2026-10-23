// KDG-owned adapter: shared generated lifecycle, application-owned current admission.
import type {SupabaseClient} from '@supabase/supabase-js';
import {createEntryBoundary, type EntryState, type EntryContext} from './entry.js';
import {createSessionLifecycle} from './auth/lifecycle.js';
export type EntryAuth = Pick<SupabaseClient['auth'], 'getSession' | 'onAuthStateChange' | 'refreshSession' | 'signOut'>;
export type AuthEntryOptions = Readonly<{
 org:string;auth:EntryAuth;publish:(state:EntryState)=>void;beginSignIn:()=>Promise<void>;
 request?:typeof fetch;online?:boolean;timeoutMs?:number;
}>;
export function createAuthEntry(options: AuthEntryOptions) {
 const {org,request,...lifecycle}=options;
 return createSessionLifecycle<EntryContext>({...lifecycle,createBoundary:publish=>createEntryBoundary(org,publish,request)});
}
