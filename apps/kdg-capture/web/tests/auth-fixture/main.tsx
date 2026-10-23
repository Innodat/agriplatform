// Synthetic SDK transport/storage only; no real provider, account or token.
import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {createClient} from '@supabase/supabase-js';
import {AuthEntry} from '../../src/AuthEntry';
import type {EntryAuth} from '../../src/auth-entry';
import '../../src/entry-screen.css';
const A='11111111-1111-4111-8111-111111111111',ORG='33333333-3333-4333-8333-333333333333';
const events:string[]=[],paths:string[]=[];let online=true,mounted=true,interactive=0,org=ORG,sequence=0;
const base64url=(value:unknown)=>btoa(JSON.stringify(value)).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
const token=(account:string)=>base64url({alg:'HS256',typ:'JWT'})+'.'+base64url({sub:account,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})+'.c3ludGhldGlj';
const sdkSession=(account:string)=>({access_token:token(account),refresh_token:'synthetic-refresh',expires_at:Math.floor(Date.now()/1000)+3600,expires_in:3600,token_type:'bearer',user:{id:account,aud:'authenticated',role:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}});
function makeOwner(account:string){
 let current=account,active=0;const values=new Map<string,string>(),key='kdg-synthetic-auth-'+sequence++;
 values.set(key,JSON.stringify(sdkSession(account)));
 const client=createClient('https://synthetic-auth.invalid','synthetic-public-key',{
  auth:{storageKey:key,storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},autoRefreshToken:false,detectSessionInUrl:false,debug:false},
  global:{fetch:async(input)=>{
   const path=new URL(String(input)).pathname;paths.push(path);
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
let owner=makeOwner(A);const previous:ReturnType<typeof makeOwner>[]=[];
const beginSignIn=async()=>{interactive++;};const root=createRoot(document.getElementById('root')!);
function render(){root.render(<StrictMode>{mounted?<AuthEntry org={org} auth={owner.auth} beginSignIn={beginSignIn} online={online}/>:<p>Entry unmounted</p>}</StrictMode>);}
Object.assign(window,{fixture:{
 refresh:()=>owner.client.auth.refreshSession(),switchAccount:(account:string)=>owner.switchAccount(account),logout:()=>owner.client.auth.signOut({scope:'local'}),
 online:(value:boolean)=>{online=value;render();},mount:(value:boolean)=>{mounted=value;render();},
 replaceOwner:(account:string)=>{previous.push(owner);owner=makeOwner(account);render();},replaceOrg:(value:string)=>{org=value;render();},
 oldRefresh:()=>previous.at(-1)?.client.auth.refreshSession(),
 snapshot:()=>({events:[...events],paths:[...paths],interactive,active:owner.active(),oldActive:previous.map(p=>p.active())}),
}});render();
