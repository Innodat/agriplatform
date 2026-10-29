import {useCallback,useEffect,useId,useMemo,useRef,useState} from 'react';
import {AdminEntry} from './AdminEntry';
import {OwnWorkspace} from './OwnWorkspace';
import {acceptOwnSignIn,invalidateOwnSelection,observeOwnAccount,hasExplicitOwnSignout} from './own-workspace';
import type {EntryAuth} from './auth-entry';
import type {EmailCodeAuth,EmailCodeState} from './auth/lifecycle';
import {useEmailCode} from './auth/use-lifecycle';
export type EmailCodeEntryProps=Readonly<{org:string;auth?:EntryAuth&EmailCodeAuth;request?:typeof fetch;online?:boolean;timeoutMs?:number;surface?:'own'|'admin'}>;
const messages:Record<EmailCodeState['notice'],string>={
 none:'Enter your details to sign in.',check_email:'If this account can sign in, a code has been sent. Check your email.',
 invalid_email:'Enter a valid email address.',invalid_code:'Enter the six-digit code from your email.',
 code_rejected:'That code is invalid or has expired. Try again.',rate_limited:'Please wait before trying again.',
 unavailable:'Could not complete sign-in. Check your connection and try again.',
};
function EmailForm({auth,online,timeoutMs,onVerified,onCancel}:Pick<EmailCodeEntryProps,'timeoutMs'>&{auth:EntryAuth&EmailCodeAuth;online:boolean;onVerified(account:string):void;onCancel():void}){
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
 const owner=useRef({auth:props.auth,org:props.org,surface:props.surface,version:0});
 if(owner.current.auth!==undefined&&owner.current.auth!==props.auth||owner.current.org!==props.org||owner.current.surface!==props.surface)owner.current={auth:props.auth,org:props.org,surface:props.surface,version:owner.current.version+1};
 return <OwnedEmailCodeEntry key={owner.current.version} {...props} bootstrap={owner.current.version===0}/>;
}
function OwnedEmailCodeEntry(props:EmailCodeEntryProps&{bootstrap:boolean}){
 const [form,setForm]=useState(false),[accepted,setAccepted]=useState<string|null|undefined>(props.bootstrap?undefined:null),[storageFailure,setStorageFailure]=useState(false);
 const launch=useRef(0),failureAccount=useRef<string|undefined>(undefined);
 useEffect(()=>()=>{launch.current++;},[]);
 const failStorage=useCallback((account?:string)=>{failureAccount.current=account;setStorageFailure(true);},[]);
 const open=useCallback(async()=>{launch.current++;setAccepted(null);setForm(true);},[]);
 const complete=useCallback(async(account:string)=>{const execution=launch.current;try{const fenced=await observeOwnAccount(localStorage,props.org,account,failStorage);if(execution!==launch.current)return;if(fenced.kind!=='locked')throw Error('local_storage_unavailable');acceptOwnSignIn(localStorage,props.org,account);setAccepted(account);setForm(false);}catch{if(execution===launch.current){setAccepted(null);setForm(false);failStorage(account);}}},[props.org,failStorage]);
 const cancel=useCallback(()=>{launch.current++;setForm(false);},[]);
 const auth=useMemo<EntryAuth|undefined>(()=>{
  const source=props.auth;if(!source)return undefined;let pinned=accepted;
  const allows=(value:{user:{id:string}}|null)=>{if(!value)return true;if(pinned===undefined)pinned=value.user.id;return pinned!==null&&value.user.id===pinned;};
  const observe=async(value:{user:{id:string}}|null)=>{if(!value)return true;const result=await observeOwnAccount(localStorage,props.org,value?.user.id??null,failStorage,pinned??undefined);if(result.kind!=='locked')throw Error('local_storage_unavailable');return !value||!hasExplicitOwnSignout(localStorage,props.org,value.user.id);};
  return{
   getSession:async()=>{const result=await source.getSession(),permitted=await observe(result.data.session);return allows(result.data.session)&&permitted?result:{...result,data:{session:null}};},
   refreshSession:async()=>{const result=await source.refreshSession(),permitted=await observe(result.data.session);return allows(result.data.session)&&permitted?result:{...result,data:{session:null,user:null}};},
   signOut:async options=>{const locked=await invalidateOwnSelection(localStorage,props.org,pinned??undefined,failStorage);const result=await source.signOut(options);if(locked.kind!=='locked')throw Error('local_storage_unavailable');return result;},
   onAuthStateChange:callback=>source.onAuthStateChange((event,value)=>{
    // Begin negative invalidation synchronously; never await SDK work in its callback.
    const prior=pinned;if(prior!==null&&(value||event==='SIGNED_OUT'))void observeOwnAccount(localStorage,props.org,value?.user.id??null,failStorage,prior??undefined);
    let permitted=false;try{permitted=!value||!hasExplicitOwnSignout(localStorage,props.org,value.user.id);}catch{failStorage(value?.user.id);}
    if(allows(value)&&permitted)callback(event,value);else{pinned=null;callback('SIGNED_OUT',null);}
   }),
  };
 },[props.auth,accepted,props.org,failStorage]);
 if(storageFailure)return <div className="kdg-entry" lang="en"><main><h1>KDG Capture</h1><h2>Device storage needs attention</h2><p role="alert">Could not secure saved work. Check device storage, then Retry. Saved work is retained.</p><button type="button" onClick={()=>{void invalidateOwnSelection(localStorage,props.org,failureAccount.current,failStorage).then(result=>{if(result.kind==='locked'){setAccepted(null);setForm(false);setStorageFailure(false);}});}}>Retry</button></main></div>;
 return form&&props.auth?<EmailForm auth={props.auth} online={props.online??true} timeoutMs={props.timeoutMs} onVerified={complete} onCancel={cancel}/>:
  props.surface==='admin'&&auth?<AdminEntry {...props} auth={auth} beginSignIn={open}/>:<OwnWorkspace {...props} auth={auth} beginSignIn={open}/>;
}
