import {useCallback,useEffect,useId,useMemo,useRef,useState} from 'react';
import {AuthEntry} from './AuthEntry';
import type {EntryAuth} from './auth-entry';
import type {EmailCodeAuth,EmailCodeState} from './auth/lifecycle';
import {useEmailCode} from './auth/use-lifecycle';
export type EmailCodeEntryProps=Readonly<{org:string;auth:EntryAuth&EmailCodeAuth;request?:typeof fetch;online?:boolean;timeoutMs?:number}>;
const messages:Record<EmailCodeState['notice'],string>={
 none:'Enter your details to sign in.',check_email:'If this account can sign in, a code has been sent. Check your email.',
 invalid_email:'Enter a valid email address.',invalid_code:'Enter the six-digit code from your email.',
 code_rejected:'That code is invalid or has expired. Try again.',rate_limited:'Please wait before trying again.',
 unavailable:'Could not complete sign-in. Check your connection and try again.',
};
function EmailForm({auth,online,timeoutMs,onVerified,onCancel}:Pick<EmailCodeEntryProps,'auth'|'timeoutMs'>&{online:boolean;onVerified(account:string):void;onCancel():void}){
 const {state,send,verify,restart}=useEmailCode({auth,online,timeoutMs});
 const [email,setEmail]=useState(''),[code,setCode]=useState(''),[clock,setClock]=useState(Date.now());
 const emailInput=useRef<HTMLInputElement>(null),codeInput=useRef<HTMLInputElement>(null),id=useId();
 const busy=state.kind==='sending'||state.kind==='verifying'||state.kind==='verified',codeStep=state.kind==='code'||state.kind==='verifying'||state.kind==='verified';
 useEffect(()=>{if(state.kind==='verified'&&state.account_id)onVerified(state.account_id);},[state.kind,state.account_id,onVerified]);
 useEffect(()=>{if(!busy)(codeStep?codeInput:emailInput).current?.focus();},[busy,codeStep,online]);
 useEffect(()=>{setClock(Date.now());const delay=state.resendAt-Date.now();if(delay>0){const timer=setTimeout(()=>setClock(Date.now()),delay+1);return()=>clearTimeout(timer);}},[state.resendAt]);
 const blocked=busy||!online,resendBlocked=blocked||clock<state.resendAt;
 return <div className="kdg-entry" lang="en"><a className="kdg-entry-skip" href="#kdg-entry-content">Skip to content</a>
  <main id="kdg-entry-content" tabIndex={-1}><h1>KDG Capture</h1><p className="kdg-entry-organization">Khula Development Group</p>
   <h2>{!online?'Connect to the internet':codeStep?'Check your email':'Sign in with an email code'}</h2>
   <div role="status" aria-live="polite" aria-atomic="true"><p id={id+'-notice'}>{!online?'Online sign-in is required.':state.kind==='sending'?'Requesting a code…':state.kind==='verifying'?'Checking the code…':!codeStep&&!busy&&clock<state.resendAt?'Please wait before requesting another code.':messages[state.notice]}</p></div>
   <form onSubmit={event=>{event.preventDefault();if(blocked)return;if(codeStep){const entered=code;setCode('');void verify(entered);}else void send(email);}}>
    {codeStep?<><label htmlFor={id+'-code'}>One-time code</label><input ref={codeInput} id={id+'-code'} aria-describedby={id+'-notice'} type="text" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" minLength={6} maxLength={6} required value={code} disabled={blocked} onChange={event=>setCode(event.target.value)}/></>:
     <><label htmlFor={id+'-email'}>Email address</label><input ref={emailInput} id={id+'-email'} aria-describedby={id+'-notice'} type="email" autoComplete="email" maxLength={254} required value={email} disabled={blocked} onChange={event=>setEmail(event.target.value)}/></>}
    <button type="submit" aria-disabled={blocked||(!codeStep&&clock<state.resendAt)||undefined} aria-busy={busy} onClick={event=>{if(blocked||(!codeStep&&clock<state.resendAt))event.preventDefault();}}>{codeStep?'Verify code':'Send code'}</button>
    {codeStep&&<><button type="button" aria-disabled={resendBlocked||undefined} onClick={()=>{if(!resendBlocked){setCode('');void send(email);}}}>Resend code</button>
     <button type="button" aria-disabled={busy||undefined} onClick={()=>{if(!busy){restart();setCode('');setEmail('');}}}>Use another email</button></>}
    <button type="button" onClick={()=>{restart();setCode('');setEmail('');onCancel();}}>Cancel</button>
   </form>
  </main></div>;
}
/** Auth owns persisted sessions. Only the current successful code attempt can reopen admission. */
export function EmailCodeEntry(props:EmailCodeEntryProps){
 const owner=useRef({auth:props.auth,org:props.org,version:0});
 if(owner.current.auth!==props.auth||owner.current.org!==props.org)owner.current={auth:props.auth,org:props.org,version:owner.current.version+1};
 return <OwnedEmailCodeEntry key={owner.current.version} {...props} bootstrap={owner.current.version===0}/>;
}
function OwnedEmailCodeEntry(props:EmailCodeEntryProps&{bootstrap:boolean}){
 const [form,setForm]=useState(false),[accepted,setAccepted]=useState<string|null|undefined>(props.bootstrap?undefined:null);
 const open=useCallback(async()=>{setAccepted(null);setForm(true);},[]);
 const complete=useCallback((account:string)=>{setAccepted(account);setForm(false);},[]);
 const cancel=useCallback(()=>setForm(false),[]);
 const auth=useMemo<EntryAuth>(()=>{
  const source=props.auth;let pinned=accepted;
  const allows=(value:{user:{id:string}}|null)=>{if(!value)return true;if(pinned===undefined)pinned=value.user.id;return pinned!==null&&value.user.id===pinned;};
  return{
   getSession:async()=>{const result=await source.getSession();return allows(result.data.session)?result:{...result,data:{session:null}};},
   refreshSession:async()=>{const result=await source.refreshSession();return allows(result.data.session)?result:{...result,data:{session:null,user:null}};},
   signOut:options=>source.signOut(options),
   onAuthStateChange:callback=>source.onAuthStateChange((event,value)=>{if(allows(value))callback(event,value);else callback('SIGNED_OUT',null);}),
  };
 },[props.auth,accepted]);
 return form?<EmailForm auth={props.auth} online={props.online??true} timeoutMs={props.timeoutMs} onVerified={complete} onCancel={cancel}/>:
  <AuthEntry {...props} auth={auth} beginSignIn={open}/>;
}
