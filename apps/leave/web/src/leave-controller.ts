// Owner transition controller: late acknowledgements cannot switch after Stay/account change.
import type {ExecutionLease} from './auth/lifecycle.ts';
import type {LeaveClient,Receipt} from './api/leave.ts';
export type SelectionState=Readonly<{kind:'idle'|'working'|'unresolved'|'committed'|'denied';org?:string;operation?:string;receipt?:Receipt;error_id?:string}>;
export function createSelectionController(options:{client:LeaveClient;acquire:()=>ExecutionLease<unknown>|null;publish:(s:SelectionState)=>void;newId?:()=>string}){
 let state:SelectionState={kind:'idle'},epoch=0,disposed=false,active:AbortController|null=null;
 const set=(value:SelectionState)=>{if(!disposed){state=Object.freeze(value);options.publish(state);}};
 const denied=(r:{ok:boolean;error_id?:string})=>!r.ok&&['authentication_required','access_denied','identity.verification_required'].includes(r.error_id??'');
 async function run(recover=false){
  if(disposed||state.kind!=='unresolved'||!state.org||!state.operation)return;
  const lease=options.acquire();if(!lease){set({...state,kind:'denied',error_id:'authentication_required'});return;}
  const mine=++epoch,{org,operation}=state,controller=new AbortController();active=controller;
  const selection={org,operation};
  const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});
  const current=()=>!disposed&&mine===epoch&&lease.isCurrent()&&!lease.signal.aborted&&!controller.signal.aborted;
  const settle=new Promise<{ok:false;error_id:string}>(resolve=>{
   controller.signal.addEventListener('abort',()=>resolve({ok:false,error_id:'cancelled'}),{once:true});
  });
  const limit=recover?15000:12000;
  const deadline=performance.now()+limit;
  const timer=setTimeout(()=>{
   if(current())set({...selection,kind:'unresolved',error_id:'api_unavailable'});
   abort();
  },limit);
  if(lease.signal.aborted)abort();
  const bounded=<T,>(work:Promise<T>)=>Promise.race([work,settle]);
  const select=()=>bounded(options.client.select(lease.session.access_token,controller.signal,org,operation));
  const lookup=()=>bounded(options.client.lookup(lease.session.access_token,controller.signal,org,operation));
  try{
   if(!current())return;
   set({...selection,kind:'working'});
   let result=await (recover?lookup():select());
   // One same-operation retry and at most three lookups share one recovery cycle.
   if(recover&&result.ok&&result.value.status==='unresolved'&&current()&&performance.now()<deadline){
    result=await select();
    for(let i=0;i<2&&!denied(result)&&(!result.ok||result.value.status==='unresolved')&&current()&&performance.now()<deadline;i++)result=await lookup();
   }
   if(!current())return;
   if(!result.ok){set({...selection,kind:denied(result)?'denied':'unresolved',error_id:result.error_id});return;}
   if(result.value.status==='unresolved'){set({...selection,kind:'unresolved'});return;}
   set({...selection,kind:'committed',receipt:result.value});
  }catch{if(current())set({...selection,kind:'unresolved',error_id:'api_unavailable'});}
  finally{clearTimeout(timer);lease.signal.removeEventListener('abort',abort);lease.release();controller.abort();if(active===controller)active=null;}
 }
 function cancel(){epoch++;active?.abort();active=null;}
 function stay(){cancel();set({kind:'idle'});}
 return{state:()=>state,select(org:string,operation=(options.newId??(()=>crypto.randomUUID()))()){cancel();set({kind:'unresolved',org,operation});return run();},retry:()=>run(true),stay,dispose(){disposed=true;cancel();}};
}

// Owner tab-local scope and the neutral in-memory same-user return guard.
import {createReturnSelection} from './auth/lifecycle.ts';
import {id,draftId,type Organization} from './api/leave.ts';
export function createEntryNavigation(){
 type Scope={account:string;org:string};
 type DraftScope=Scope&{draft:string};
 type Route=Pick<Location,'pathname'|'search'|'hash'>;
 let active:(Scope&{returned?:string})|null=null,opened:DraftScope|null=null;
 let pending:(Scope&{draft?:string;operation?:string})|null=null,epoch=0,returnRefused=false;
 const observations=new Set<ReturnType<typeof createReturnSelection>>();
 const path=(org:string,draft?:string)=>'/organizations/'+org+(draft?'/drafts/'+draft:'');
 const exact=(route:Route,org:string,draft:string)=>route.pathname===path(org,draft)&&!route.search&&!route.hash;
 function clear(){epoch++;active=null;opened=null;pending=null;returnRefused=false;for(const guard of observations)guard.dispose();observations.clear();}
 function refuseReturn(){
  const draft=Boolean(pending?.draft);
  clear();returnRefused=draft;
  return draft?{kind:'none' as const,returnUnavailable:true}:{kind:'none' as const};
 }
 function resume(intent:unknown):boolean{
  clear();if(!intent||typeof intent!=='object'||Array.isArray(intent))return false;
  const keys=Object.keys(intent).sort().join();
  const value=intent as Record<string,unknown>;
  if(!id(value.account_id)||!id(value.scope_id)||
     (keys!=='account_id,scope_id'&&(keys!=='account_id,draft_id,scope_id'||!draftId(value.draft_id))))return false;
  pending={account:value.account_id,org:value.scope_id,...(draftId(value.draft_id)?{draft:value.draft_id,operation:crypto.randomUUID()}:{})};return true;
 }
 return{
  establish(account:string,org:string,operation?:string){
   if(!id(account)||!id(org))throw Error('entry_scope_invalid');
   const returned=pending?.operation&&pending.operation===operation&&pending.account===account&&pending.org===org?pending.draft:undefined;
   clear();active={account,org,returned};
  },
  openDraft(org:string,draft:string,route:Route){
   if(active?.org===org&&draftId(draft)&&exact(route,org,draft))opened={account:active.account,org,draft};
  },
  leaveDraft(org:string){
   if(active?.org!==org)return;
   active.returned=undefined;opened=null;
  },
  openedDraft(route:Route){return opened&&exact(route,opened.org,opened.draft)?opened:null;},
  returnedDraft(org:string,route:Route){return active?.org===org&&active.returned&&exact(route,org,active.returned)?active.returned:undefined;},
  suspend(draft?:string){if(active)resume({account_id:active.account,scope_id:active.org,...(draftId(draft)?{draft_id:draft}:{})});},
  returnIntent(){
   const scope=pending??active;
   return scope?Object.freeze({account_id:scope.account,scope_id:scope.org,...(pending?.draft?{draft_id:pending.draft}:{})}):null;
  },
  resume,refuseReturn,
  supersedeReturn(){if(pending||returnRefused)clear();},
  async target(account:string,organizations:readonly Organization[],location:Route,observe:(org:string)=>Promise<{account_id:string;scope_id:string}|null|'unavailable'>,execution?:Pick<ExecutionLease<unknown>,'signal'|'isCurrent'>):Promise<{kind:'established'|'select'|'none'|'retry';org?:string;draft?:string;operation?:string;returnUnavailable?:boolean}>{
   const live=()=>!execution||!execution.signal.aborted&&execution.isCurrent();
   if(!live())return{kind:'none'};
   if(returnRefused)return{kind:'none',returnUnavailable:true};
   const allowed=(org:string)=>organizations.some(o=>o.org_id===org);
   if(active){
    const owningAccount=active.account;
    if(owningAccount===account&&allowed(active.org))return{kind:'established',org:active.org};
    clear();
    if(owningAccount!==account)return{kind:'none'};
   }
   if(pending){
    const previous=pending,mine=++epoch;
    if(previous.account!==account||!allowed(previous.org))return refuseReturn();
    // Each executing lease owns its observation. A replaced/cancelled execution
    // leaves the identity pending so its replacement can freshly observe it.
    const destination=path(previous.org,previous.draft);
    const guard=createReturnSelection({routes:['/',destination],safePath:'/'});
    guard.capture(destination,{account_id:previous.account,scope_id:previous.org});observations.add(guard);
    const abort=()=>guard.dispose(),current=()=>live()&&epoch===mine&&pending===previous;
    execution?.signal.addEventListener('abort',abort,{once:true});if(!live())abort();
    try{
     let unavailable=true;
     const result=await guard.restore(async()=>{
      if(!current())return null;
      const observed=await observe(previous.org);
      if(observed==='unavailable')return null;
      unavailable=false;
      return observed;
     });
     if(!current())return{kind:'none'};
     if(result.kind!=='restored'&&previous.draft&&unavailable)return{kind:'retry'};
     if(result.kind!=='restored')return refuseReturn();
     // Draft return is claimed only when the selection commits. If SDK startup
     // replaces this lease, its successor observes afresh and reuses the audit operation.
     if(previous.draft)return{kind:'select',org:previous.org,draft:previous.draft,operation:previous.operation};
     pending=null;return{kind:'select',org:previous.org};
    }finally{execution?.signal.removeEventListener('abort',abort);observations.delete(guard);guard.dispose();}
   }
   if(location.search||location.hash)return{kind:'none'};
   const prefix='/organizations/',parts=location.pathname.startsWith(prefix)?location.pathname.slice(prefix.length).split('/'):[],org=parts[0]??'';
   if(parts.length>0&&parts.length!==1&&!(parts.length===3&&parts[1]==='drafts'&&draftId(parts[2])))return{kind:'none'};
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
