// Owner entry and tab-local Leave workspace.
import {useEffect,useLayoutEffect,useRef,useState,useSyncExternalStore} from 'react';
import {leaveSession,leaveClient,leaveNavigation} from './leave-session';
import {createSelectionController,createLanguageController,type LanguageState,type SelectionState} from './leave-controller';
import {draftId,type Organizations} from './api/leave';
import {Launcher} from './Launcher';
import {DraftContext} from './DraftContext';
function Workspace({choices,paused=false}:{choices:Organizations;paused?:boolean}){
 const [selected,setSelected]=useState('');
 const [transition,setTransition]=useState<SelectionState>({kind:'idle'});
 const [restoringSource,setRestoringSource]=useState(false),[sourceDenied,setSourceDenied]=useState(false);
 const [sourceCheck,setSourceCheck]=useState(0);
 const [returnUnavailable,setReturnUnavailable]=useState(false),[returnRetry,setReturnRetry]=useState(false);
 const [selectionAbandoned,setSelectionAbandoned]=useState(false);
 const [preference,setPreference]=useState<LanguageState>({language:null,desired:null,notice:'loading'});
 const controller=useRef<ReturnType<typeof createSelectionController>|null>(null);
 const languageController=useRef<ReturnType<typeof createLanguageController>|null>(null);
 const activeOrganization=useRef(''),entrySuperseded=useRef(false);
 const returnCandidate=useRef<{org:string;draft:string}|null>(null);
 const heading=useRef<HTMLHeadingElement>(null),organizationHeading=useRef<HTMLHeadingElement>(null);
 const selecting=transition.kind==='working'||transition.kind==='unresolved';
 const setActive=(org:string)=>{activeOrganization.current=org;setSelected(org);};
 const returnToSource=()=>{
  const source=activeOrganization.current;
  history.replaceState(null,'',source?'/organizations/'+source:'/');
  if(source)setSourceCheck(previous=>previous+1);
  setRestoringSource(Boolean(source));
 };
 const rejectSource=()=>{
  leaveNavigation.clear();
  history.replaceState(null,'','/');
  setActive('');
  setRestoringSource(false);
  setSourceDenied(true);
 };
 const recoverAuthentication=()=>{
  leaveNavigation.suspend();
  history.replaceState(null,'','/');
  setActive('');
  setRestoringSource(false);
  void leaveSession.retry();
 };
 useLayoutEffect(()=>{
  if(selecting||restoringSource||sourceDenied||transition.kind==='denied'&&!selected)organizationHeading.current?.focus();
  else if(selected)heading.current?.focus();
 },[selected,selecting,restoringSource,sourceDenied,transition.kind]);
 useLayoutEffect(()=>{
  entrySuperseded.current=false;
  const current=createSelectionController({client:leaveClient,acquire:leaveSession.acquire,publish:next=>{
   setTransition(next);
   if(next.kind==='committed'&&next.org){
    const lease=leaveSession.acquire();
    if(!lease||!lease.isCurrent()){
     lease?.release();
     setActive('');
     return;
    }
    leaveNavigation.establish(lease.session.account_id,next.org,next.operation);
    lease.release();
    const prefix='/organizations/'+next.org+'/drafts/';
    const candidate=location.pathname.startsWith(prefix)?location.pathname.slice(prefix.length):'';
    const returned=returnCandidate.current?.org===next.org?returnCandidate.current.draft:undefined;
    returnCandidate.current=null;
    if(returned)history.replaceState(null,'',prefix+returned);
    else if(!draftId(candidate)||location.search||location.hash)history.replaceState(null,'','/organizations/'+next.org);
    setActive(next.org);
    setRestoringSource(false);
   }
   if(next.kind==='denied'){
    if(returnCandidate.current){leaveNavigation.refuseReturn();setReturnUnavailable(true);returnCandidate.current=null;}
    if(next.error_id==='authentication_required')recoverAuthentication();
    else returnToSource();
   }
  }});
  controller.current=current;
  const entryLease=leaveSession.acquire();
  if(entryLease){
   const previous=leaveNavigation.returnIntent();
   if(previous&&previous.account_id!==entryLease.session.account_id){
    // Clear the prior account's URL before another mount can treat it as a bookmark.
    leaveNavigation.refuseReturn();
    if(previous.draft_id)setReturnUnavailable(true);
    history.replaceState(null,'','/');
   }
   void leaveNavigation.target(entryLease.session.account_id,choices.organizations,location,async org=>{
    const result=await leaveClient.organizations(entryLease.session.access_token,entryLease.signal);
    if(!result.ok)return ['access_denied','identity.verification_required','authentication_required'].includes(result.error_id)?null:'unavailable';
    return result.value.organizations.some(o=>o.org_id===org)?{account_id:entryLease.session.account_id,scope_id:org}:null;
   },entryLease).then(target=>{
    if(!entryLease.isCurrent()||entrySuperseded.current||controller.current!==current)return;
    if(target.kind==='established'&&target.org)setActive(target.org);
    else if(target.kind==='select'&&target.org){
     returnCandidate.current=target.draft?{org:target.org,draft:target.draft}:null;
     void current.select(target.org,target.operation);
    }else if(target.kind==='retry')setReturnRetry(true);
    else{
     if(target.returnUnavailable)setReturnUnavailable(true);
     history.replaceState(null,'','/');
    }
   }).finally(()=>entryLease.release());
  }
  const language=createLanguageController({client:leaveClient,acquire:leaveSession.acquire,publish:setPreference});
  languageController.current=language;
  void language.load();
  return()=>{language.dispose();languageController.current=null;controller.current=null;current.dispose();};
 },[choices]);
 const selectOrganization=(target:string)=>{
  if(target===selected||!choices.organizations.some(organization=>organization.org_id===target))return;
  entrySuperseded.current=true;
  leaveNavigation.supersedeReturn?.();
  if(selected)leaveNavigation.leaveDraft(selected);
  returnCandidate.current=null;
  setReturnUnavailable(false);
  setReturnRetry(false);
  setSelectionAbandoned(false);
  setSourceDenied(false);
  void controller.current?.select(target);
 };
 const stay=()=>{
  entrySuperseded.current=true;
  leaveNavigation.supersedeReturn?.();
  returnCandidate.current=null;
  setSelectionAbandoned(true);
  controller.current?.stay();
  returnToSource();
 };
 const org=choices.organizations.find(organization=>organization.org_id===selected);
 return <>
 <section aria-labelledby="organization-heading"><h2 id="organization-heading" ref={organizationHeading} tabIndex={-1}>Organization</h2>
 {choices.organizations.length===0?<p>You do not have access to a Leave organization.</p>:choices.organizations.length===1?
  (returnUnavailable||selectionAbandoned)&&!selected?<button onClick={()=>selectOrganization(choices.organizations[0]!.org_id)}>Continue to {choices.organizations[0]!.name}</button>:<p>{choices.organizations[0]!.name}</p>:
  <label>Choose organization<select value={selecting?transition.org??selected:selected} onChange={event=>{if(event.currentTarget.value)selectOrganization(event.currentTarget.value);}}><option value="">Choose an organization</option>{choices.organizations.map(o=><option key={o.org_id} value={o.org_id}>{o.name}</option>)}</select></label>}
 {transition.kind==='working'&&<p role="status">Confirming organization access…</p>}
 {transition.kind==='unresolved'&&<><p role="alert">Organization selection could not be confirmed.</p><button onClick={()=>void controller.current?.retry()}>Retry selection</button></>}
 {selecting&&<button onClick={stay}>Stay</button>}
 {transition.kind==='denied'&&transition.error_id!=='authentication_required'&&<p role="alert">You do not currently have access to the selected organization.</p>}
 {sourceDenied&&<p role="alert">You no longer have access to the previous organization.</p>}
 {returnUnavailable&&<p role="status">Your previous draft could not be reopened.{choices.organizations.length>0?' Choose an available organization to continue.':''}</p>}
 {returnRetry&&<><p role="alert">Current access to your previous draft could not be checked.</p><button onClick={()=>void leaveSession.retry()}>Retry draft return</button></>}
 <button onClick={()=>void leaveSession.retry()}>Refresh organization access</button></section>
 {org&&!selecting&&<section aria-labelledby={restoringSource?undefined:'workspace-heading'}>
  {!restoringSource&&<><h2 id="workspace-heading" ref={heading} tabIndex={-1}>{org.name}</h2><p>Welcome to Leave.</p></>}
  <DraftContext key={org.org_id+'-'+sourceCheck} org={org.org_id} organizations={choices.organizations} onSwitch={selectOrganization} paused={paused} returnedDraft={leaveNavigation.returnedDraft(org.org_id,location)}
   onSwitchSourceLost={failure=>{if(failure==='auth_required')recoverAuthentication();else returnToSource();}}
   onCurrent={restoringSource?()=>setRestoringSource(false):undefined}
   onAccessDenied={restoringSource?errorId=>{if(errorId==='authentication_required')recoverAuthentication();else rejectSource();}:undefined}/>
 </section>}
 <section aria-labelledby="language-heading"><h2 id="language-heading">Language</h2>{preference.language?<label>Preferred language<select value={preference.desired??preference.language.preferred_locale} onChange={e=>void languageController.current?.change(e.target.value as 'en'|'pt')}><option value="en">English</option><option value="pt">Português</option></select></label>:<p>Language preference is unavailable.</p>}<p role="status">{preference.notice==='saving'?'Saving language…':preference.notice==='retry'?'Language not saved. Retry.':preference.language?.preferred_locale==='pt'?'Portuguese is preferred. English is shown where translation is unavailable.':''}</p>{preference.notice==='retry'&&<button onClick={()=>void languageController.current?.retry()}>Retry language</button>}</section>
 </>;
}
export function App(){
 const snapshot=useSyncExternalStore(leaveSession.subscribe,leaveSession.snapshot);
 useEffect(()=>{void leaveSession.start();},[]);
 const state=snapshot.state;
 const recovery=snapshot.draftRecovery,recoveryNotice=useRef<HTMLParagraphElement>(null);
 useLayoutEffect(()=>{if(recovery&&recovery!=='checking')recoveryNotice.current?.focus();},[recovery]);
 const signIn=()=><><button onClick={()=>void leaveSession.signIn()}>Sign in with Microsoft</button><button className="account-switch" onClick={()=>void leaveSession.signIn(true)}>Use another Microsoft account</button></>;
 return <><a className="skip" href="#main">Skip to content</a><header><span className="brand">Leave</span>{!recovery&&<Launcher/>}{state.kind==='authorized'&&!recovery&&<button onClick={()=>void leaveSession.signOut()}>Sign out</button>}</header><main id="main"><h1>Leave</h1>
 {!leaveSession.configured?<p role="alert">Sign-in configuration is unavailable.</p>:state.kind==='authorized'?<div hidden={Boolean(recovery)}><Workspace key={snapshot.revision} choices={state.context} paused={Boolean(recovery)}/></div>:recovery?null:state.kind==='checking'?<p role="status">Checking current access…</p>:<>{state.kind==='access_denied'?<p role="alert">You do not have access to Leave.</p>:state.kind==='authorization_unavailable'||state.kind==='invalid_response'?<p role="alert">Current access could not be checked.</p>:<p>Sign in to continue.</p>}{signIn()}<button onClick={()=>void leaveSession.retry()}>Retry access</button></>}
 {recovery==='checking'&&<p role="status">Saving is paused while we check your session…</p>}
 {recovery==='unavailable'&&<><p role="alert" ref={recoveryNotice} tabIndex={-1}>Your session could not be renewed. Saving is paused.</p><button onClick={()=>void leaveSession.retry()}>Retry access</button></>}
 {recovery==='authentication_required'&&<><p role="alert" ref={recoveryNotice} tabIndex={-1}>Sign in again to continue. Saving is paused and your latest changes may be lost.</p>{signIn()}</>}
 </main></>;
}
