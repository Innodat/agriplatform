// Owner entry UI. E1-A1 has no request draft or submission surface.
import {useEffect,useLayoutEffect,useRef,useState,useSyncExternalStore} from 'react';
import {leaveSession,leaveClient,leaveNavigation} from './leave-session';
import {createSelectionController,createLanguageController,type LanguageState,type SelectionState} from './leave-controller';
import type {Organizations,Language} from './api/leave';
import {Launcher} from './Launcher';
function Workspace({choices}:{choices:Organizations}){
 const [selected,setSelected]=useState(''),[transition,setTransition]=useState<SelectionState>({kind:'idle'}),[preference,setPreference]=useState<LanguageState>({language:null,desired:null,notice:'loading'});
 const controller=useRef<ReturnType<typeof createSelectionController>|null>(null),languageController=useRef<ReturnType<typeof createLanguageController>|null>(null);
 const heading=useRef<HTMLHeadingElement>(null);
 useLayoutEffect(()=>{if(selected)heading.current?.focus();},[selected]);
 useLayoutEffect(()=>{
  const current=createSelectionController({client:leaveClient,acquire:leaveSession.acquire,publish:next=>{setTransition(next);if(next.kind==='committed'&&next.org){setSelected(next.org);const lease=leaveSession.acquire();if(lease){leaveNavigation.establish(lease.session.account_id,next.org);lease.release();globalThis.history.replaceState(null,'','/organizations/'+next.org);}}if(next.kind==='denied'){setSelected('');void leaveSession.retry();}}});controller.current=current;
  const entryLease=leaveSession.acquire();if(entryLease){void leaveNavigation.target(entryLease.session.account_id,choices.organizations,globalThis.location,async org=>{const result=await leaveClient.organizations(entryLease.session.access_token,entryLease.signal);return result.ok&&result.value.organizations.some(o=>o.org_id===org)?{account_id:entryLease.session.account_id,scope_id:org}:null;},entryLease).then(target=>{if(!entryLease.isCurrent())return;if(target.kind==='established'&&target.org)setSelected(target.org);else if(target.kind==='select'&&target.org)void current.select(target.org);else globalThis.history.replaceState(null,'','/');}).finally(()=>entryLease.release());}
  const language=createLanguageController({client:leaveClient,acquire:leaveSession.acquire,publish:setPreference});languageController.current=language;void language.load();
  return()=>{language.dispose();languageController.current=null;controller.current=null;current.dispose();};
 },[choices]);
 const org=choices.organizations.find(o=>o.org_id===selected);
 return <>
 <section aria-labelledby="organization-heading"><h2 id="organization-heading">Organization</h2>
 {choices.organizations.length===0?<p>You do not have access to a Leave organization.</p>:choices.organizations.length===1?<p>{choices.organizations[0]!.name}</p>:<label>Choose organization<select value={transition.org??selected} onChange={e=>{if(e.target.value)void controller.current?.select(e.target.value);}}><option value="">Choose an organization</option>{choices.organizations.map(o=><option key={o.org_id} value={o.org_id}>{o.name}</option>)}</select></label>}
 {transition.kind==='working'&&<><p role="status">Confirming organization access…</p><button onClick={()=>{controller.current?.stay();heading.current?.focus();}}>Stay</button></>}
 {transition.kind==='unresolved'&&<><p role="alert">Organization selection could not be confirmed.</p><button onClick={()=>void controller.current?.retry()}>Retry selection</button><button onClick={()=>{controller.current?.stay();heading.current?.focus();}}>Stay</button></>}
 <button onClick={()=>void leaveSession.retry()}>Refresh organization access</button></section>
 {org&&<section aria-labelledby="workspace-heading"><h2 id="workspace-heading" ref={heading} tabIndex={-1}>{org.name}</h2><p>Welcome to Leave.</p></section>}
 <section aria-labelledby="language-heading"><h2 id="language-heading">Language</h2>{preference.language?<label>Preferred language<select value={preference.desired??preference.language.preferred_locale} onChange={e=>void languageController.current?.change(e.target.value as 'en'|'pt')}><option value="en">English</option><option value="pt">Português</option></select></label>:<p>Language preference is unavailable.</p>}<p role="status">{preference.notice==='saving'?'Saving language…':preference.notice==='retry'?'Language not saved. Retry.':preference.language?.preferred_locale==='pt'?'Portuguese is preferred. English is shown where translation is unavailable.':''}</p>{preference.notice==='retry'&&<button onClick={()=>void languageController.current?.retry()}>Retry language</button>}</section>
 </>;
}
export function App(){
 const snapshot=useSyncExternalStore(leaveSession.subscribe,leaveSession.snapshot);
 useEffect(()=>{void leaveSession.start();},[]);
 const state=snapshot.state;
 return <><a className="skip" href="#main">Skip to content</a><header><span className="brand">Leave</span><Launcher/>{state.kind==='authorized'&&<button onClick={()=>void leaveSession.signOut()}>Sign out</button>}</header><main id="main"><h1>Leave</h1>
 {!leaveSession.configured?<p role="alert">Sign-in configuration is unavailable.</p>:state.kind==='authorized'?<Workspace key={snapshot.revision} choices={state.context}/>:state.kind==='checking'?<p role="status">Checking current access…</p>:<>{state.kind==='access_denied'?<p role="alert">You do not have access to Leave.</p>:state.kind==='authorization_unavailable'||state.kind==='invalid_response'?<p role="alert">Current access could not be checked.</p>:<p>Sign in to continue.</p>}<button onClick={()=>void leaveSession.signIn()}>Sign in with Microsoft</button><button className="account-switch" onClick={()=>void leaveSession.signIn(true)}>Use another Microsoft account</button><button onClick={()=>void leaveSession.retry()}>Retry access</button></>}
 </main></>;
}
