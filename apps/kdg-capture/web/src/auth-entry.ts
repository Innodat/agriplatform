// KDG-owned adapter: shared generated lifecycle, application-owned current admission.
import type {SupabaseClient} from '@supabase/supabase-js';
import {createEntryBoundary, type EntryState, type EntryContext, type Session, getCurrentContext} from './entry.js';
import {createSessionLifecycle,createReturnSelection,createOAuthController,type OAuthStore} from './auth/lifecycle.js';
export type EntryAuth = Pick<SupabaseClient['auth'], 'getSession' | 'onAuthStateChange' | 'refreshSession' | 'signOut'>;
export type AuthEntryOptions = Readonly<{
 org:string;auth:EntryAuth;publish:(state:EntryState)=>void;beginSignIn:()=>Promise<void>;
 request?:typeof fetch;online?:boolean;timeoutMs?:number;
}>;
export function createAuthEntry(options: AuthEntryOptions) {
 const {org,request,...lifecycle}=options;
 return createSessionLifecycle<EntryContext>({...lifecycle,createBoundary:publish=>createEntryBoundary(org,publish,request)});
}

/** Owner adapter for the only implemented return destination. No navigation or storage. */
export function createEntryReturn(options:Readonly<{org:string;request?:typeof fetch;timeoutMs?:number}>) {
 const guard=createReturnSelection({routes:['/'],safePath:'/',timeoutMs:options.timeoutMs});
 return {
  capture(path:unknown,context:EntryContext):boolean {
   if(context.authorization_scope.org_id!==options.org){guard.clear();return false;}
   return guard.capture(path,{account_id:context.account_id,scope_id:options.org});
  },
  restore(session:Session|null) {
   const current=session?{account_id:session.account_id,access_token:session.access_token}:null;
   return guard.restore(async(_path,signal)=>{
    if(!current)return null;
    const result=await getCurrentContext(current,options.org,{request:options.request,timeoutMs:options.timeoutMs,signal});
    return result.kind==='authorized'?{account_id:result.context.account_id,scope_id:result.context.authorization_scope.org_id}:null;
   });
  },
  clear:guard.clear,dispose:guard.dispose,
 };
}

export type EntryOAuthAuth=Pick<SupabaseClient['auth'],'signInWithOAuth'|'exchangeCodeForSession'>;
/** The supplied SDK must explicitly use PKCE and detectSessionInUrl:false. */
export function createEntryOAuth(configuration:Readonly<{
 org:string;auth:EntryOAuthAuth;authorizeUrl:string;callbackUrl:string;
 provider:Parameters<EntryOAuthAuth['signInWithOAuth']>[0]['provider'];scopes:string;
 store:OAuthStore;pause():void;navigate(url:string):void;scrub(url:string):void;
 request?:typeof fetch;timeoutMs?:number;now?:()=>number;
}>) {
 const options=Object.freeze({...configuration});
 return createOAuthController<EntryContext>({...options,
  begin:async()=>{const result=await options.auth.signInWithOAuth({provider:options.provider,options:{redirectTo:options.callbackUrl,scopes:options.scopes,skipBrowserRedirect:true}});return{url:result.data.url,flowId:result.data.flowId??null,error:result.error};},
  exchange:async(code,flowId)=>{const result=await options.auth.exchangeCodeForSession(code,{flowId});return{session:result.data.session,error:result.error};},
  admit:(session,signal)=>getCurrentContext(session,options.org,{request:options.request,signal,timeoutMs:options.timeoutMs}),
 });
}
