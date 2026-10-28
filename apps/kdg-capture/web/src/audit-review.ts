/** Inert single-context audit state; no Auth admission, mounting or persistence. */
import {auditDetails,type PendingAuditDetails,type AuditDetailsOptions} from './audit-display.js';
import {auditPresentation,type AuditPresentationResult} from './audit-presentation.js';
import type {Session} from './entry';
export type AuditReviewOptions = AuditDetailsOptions & {session:Session;pending:PendingAuditDetails};
export type AuditReviewState = AuditPresentationResult | Readonly<{kind:'idle'|'loading'|'locked'|'closed'}>;
export type AuditReview = Readonly<{
 snapshot():AuditReviewState;load():Promise<AuditReviewState>;retry():Promise<AuditReviewState>;invalidate():void;close():void;
}>;
export function createAuditReview(configuration:AuditReviewOptions):AuditReview {
 let bound:{session:Session;pending:PendingAuditDetails}|undefined;
 let signal:AbortSignal,isCurrent:()=>boolean,request:typeof fetch|undefined,timeoutMs:number|undefined;
 try{
  ({signal,isCurrent,request,timeoutMs}=configuration);
  if(!(signal instanceof AbortSignal)||typeof isCurrent!=='function')throw Error();
  bound={session:Object.freeze({account_id:configuration.session.account_id,access_token:configuration.session.access_token}),pending:Object.freeze({...configuration.pending})};
 }catch{throw Error('audit_review_configuration_invalid');}
 let state:AuditReviewState=Object.freeze({kind:'idle'}),generation=0,terminal=false;
 let active:AbortController|undefined;
 function end(kind:'locked'|'closed'){
  if(state.kind==='closed'||(terminal&&kind==='locked'))return;
  terminal=true;generation++;bound=undefined;
  state=Object.freeze({kind});
  signal.removeEventListener('abort',invalidate);
  const owned=active;active=undefined;owned?.abort();
 }
 function invalidate(){end('locked');}
 function current():boolean{
  if(terminal||signal.aborted)return false;
  let valid=false;try{valid=isCurrent()===true;}catch{/* Caller failure is refusal. */}
  // The predicate may synchronously invalidate, close or abort this context.
  return valid&&!terminal&&!signal.aborted;
 }
 function ensureCurrent(){if(terminal)return false;if(current())return true;invalidate();return false;}
 function snapshot():AuditReviewState{ensureCurrent();return state;}
 async function load():Promise<AuditReviewState>{
  if(!ensureCurrent())return state;
  const epoch=++generation,context=bound!;
  const prior=active;const owned=new AbortController();active=owned;
  state=Object.freeze({kind:'loading'});prior?.abort();
  let result:AuditPresentationResult;
  try{
   result=auditPresentation(await auditDetails(context.session,context.pending,{
    signal:owned.signal,isCurrent:()=>epoch===generation&&current(),request,timeoutMs
   }));
  }catch{result=Object.freeze({kind:'verification_unavailable'});}
  if(epoch!==generation)return Object.freeze({kind:'superseded'});
  if(!ensureCurrent())return state;
  active=undefined;state=result;return state;
 }
 if(signal.aborted)invalidate();else signal.addEventListener('abort',invalidate,{once:true});
 return Object.freeze({snapshot,load,retry:load,invalidate,close:()=>end('closed')});
}
