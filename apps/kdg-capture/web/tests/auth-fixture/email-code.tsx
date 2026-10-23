// Synthetic numeric-code transport; no real email/account/service request.
import type {Root} from 'react-dom/client';
import {StrictMode} from 'react';
import {EmailCodeEntry} from '../../src/EmailCodeEntry';
import {createKdgEmailAuth} from '../../src/email-auth';
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';
const paths:string[]=[];let online=true;let hold=false,inFlight=0,release:(()=>void)|null=null;
const base64url=(value:unknown)=>btoa(JSON.stringify(value)).replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
const token=(account:string)=>base64url({alg:'HS256',typ:'JWT'})+'.'+base64url({sub:account,exp:Math.floor(Date.now()/1000)+3600,aud:'authenticated'})+'.c3ludGhldGlj';
export function mountEmailCode(root:Root){
 let org=ORG;
 const makeAuth=(account:string,storage:Storage|{getItem(k:string):string|null;setItem(k:string,v:string):void;removeItem(k:string):void})=>createKdgEmailAuth({url:'https://synthetic-auth.invalid',publicKey:'sb_publishable_synthetic_public_123456',storage,request:async(input,init)=>{
  const url=new URL(String(input)),path=url.pathname;paths.push(path);
  if(url.origin!=='https://synthetic-auth.invalid')throw new Error('unexpected_synthetic_auth_origin');
  const body=init?.body?JSON.parse(String(init.body)):null;
  if(path==='/auth/v1/otp'){
   if(body.create_user!==false||body.code_challenge!==null)throw new Error('invalid_synthetic_otp_request');
   return new Response('{}',{headers:{'content-type':'application/json'}});
  }
  if(path==='/auth/v1/verify'){
   if(body.type!=='email'||body.email!=='facilitator@example.invalid')throw new Error('invalid_synthetic_verify_request');
   if(body.token!=='123456')return new Response(JSON.stringify({code:'otp_expired',msg:'PRIVATE'}),{status:403,headers:{'content-type':'application/json','X-Supabase-Api-Version':'2024-01-01'}});
   if(hold&&account===A){inFlight++;try{await new Promise<void>(resolve=>{release=resolve;});}finally{inFlight--;}}
   return new Response(JSON.stringify({access_token:token(account),refresh_token:'synthetic-refresh',expires_in:3600,token_type:'bearer',user:{id:account,aud:'authenticated',app_metadata:{},user_metadata:{},created_at:'2026-10-23T10:00:00Z'}}),{headers:{'content-type':'application/json'}});
  }
  if(path==='/auth/v1/logout')return new Response(null,{status:204});
  throw new Error('unexpected_synthetic_auth_path');
 }});
 let auth=makeAuth(A,localStorage);
 const render=()=>root.render(<StrictMode><EmailCodeEntry org={org} auth={auth} online={online}/></StrictMode>);
 Object.assign(window,{emailFixture:{replaceOrg:(value:string)=>{org=value;render();},replaceOwner:()=>{const values=new Map<string,string>();auth=makeAuth(B,{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}});render();},online:(value:boolean)=>{online=value;render();},holdVerify:()=>{hold=true;},releaseVerify:()=>{hold=false;release?.();release=null;},session:async()=>{const result=await auth.getSession();return result.data.session?.user.id??null;},logout:()=>auth.signOut({scope:'local'}),snapshot:()=>({inFlight,paths:[...paths],storageKeys:Object.keys(localStorage)})}});
 render();
}
