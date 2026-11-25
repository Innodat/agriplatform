import type {DraftInput} from './draft-input.ts';
import type {ExecutionLease} from './auth/lifecycle.ts';
import type {LeaveClient,DraftChoicesResponse} from './api/leave.ts';
export function selectionNotice(previous:string|null,notice:string|null,input:DraftInput):string|null{
 if(notice!==null)return notice;
 if(previous==='Please choose a leave type again.'&&input.leave_type_id===null)return previous;
 if(previous==='Please choose a duration again.'&&input.duration_mode===null)return previous;
 return null;
}
export type ChoicesState=Readonly<{kind:'loading'|'denied'|'unavailable';error_id?:string}>|Readonly<{kind:'retained';value:DraftChoicesResponse}>|Readonly<{kind:'resolved';value:DraftChoicesResponse;inputGeneration:number}>;
export function createChoicesController(options:{client:Pick<LeaveClient,'choices'>;acquire:()=>ExecutionLease<unknown>|null;publish:(s:ChoicesState)=>void;initial?:DraftChoicesResponse}){
 let epoch=0,disposed=false,active:AbortController|null=null,last:DraftChoicesResponse|null=options.initial??null;
 function clear(){epoch++;active?.abort();active=null;}
 const publish=(state:ChoicesState)=>{if(!disposed)options.publish(state);};
 return{
  async load(org:string,selected:string|null,inputGeneration:number,cursor:string|null=null){
   clear();const mine=epoch;publish({kind:'loading'});const lease=options.acquire();if(!lease){publish({kind:'denied'});return;}
   const controller=new AbortController();active=controller;const abort=()=>controller.abort();lease.signal.addEventListener('abort',abort,{once:true});if(lease.signal.aborted)abort();
   const current=()=>!disposed&&mine===epoch&&lease.isCurrent()&&!controller.signal.aborted;
   try{const result=await options.client.choices(lease.session.access_token,controller.signal,org,selected,cursor);if(current()){if(result.ok)last=result.value;publish(result.ok?{kind:'resolved',value:result.value,inputGeneration}:{kind:['authentication_required','access_denied','identity.verification_required'].includes(result.error_id)?'denied':'unavailable',error_id:result.error_id});}}
   catch{if(current())publish({kind:'unavailable'});}
   finally{lease.signal.removeEventListener('abort',abort);controller.abort();lease.release();if(active===controller)active=null;}
  },invalidate(){const pending=active!==null;clear();if(pending)publish(last?{kind:'retained',value:last}:{kind:'loading'});return pending&&last===null;},dispose(){clear();disposed=true;},
 };
}
