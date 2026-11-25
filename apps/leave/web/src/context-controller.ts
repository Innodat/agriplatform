// Owner observation controller. Every load uses a current Auth execution lease.
import type {ExecutionLease} from './auth/lifecycle.ts';
import type {LeaveClient,DraftPreparation} from './api/leave.ts';
export type ContextState=Readonly<{kind:'loading'|'denied'|'unavailable'}>|Readonly<{kind:'resolved';value:DraftPreparation}>;
export function createContextController(options:{client:Pick<LeaveClient,'context'>;acquire:()=>ExecutionLease<unknown>|null;publish:(s:ContextState)=>void}){
 let epoch=0,disposed=false,active:AbortController|null=null;
 const publish=(s:ContextState)=>{if(!disposed)options.publish(s);};
 function clear(){epoch++;active?.abort();active=null;}
 return{
  async load(org:string){
   clear();const mine=epoch;publish({kind:'loading'});
   const lease=options.acquire();if(!lease){publish({kind:'denied'});return;}
   const controller=new AbortController();active=controller;
   const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});if(lease.signal.aborted)abort();
   const current=()=>!disposed&&mine===epoch&&lease.isCurrent()&&!controller.signal.aborted;
   try{
    const result=await options.client.context(lease.session.access_token,controller.signal,org);
    if(!current())return;
    publish(result.ok?{kind:'resolved',value:result.value}:{kind:['authentication_required','access_denied','identity.verification_required'].includes(result.error_id)?'denied':'unavailable'});
   }catch{if(current())publish({kind:'unavailable'});}
   finally{lease.signal.removeEventListener('abort',abort);controller.abort();lease.release();if(active===controller)active=null;}
  },dispose(){clear();disposed=true;},
 };
}
