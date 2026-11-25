import {useEffect,useLayoutEffect,useRef,useState} from 'react';
import {leaveClient,leaveNavigation,leaveSession} from './leave-session';
import {createDraftController,type DraftState} from './draft-controller';
import {draftId,type Organization} from './api/leave';
import {MyLeave} from './MyLeave';
import {DraftEditor,type SwitchSourceFailure} from './DraftEditor';
export function DraftContext({org,organizations,onSwitch,onSwitchSourceLost,onCurrent,onAccessDenied,paused=false,returnedDraft}:{org:string;organizations:readonly Organization[];onSwitch:(org:string)=>void;onSwitchSourceLost:(failure:SwitchSourceFailure)=>void;onCurrent?:()=>void;onAccessDenied?:(errorId?:string)=>void;paused?:boolean;returnedDraft?:string}){
 const [state,setState]=useState<DraftState>({kind:'loading'}),controller=useRef<ReturnType<typeof createDraftController>|null>(null);
 const requestedDraft=()=>{const prefix='/organizations/'+org+'/drafts/',candidate=location.pathname.startsWith(prefix)?location.pathname.slice(prefix.length):null;return candidate&&draftId(candidate)&&!location.search&&!location.hash?candidate:undefined;};
 useEffect(()=>{
  const current=createDraftController({client:leaveClient,acquire:leaveSession.acquire,publish:setState,navigate:draft=>{
   history.replaceState(null,'','/organizations/'+org+(draft?'/drafts/'+draft:''));
   if(draft)leaveNavigation.openDraft(org,draft,location);
   else leaveNavigation.leaveDraft(org);
  }});controller.current=current;
  queueMicrotask(()=>{if(controller.current===current)void current.load(org,requestedDraft());});
  return()=>{controller.current=null;current.dispose();};
 },[org]);
 const [backgroundDenied,setBackgroundDenied]=useState(false);
 const [savedOnly,setSavedOnly]=useState(returnedDraft);
 const region=useRef<HTMLElement>(null),focusMyLeaveAfterDiscard=useRef(false);
 useLayoutEffect(()=>{if(state.kind==='context')setBackgroundDenied(false);},[state]);
 useLayoutEffect(()=>{
  if(state.kind==='context'){
   if(focusMyLeaveAfterDiscard.current){
    focusMyLeaveAfterDiscard.current=false;
    const focused=document.activeElement;
    if(focused===document.body||focused?.matches('main h1'))region.current?.querySelector<HTMLElement>('[data-task-return]')?.focus();
   }
   onCurrent?.();
  }
  if(state.kind==='denied'){
   focusMyLeaveAfterDiscard.current=false;
   const current=controller.current,draft=state.draft;
   if(state.error_id==='authentication_required'&&draft&&current&&leaveSession.recoverDraft){
    leaveSession.recoverDraft(org,draft,result=>current.resumeOpen(draft,result));
   }else{
    leaveNavigation.leaveDraft(org);
    if(savedOnly)history.replaceState(null,'','/organizations/'+org);
    onAccessDenied?.(state.error_id);
   }
  }
  if(state.kind==='closed')leaveNavigation.leaveDraft(org);
 },[state,onCurrent,onAccessDenied]);
 const retainedBackground=useRef<import('./api/leave').DraftContextV1|null>(null);
 if(state.kind==='denied')retainedBackground.current=null;
 if(!backgroundDenied&&state.kind==='context')retainedBackground.current=state.value;
 if(!backgroundDenied&&state.kind==='opened'&&state.background)retainedBackground.current=state.background;
 const background=backgroundDenied?undefined:state.kind==='context'?state.value:state.kind==='opened'?(state.background??retainedBackground.current):state.kind==='loading'?retainedBackground.current:undefined;
 return <section ref={region} aria-label="My Leave">
 {background&&<MyLeave context={background} apply={()=>{leaveNavigation.leaveDraft(org);setSavedOnly(undefined);void controller.current?.apply();}} open={draft=>{leaveNavigation.leaveDraft(org);setSavedOnly(undefined);void controller.current?.open(draft);}}/>}
 {(state.kind==='loading'||state.kind==='working')&&<p role="status">{state.kind==='loading'?'Loading your application…':'Opening your application…'}</p>}
 {state.kind==='opened'&&state.value.state==='active'&&<DraftEditor key={state.value.draft_id} org={org} draft={state.value} choices={state.choices} firstChoiceEligible={state.firstChoiceEligible===true} organizations={organizations} onSwitch={onSwitch} onSwitchSourceLost={onSwitchSourceLost} paused={paused} savedOnly={savedOnly===state.value.draft_id} onDenied={()=>{leaveNavigation.leaveDraft(org);retainedBackground.current=null;setBackgroundDenied(true);}} onClosed={discarded=>{setSavedOnly(undefined);if(discarded){retainedBackground.current=null;focusMyLeaveAfterDiscard.current=true;}void controller.current?.close();}}/>}
 {state.kind==='unresolved'&&<><p role="alert">Opening your application is not yet confirmed.</p><button onClick={()=>void controller.current?.retry()}>Retry</button></>}
 {state.kind==='unavailable'&&<><p role="alert">Your application could not be loaded.</p><button onClick={()=>void controller.current?.retryOpen()}>Retry</button></>}
 {state.kind==='read_only'&&<p role="status">Your employment has ended. Your saved application is read only.</p>}
 {state.kind==='setup_required'&&<p role="status">Employment setup is needed before you can apply for leave. Your saved application is retained.</p>}
 {(state.kind==='read_only'||state.kind==='setup_required')&&<button onClick={()=>void controller.current?.close()}>Back to My Leave</button>}
 {state.kind==='denied'&&<><p role="alert">You do not currently have access to this application.</p>{savedOnly&&<button onClick={()=>{setSavedOnly(undefined);void controller.current?.close();}}>Back to My Leave</button>}</>}
 {(state.kind==='closed'||state.kind==='outdated')&&<><p role="status">{state.kind==='closed'?'This application was discarded.':'Your application context changed. Return to My Leave before applying again.'}</p><button onClick={()=>void controller.current?.close()}>Back to My Leave</button></>}
 </section>;
}
