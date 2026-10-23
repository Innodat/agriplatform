import {GoTrueClient} from '@supabase/auth-js';
// Explicit owner mount, actual SDK with injected synthetic transport only.
import type {Root} from 'react-dom/client';
import {mountKdgLocalEntry} from '../../src/LocalEntryRoute';
const A='11111111-1111-4111-8111-111111111111',ORG='33333333-3333-4333-8333-333333333333';
const b64=(v:unknown)=>btoa(JSON.stringify(v)).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
export function mountLocalEntry(root:Root){
 const scenario=new URLSearchParams(location.search).get('scenario');
 if(scenario==='offline')Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});
 const refreshCalls:string[]=[],events:string[]=[];
 for(const name of ['startAutoRefresh','stopAutoRefresh'] as const){const original=GoTrueClient.prototype[name];GoTrueClient.prototype[name]=function(this:GoTrueClient){refreshCalls.push(name);return original.call(this);};}
 if(new URLSearchParams(location.search).has('local-entry'))history.replaceState(null,'',scenario==='callback'?'/auth/callback?code=PRIVATE#access_token=PRIVATE':'/');
 let reads=0,writes=0,hold=false,inFlight=0,release:(()=>void)|undefined;
 const paths:string[]=[],listeners=new Map<string,()=>void>();
 const browser={location,navigator,history,localStorage,addEventListener:(name:string,fn:()=>void)=>{const wrapped=()=>{events.push(name);fn();};listeners.set(name,wrapped);window.addEventListener(name,wrapped);},removeEventListener:(name:string,_fn:()=>void)=>{const wrapped=listeners.get(name);if(wrapped)window.removeEventListener(name,wrapped);listeners.delete(name);}};
 const mounted=mountKdgLocalEntry(root,{browser,org:scenario==='bad-org'?'PRIVATE':ORG,url:scenario==='bad-url'?'http://private.example.invalid':'https://synthetic-auth.invalid',publicKey:scenario==='bad-key'?'sb_secret_PRIVATE':'sb_publishable_synthetic_public_123456',
  storage:{getItem:k=>{reads++;return localStorage.getItem(k);},setItem:(k,v)=>{writes++;if(scenario==='storage')throw Error('PRIVATE');localStorage.setItem(k,v);},removeItem:k=>localStorage.removeItem(k)},
  authRequest:async(input,init)=>{
   const path=new URL(String(input)).pathname;paths.push(path);
   if(path==='/auth/v1/otp'){const body=JSON.parse(String(init?.body));if(body.create_user!==false)throw Error('invalid_synthetic_request');return new Response('{}',{headers:{'content-type':'application/json'}});}
   if(path==='/auth/v1/verify'){
    const body=JSON.parse(String(init?.body));if(body.type!=='email'||body.token!=='123456'||body.email!=='facilitator@example.invalid')throw Error('invalid_synthetic_verify');
    if(hold){inFlight++;try{await new Promise<void>(resolve=>{release=resolve;});}finally{inFlight--;}}
    const token=b64({alg:'HS256',typ:'JWT'})+'.'+b64({sub:A,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})+'.c3ludGhldGlj';
    return new Response(JSON.stringify({access_token:token,refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:A,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}),{headers:{'content-type':'application/json'}});
   }
   throw Error('unexpected_synthetic_path');
  },
 });
 Object.assign(window,{localEntryFixture:{hold:()=>{hold=true;},release:()=>{hold=false;release?.();},dispose:()=>mounted.dispose(),snapshot:()=>({reads,writes,paths:[...paths],inFlight,listeners:listeners.size,events:[...events],refreshCalls:[...refreshCalls]})}});
}
