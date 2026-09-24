import {useEffect,useRef,useState,type FormEvent} from 'react';
import {auth,authError,configured,microsoftEnabled,rememberPasswordReturn,type PasswordFlow} from './auth';

type Props={flow:PasswordFlow|null;initialError:string;onPasswordSaved:()=>void};
export function LoginForm({flow,initialError,onPasswordSaved}:Props){
 const [mode,setMode]=useState<'login'|'reset'>('login');
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[confirmation,setConfirmation]=useState('');
 const [busy,setBusy]=useState(false),[error,setError]=useState(initialError),[notice,setNotice]=useState('');
 const pending=useRef(false),active=useRef(true);
 useEffect(()=>()=>{active.current=false;},[]);
 function switchMode(next:'login'|'reset'){setMode(next);setPassword('');setConfirmation('');setError('');setNotice('');}
 async function submit(event:FormEvent){
  event.preventDefault();if(pending.current||!configured)return;
  setError('');setNotice('');
  if(flow&&password!==confirmation){setError('Passwords do not match. Enter the same password twice.');return;}
  pending.current=true;setBusy(true);
  const action=flow?'password':mode==='reset'?'reset':'login';
  try{
   const result=flow?await auth.updateUser({password}):mode==='reset'
    ?await auth.resetPasswordForEmail(email.trim(),{redirectTo:location.origin+location.pathname})
    :await auth.signInWithPassword({email:email.trim(),password});
   if(!active.current)return;
   if(result.error){setError(authError(result.error,action));return;}
   if(flow){setPassword('');setConfirmation('');onPasswordSaved();}
   else if(mode==='reset'){rememberPasswordReturn();setNotice('If an account exists for that email, a password reset link will arrive shortly.');}
  }catch(error){if(active.current)setError(authError(error,action));}
  finally{pending.current=false;if(active.current)setBusy(false);}
 }
 async function microsoft(){
  if(pending.current)return;pending.current=true;setBusy(true);setError('');
  try{
   const {error}=await auth.signInWithOAuth({provider:'azure',options:{scopes:'email',redirectTo:location.origin+location.pathname+location.search}});
   if(error&&active.current)setError(authError(error,'oauth'));
  }catch(error){if(active.current)setError(authError(error,'oauth'));}
  finally{pending.current=false;if(active.current)setBusy(false);}
 }
 const heading=flow==='invite'?'Set your password':flow==='recovery'?'Choose a new password':mode==='reset'?'Reset your password':'Sign in to read';
 return <section className="panel auth-panel" aria-labelledby="auth-heading">
  <h2 id="auth-heading">{heading}</h2>
  <p>{flow?'Choose a password for your account.':mode==='reset'?'Enter your account email and we’ll send a reset link.':'Use your account email and password. Access is limited to authorized organization readers.'}</p>
  {!configured&&<p role="alert">Sign-in is not configured for this installation.</p>}
  {error&&<p role="alert" className="error">{error}</p>}
  <form onSubmit={submit} aria-busy={busy}>
   {!flow&&<label>Email<input type="email" autoComplete="username" autoCapitalize="none" spellCheck={false} value={email} onChange={e=>setEmail(e.target.value)} required disabled={busy||!configured}/></label>}
   {(flow||mode==='login')&&<label>{flow?'New password':'Password'}<input type="password" autoComplete={flow?'new-password':'current-password'} value={password} onChange={e=>setPassword(e.target.value)} required minLength={flow?8:undefined} disabled={busy||!configured} aria-describedby={flow?'password-help':undefined}/></label>}
   {flow&&<><p id="password-help" className="quality-note">Use at least 8 characters. Your organization may require a stronger password.</p><label>Confirm password<input type="password" autoComplete="new-password" value={confirmation} onChange={e=>setConfirmation(e.target.value)} required disabled={busy||!configured}/></label></>}
   <button type="submit" className="auth-primary" disabled={busy||!configured}>{busy?(flow?'Saving…':mode==='reset'?'Sending…':'Signing in…'):flow?'Save password':mode==='reset'?'Send reset link':'Sign in'}</button>
  </form>
  <p role="status" aria-live="polite">{notice}</p>
  {!flow&&<div className="auth-actions"><button type="button" disabled={busy} onClick={()=>switchMode(mode==='login'?'reset':'login')}>{mode==='login'?'Forgot password?':'Back to sign in'}</button>
   {mode==='login'&&microsoftEnabled&&<button type="button" disabled={busy||!configured} onClick={microsoft}>Continue with Microsoft</button>}</div>}
  {!flow&&mode==='login'&&<p className="quality-note">Need an account or collection access? Contact your organization administrator.</p>}
 </section>;
}
