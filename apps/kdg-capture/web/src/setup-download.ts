/** Explicit verified setup import; no startup, editor or sender activation. */
import {createAuthEntry,type AuthEntryOptions} from './auth-entry.js';
import {loadProvision,type PendingProvision} from './provision.js';
import type {openHistoryStore} from './history-store.js';
type Store=Awaited<ReturnType<typeof openHistoryStore>>;
export type SetupResult=Exclude<Awaited<ReturnType<typeof loadProvision>>,{kind:'loaded'}>|Exclude<Awaited<ReturnType<Store['beginSetupRefresh']>>,{kind:'started'}>|Awaited<ReturnType<Store['importProvision']>>|Awaited<ReturnType<Store['denySetup']>>;
export function createSetupEntry(configuration:AuthEntryOptions&{store:Store;setupTimeoutMs?:number}){
 const {store,setupTimeoutMs=10000,...options}=Object.freeze({...configuration});
 const {acquireExecution,...entry}=createAuthEntry(options);
 return {...entry,async refresh(pending:PendingProvision,restore:Readonly<{restoreDenied?:boolean}>={}):Promise<SetupResult>{
  const started=performance.now(),lease=acquireExecution();if(!lease)return Object.freeze({kind:'superseded'});
  const controller=new AbortController(),abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});
  const valid=Number.isFinite(setupTimeoutMs)&&setupTimeoutMs>0&&setupTimeoutMs<=10000;
  const current=()=>valid&&!controller.signal.aborted&&lease.isCurrent()&&performance.now()-started<setupTimeoutMs;
  const execution={signal:controller.signal,isCurrent:current};let result:SetupResult=Object.freeze({kind:'invalid_request'});
  const timer=valid?setTimeout(abort,Math.max(0,setupTimeoutMs-(performance.now()-started))):undefined;
  try{
   const pinned=Object.freeze({...pending});
   if(current()&&pinned.account_id===lease.session.account_id&&pinned.account_id===lease.context.account_id&&pinned.org_id===options.org&&pinned.org_id===lease.context.authorization_scope.org_id){
    const begun=await store.beginSetupRefresh(execution);
    if(begun.kind!=='started')result=begun;
    else if(current()){
     const loaded=await loadProvision(lease.session,pinned,{...execution,request:options.request,timeoutMs:setupTimeoutMs-(performance.now()-started)});
     if(current()){
      if(loaded.kind==='loaded')result=await store.importProvision(loaded.provision,begun.ticket,{...execution,restoreDenied:restore.restoreDenied===true});
      else if(loaded.kind==='error'&&loaded.error_id==='access_denied')result=await store.denySetup(begun.ticket,execution);
      else result=loaded;
     }
    }
   }
  }catch{result=Object.freeze({kind:'unavailable'});}
  finally{
   try{if(!lease.isCurrent())result=Object.freeze({kind:'superseded'});else if(!current())result=Object.freeze({kind:valid?'verification_unavailable':'invalid_request'});}catch{result=Object.freeze({kind:'superseded'});}
   try{lease.release();}catch{result=Object.freeze({kind:'unavailable'});}
   if(valid&&performance.now()-started>=setupTimeoutMs)result=Object.freeze({kind:'verification_unavailable'});
   clearTimeout(timer);lease.signal.removeEventListener('abort',abort);controller.abort();
  }
  return result;
 }};
}
