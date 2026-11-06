// Owner transition controller: late acknowledgements cannot switch after Stay/account change.
import type {ExecutionLease} from './auth/lifecycle.ts';
import type {LeaveClient,Receipt} from './api/leave.ts';
export type SelectionState=Readonly<{kind:'idle'|'working'|'unresolved'|'committed'|'denied';org?:string;operation?:string;receipt?:Receipt;error_id?:string}>;
export function createSelectionController(options:{client:LeaveClient;acquire:()=>ExecutionLease<unknown>|null;publish:(s:SelectionState)=>void;newId?:()=>string}){
 let state:SelectionState={kind:'idle'},epoch=0,disposed=false,active:AbortController|null=null;
 const set=(value:SelectionState)=>{if(!disposed){state=Object.freeze(value);options.publish(state);}};
 async function run(recover=false){
  if(disposed||state.kind==='working'||!state.org||!state.operation)return;
  const lease=options.acquire();if(!lease){set({...state,kind:'denied',error_id:'authentication_required'});return;}
  const mine=++epoch,snapshot=state,controller=new AbortController();active=controller;
  const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});
  const current=()=>!disposed&&mine===epoch&&lease.isCurrent()&&!controller.signal.aborted;
  const denied=(r:{ok:boolean;error_id?:string})=>!r.ok&&['authentication_required','access_denied','service_access_denied','identity.verification_required'].includes(r.error_id??'');
  const deadline=performance.now()+15000;let expire!:(r:{ok:false;error_id:string})=>void;const expired=new Promise<{ok:false;error_id:string}>(resolve=>{expire=resolve;});const timer=setTimeout(()=>{if(current())set({...snapshot,kind:'unresolved',error_id:'api_unavailable'});expire({ok:false,error_id:'api_unavailable'});abort();},15000);
  const bounded=<T,>(work:Promise<T>)=>Promise.race([work,expired]);
  set({...snapshot,kind:'working'});
  try{
   let result=await bounded((recover?options.client.lookup:options.client.select)(lease.session.access_token,controller.signal,snapshot.org!,snapshot.operation!));
   // One same-operation retry and at most three lookups share one recovery cycle.
   if(recover&&result.ok&&result.value.status==='unresolved'&&performance.now()<deadline){
    result=await bounded(options.client.select(lease.session.access_token,controller.signal,snapshot.org!,snapshot.operation!));
    for(let i=0;i<2&&!denied(result)&&(!result.ok||result.value.status==='unresolved')&&current()&&performance.now()<deadline;i++)result=await bounded(options.client.lookup(lease.session.access_token,controller.signal,snapshot.org!,snapshot.operation!));
   }
   if(!current())return;
   if(!result.ok){const denied=['authentication_required','access_denied','service_access_denied','identity.verification_required'].includes(result.error_id);set({...snapshot,kind:denied?'denied':'unresolved',error_id:result.error_id});return;}
   if(result.value.status==='unresolved'){set({...snapshot,kind:'unresolved'});return;}
   set({...snapshot,kind:'committed',receipt:result.value});
  }catch{if(current())set({...snapshot,kind:'unresolved',error_id:'api_unavailable'});}
  finally{clearTimeout(timer);lease.signal.removeEventListener('abort',abort);lease.release();controller.abort();if(active===controller)active=null;}
 }
 function stay(){epoch++;active?.abort();active=null;set({kind:'idle'});}
 return{state:()=>state,select(org:string){stay();set({kind:'unresolved',org,operation:(options.newId??(()=>crypto.randomUUID()))()});return run();},retry:()=>run(true),stay,dispose(){stay();disposed=true;}};
}

// Owner tab-local scope and the neutral in-memory same-user return guard.
import {createReturnSelection} from './auth/lifecycle.ts';
import {id,type Organization} from './api/leave.ts';
export function createEntryNavigation(){
 let active:{account:string;org:string}|null=null,pending:{account:string;org:string}|null=null,epoch=0;
 const observations=new Set<ReturnType<typeof createReturnSelection>>();
 const path=(org:string)=>'/organizations/'+org;
 function clear(){epoch++;active=null;pending=null;for(const guard of observations)guard.dispose();observations.clear();}
 function resume(intent:unknown):boolean{
  clear();if(!intent||typeof intent!=='object'||Array.isArray(intent)||Object.keys(intent).sort().join()!=='account_id,scope_id')return false;
  const value=intent as Record<string,unknown>;if(!id(value.account_id)||!id(value.scope_id))return false;
  pending={account:value.account_id,org:value.scope_id};return true;
 }
 return{
  establish(account:string,org:string){if(!id(account)||!id(org))throw Error('entry_scope_invalid');clear();active={account,org};},
  suspend(){if(active)resume({account_id:active.account,scope_id:active.org});},
  returnIntent(){const scope=pending??active;return scope?Object.freeze({account_id:scope.account,scope_id:scope.org}):null;},
  resume,
  async target(account:string,organizations:readonly Organization[],location:{pathname:string;search:string;hash:string},observe:(org:string)=>Promise<{account_id:string;scope_id:string}|null>,execution?:Pick<ExecutionLease<unknown>,'signal'|'isCurrent'>):Promise<{kind:'established'|'select'|'none';org?:string}>{
   const live=()=>!execution||!execution.signal.aborted&&execution.isCurrent();
   if(!live())return{kind:'none'};
   const allowed=(org:string)=>organizations.some(o=>o.org_id===org);
   if(active){if(active.account===account&&allowed(active.org))return{kind:'established',org:active.org};clear();}
   if(pending){
    const previous=pending,mine=++epoch;
    if(previous.account!==account||!allowed(previous.org)){clear();return{kind:'none'};}
    // Each executing lease owns its observation. A replaced/cancelled execution
    // leaves the identity pending so its replacement can freshly observe it.
    const guard=createReturnSelection({routes:['/',path(previous.org)],safePath:'/'});
    guard.capture(path(previous.org),{account_id:previous.account,scope_id:previous.org});observations.add(guard);
    const abort=()=>guard.dispose(),current=()=>live()&&epoch===mine&&pending===previous;
    execution?.signal.addEventListener('abort',abort,{once:true});if(!live())abort();
    try{
     const result=await guard.restore(()=>current()?observe(previous.org):Promise.resolve(null));
     if(!current())return{kind:'none'};
     if(result.kind==='restored'){pending=null;return{kind:'select',org:previous.org};}
     clear();return{kind:'none'};
    }finally{execution?.signal.removeEventListener('abort',abort);observations.delete(guard);guard.dispose();}
   }
   if(location.search||location.hash)return{kind:'none'};
   const prefix='/organizations/',org=location.pathname.startsWith(prefix)?location.pathname.slice(prefix.length):'';
   if(id(org)&&allowed(org))return{kind:'select',org};
   if(organizations.length===1&&location.pathname==='/')return{kind:'select',org:organizations[0]!.org_id};
   return{kind:'none'};
  },clear,
 };
}

import type {Language} from './api/leave.ts';
export type LanguageState=Readonly<{language:Language|null;desired:'en'|'pt'|null;notice:'loading'|'saving'|'saved'|'unavailable'|'retry'}>;
export function createLanguageController(options:{client:LeaveClient;acquire:()=>ExecutionLease<unknown>|null;publish:(s:LanguageState)=>void;newId?:()=>string}){
 let state:LanguageState={language:null,desired:null,notice:'loading'},pending:{operation_id:string;expected_revision:string;preferred_locale:'en'|'pt'}|null=null,epoch=0,disposed=false;
 const set=(next:LanguageState)=>{if(!disposed){state=Object.freeze(next);options.publish(state);}};
 async function load(){const lease=options.acquire();if(!lease)return;const mine=++epoch;try{const result=await options.client.language(lease.session.access_token,lease.signal);if(disposed||mine!==epoch||!lease.isCurrent())return;if(result.ok)set({...state,language:result.value,notice:'saved'});else set({...state,notice:'unavailable'});}finally{lease.release();}}
 async function save(){
  if(!state.language||!state.desired||disposed)return;
  const lease=options.acquire();if(!lease)return;const mine=++epoch;
  if(!pending||pending.preferred_locale!==state.desired)pending={operation_id:(options.newId??(()=>crypto.randomUUID()))(),expected_revision:state.language.revision,preferred_locale:state.desired};
  const command=pending;set({...state,notice:'saving'});
  try{
   const result=await options.client.setLanguage(lease.session.access_token,lease.signal,command);
   if(disposed||mine!==epoch||!lease.isCurrent())return;
   if(result.ok){pending=null;set({language:result.value,desired:result.value.preferred_locale,notice:'saved'});return;}
   if(result.error_id==='identity.preference_revision_conflict'){
    // Rejected operation stays immutable. New retry uses the current revision while
    // preserving the user's desired locale independently of the committed value.
    pending=null;const current=await options.client.language(lease.session.access_token,lease.signal);
    if(disposed||mine!==epoch||!lease.isCurrent())return;
    if(current.ok)set({...state,language:current.value,notice:'retry'});else set({...state,notice:'retry'});
   }else set({...state,notice:'retry'});
  }catch{if(!disposed&&mine===epoch&&lease.isCurrent())set({...state,notice:'retry'});}
  finally{lease.release();}
 }
 return{state:()=>state,load,change(desired:'en'|'pt'){set({...state,desired});return save();},retry:save,dispose(){disposed=true;epoch++;pending=null;state={language:null,desired:null,notice:'loading'};}};
}
