// Synthetic SDK transport/storage only; no real provider, account or token.
import {mountEmailCode} from './email-code';
import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {createClient} from '@supabase/supabase-js';
import {AuthEntry} from '../../src/AuthEntry';
import {createEntryReturn,createEntryOAuth,type EntryAuth} from '../../src/auth-entry';
import type {OAuthFlow} from '../../src/auth/lifecycle';
import {getCurrentContext} from '../../src/entry';
import '../../src/entry-screen.css';
const A='11111111-1111-4111-8111-111111111111',ORG='33333333-3333-4333-8333-333333333333';
const events:string[]=[],paths:string[]=[],oauthChecks:string[]=[];let holdOAuth=false,oauthInFlight=0,releaseOAuth:(()=>void)|null=null;let online=true,mounted=true,interactive=0,org=ORG,sequence=0;
const base64url=(value:unknown)=>btoa(JSON.stringify(value)).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
const token=(account:string)=>base64url({alg:'HS256',typ:'JWT'})+'.'+base64url({sub:account,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})+'.c3ludGhldGlj';
const sdkSession=(account:string)=>({access_token:token(account),refresh_token:'synthetic-refresh',expires_at:Math.floor(Date.now()/1000)+3600,expires_in:3600,token_type:'bearer',user:{id:account,aud:'authenticated',role:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}});
function makeOwner(account:string){
 let current=account,active=0;const values=new Map<string,string>(),key='kdg-synthetic-auth-'+sequence++;
 values.set(key,JSON.stringify(sdkSession(account)));
 const client=createClient('https://synthetic-auth.invalid','synthetic-public-key',{
  auth:{flowType:'pkce',storageKey:key,storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},autoRefreshToken:false,detectSessionInUrl:false,debug:false},
  global:{fetch:async(input,init)=>{
   const path=new URL(String(input)).pathname;paths.push(path);
   if(path==='/auth/v1/token'&&new URL(String(input)).searchParams.get('grant_type')==='pkce'){
    const body=JSON.parse(String(init?.body));if(!body.code_verifier||!body.auth_code||location.search||location.hash)throw new Error('synthetic_callback_not_scrubbed');
    oauthChecks.push('scrubbed_before_exchange');
    if(holdOAuth){oauthInFlight++;try{await new Promise<void>(resolve=>{releaseOAuth=resolve;});}finally{oauthInFlight--;}}
   }
   if(path==='/auth/v1/token')return new Response(JSON.stringify(sdkSession(current)),{headers:{'content-type':'application/json'}});
   if(path==='/auth/v1/user')return new Response(JSON.stringify(sdkSession(current).user),{headers:{'content-type':'application/json'}});
   if(path==='/auth/v1/logout')return new Response(null,{status:204});throw new Error('unexpected synthetic Auth request');
  }},
 });
 client.auth.onAuthStateChange(event=>{events.push(event);});
 const auth:EntryAuth={
  getSession:()=>client.auth.getSession(),refreshSession:()=>client.auth.refreshSession(),signOut:options=>client.auth.signOut(options),
  onAuthStateChange:callback=>{
   active++;const subscription=client.auth.onAuthStateChange(callback).data.subscription;let closed=false;
   return{data:{subscription:{...subscription,unsubscribe(){if(!closed){closed=true;active--;subscription.unsubscribe();}}}}};
  },
 };
 return{client,auth,active:()=>active,switchAccount:async(account:string)=>{current=account;const result=await client.auth.setSession({access_token:token(account),refresh_token:'synthetic-refresh'});if(result.error)throw new Error('synthetic_set_session_failed');}};
}
let returnGuard=createEntryReturn({org:ORG});
let owner=makeOwner(A);const previous:ReturnType<typeof makeOwner>[]=[];
let oauth:ReturnType<typeof createEntryOAuth>|null=null,pendingOAuth:OAuthFlow|null=null;
function oauthController(){const currentOwner=owner;
 return createEntryOAuth({org,auth:currentOwner.client.auth,authorizeUrl:'https://synthetic-auth.invalid/auth/v1/authorize',callbackUrl:location.origin+'/auth/callback',provider:'azure',scopes:'email',
 store:{read:()=>pendingOAuth,write:value=>{pendingOAuth=value;},take:()=>{const prior=pendingOAuth;pendingOAuth=null;return prior;}},
 pause:()=>{returnGuard.clear();flushSync(()=>{mounted=false;render();});},navigate:()=>{oauthChecks.push('validated_launch');},scrub:url=>{history.replaceState(null,'',url);oauthChecks.push('scrubbed');}});
}
const beginSignIn=async()=>{interactive++;};const root=createRoot(document.getElementById('root')!);
function render(){root.render(<StrictMode>{mounted?<AuthEntry org={org} auth={owner.auth} beginSignIn={beginSignIn} online={online}/>:<p>Entry unmounted</p>}</StrictMode>);}
Object.assign(window,{fixture:{
 holdOAuth:()=>{holdOAuth=true;},releaseOAuth:()=>{holdOAuth=false;releaseOAuth?.();releaseOAuth=null;},
 oauthLaunch:async()=>{oauth?.dispose();oauth=oauthController();return oauth.launch();},
 oauthCallback:async(query:string)=>{oauth?.dispose();oauth=oauthController();history.replaceState(null,'','/auth/callback'+query);const result=await oauth.callback(location.href);
  if(result.kind==='authorized'){history.replaceState(null,'','/');mounted=true;render();}return result.kind;
 },
 captureReturn:async(path:unknown)=>{
  const guard=returnGuard,currentOwner=owner,currentOrg=org;guard.clear();
  const result=await currentOwner.client.auth.getSession(),session=result.data.session;if(!session||currentOwner!==owner||currentOrg!==org)return false;
  const observation=await getCurrentContext({account_id:session.user.id,access_token:session.access_token},currentOrg);
  return currentOwner===owner&&currentOrg===org&&observation.kind==='authorized'&&guard.capture(path,observation.context);
 },
 restoreReturn:async()=>{const result=await owner.client.auth.getSession(),session=result.data.session;return returnGuard.restore(session?{account_id:session.user.id,access_token:session.access_token}:null);},
 refresh:()=>owner.client.auth.refreshSession(),switchAccount:(account:string)=>owner.switchAccount(account),logout:()=>{returnGuard.clear();return owner.client.auth.signOut({scope:'local'});},
 online:(value:boolean)=>{online=value;render();},mount:(value:boolean)=>{mounted=value;render();},
 replaceOwner:(account:string)=>{oauth?.invalidate();oauth?.dispose();oauth=null;pendingOAuth=null;returnGuard.clear();previous.push(owner);owner=makeOwner(account);render();},replaceOrg:(value:string)=>{oauth?.invalidate();oauth?.dispose();oauth=null;pendingOAuth=null;returnGuard.dispose();org=value;returnGuard=createEntryReturn({org});render();},
 oldRefresh:()=>previous.at(-1)?.client.auth.refreshSession(),
 snapshot:()=>({oauthInFlight,oauthChecks:[...oauthChecks],oauthPending:pendingOAuth!==null,events:[...events],paths:[...paths],interactive,active:owner.active(),oldActive:previous.map(p=>p.active())}),
}});if(new URLSearchParams(location.search).has('email-code'))mountEmailCode(root);else render();
