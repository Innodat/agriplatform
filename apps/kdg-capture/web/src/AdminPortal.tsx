import {useLayoutEffect,useRef,useState,useSyncExternalStore} from 'react';
import {flushSync} from 'react-dom';
import type {AdminPortalController} from './admin-portal.js';
import type {AuditActorLabel} from './audit-presentation.js';
import './entry-screen.css';
import './admin-portal.css';

export function actorName(actor:Readonly<AuditActorLabel>):string {
 return actor.status==='resolved'?actor.display_name:actor.status==='unavailable'?'Name unavailable':'Names temporarily unavailable';
}
/** Explicit preview consumer; the host owns the controller and its disposal. */
export function AdminPortal({portal,from_date,to_date}:{portal:AdminPortalController;from_date:string;to_date:string}){
 const state=useSyncExternalStore(listener=>portal.subscribe(()=>flushSync(listener)),portal.snapshot,portal.snapshot);
 const heading=useRef<HTMLHeadingElement>(null),auditHeading=useRef<HTMLHeadingElement>(null),scroll=useRef(0);
 const lastNavigation=useRef<unknown>(null);
 const [from,setFrom]=useState(from_date),[to,setTo]=useState(to_date);
 // Each replacement page gets an entry point. Expanding audit leaves the button
 // focused; a completed fresh audit page focuses its semantic section heading.
 useLayoutEffect(()=>{
  if(state.kind==='history'||state.kind==='detail'){
   const navigation=state.kind==='history'?state.rows:state.audit;
   if(lastNavigation.current===navigation)return;lastNavigation.current=navigation;
   if(state.kind==='history'&&state.returnFocus){
    const row=document.getElementById('capture-'+state.returnFocus);
    if(row){row.focus({preventScroll:true});window.scrollTo({top:scroll.current});return;}
   }
   (state.kind==='detail'&&state.auditExpanded?auditHeading.current:heading.current)?.focus();
   window.scrollTo({top:0});
  }else lastNavigation.current=null;
 },[state]);
 const label=state.kind==='history'?'Observation history':state.kind==='detail'?'Observation details':state.kind==='checking'?'Checking access':state.kind==='loading'?'Loading review':state.kind==='offline'?'Connect to the internet':state.kind==='denied'?'Access denied':state.kind==='signed_out'?'Sign in to review':state.kind==='closed'?'Preview closed':'Review unavailable';
 const historyOutage=state.kind==='history'&&state.rows.some(row=>row.capturer.status==='temporarily_unavailable');
 return <div className="kdg-entry kdg-admin">
  <a className="kdg-entry-skip" href="#admin-main">Skip to review</a>
  <main id="admin-main">
   <p>KDG Capture · Administrator review preview</p>
   <h1 ref={heading} tabIndex={-1}>{label}</h1>
   <div role="status" aria-live="polite">{state.kind==='checking'?'Verifying current administrator access…':state.kind==='loading'?'Loading fresh authorized records…':state.kind==='history'?`${state.rows.length} observations on this page.`:state.kind==='detail'?'Observation loaded.':''}</div>
   {['history','detail'].includes(state.kind)&&<nav aria-label="Review actions"><button onClick={()=>void portal.refresh()}>Verify access and refresh history</button><button onClick={()=>void portal.signOut()}>Sign out</button></nav>}
   {state.kind==='history'&&<>
    <form aria-label="Observation dates" onSubmit={event=>{event.preventDefault();void portal.dates(from,to);}}>
     <label htmlFor="history-from">From observation date</label><input id="history-from" type="date" required value={from} onChange={event=>setFrom(event.target.value)}/>
     <label htmlFor="history-to">To observation date</label><input id="history-to" type="date" required value={to} min={from} onChange={event=>setTo(event.target.value)}/>
     <button type="submit">Apply dates</button>
    </form>
    {historyOutage&&<p role="status">Names temporarily unavailable. <button onClick={()=>void portal.retry()}>Retry</button></p>}
    {state.rows.length===0?<p>No observations in these dates.</p>:<ul className="kdg-admin-history">{state.rows.map(({capture,capturer})=><li key={capture.capture_id}><button id={'capture-'+capture.capture_id} onClick={()=>{scroll.current=window.scrollY;void portal.select(capture.capture_id);}}><span>{capture.child_label}</span><span>Observation date: {capture.observation_date}</span><span>Original capturer: {actorName(capturer)}</span></button></li>)}</ul>}
    <nav aria-label="History pages"><button onClick={()=>void portal.firstHistory()}>First history page</button>{state.next_cursor&&<button onClick={()=>void portal.nextHistory()}>Next history page</button>}</nav>
   </>}
   {state.kind==='detail'&&<>
    <button onClick={()=>void portal.back()}>Back to history</button>
    <h2>{state.capture.child_label}</h2>
    <dl><dt>Observation date</dt><dd>{state.capture.observation_date}</dd><dt>Original capturer</dt><dd>{actorName(state.audit.original_capturer)}</dd><dt>Questionnaire version</dt><dd>{state.capture.questionnaire_version}</dd></dl>
    <h2>Original questionnaire answers</h2>
    <ol className="kdg-admin-questions">{state.capture.definition.questions.map(question=>{
     const answer=state.capture.answers[question.id];
     return <li key={question.id}><h3>{question.label}</h3><p className="kdg-admin-answer">{!answer?'No answer':typeof answer.value==='boolean'?(answer.value?'Ja':'Nee'):String(answer.value)}</p>{question.type==='rating'&&<p>1 — {question.minimum_label}; 5 — {question.maximum_label}</p>}{question.type==='boolean'&&answer&&'details' in answer&&answer.details&&<dl><dt>{question.details_label}</dt><dd className="kdg-admin-answer">{answer.details}</dd></dl>}</li>;
    })}</ol>
    {state.audit.names.status==='temporarily_unavailable'&&<p role="status">Names temporarily unavailable. <button onClick={()=>void portal.retry()}>Retry</button></p>}
    <button aria-expanded={state.auditExpanded} aria-controls="observation-audit" onClick={()=>portal.toggleAudit()}>{state.auditExpanded?'Hide audit':'Show audit'}</button>
    {state.auditExpanded&&<section id="observation-audit" aria-labelledby="audit-heading"><h2 id="audit-heading" ref={auditHeading} tabIndex={-1}>Read-only audit</h2>
     <p>Names are current retained names.</p>
     <dl><dt>Current revision</dt><dd>{state.audit.current_revision}</dd><dt>Original creator</dt><dd>{actorName(state.audit.creation.actor)}</dd><dt>Created at</dt><dd><time dateTime={state.audit.creation.recorded_at}>{state.audit.creation.recorded_at}</time></dd><dt>Latest modifier</dt><dd>{actorName(state.audit.latest_modification.actor)}</dd><dt>Updated at</dt><dd><time dateTime={state.audit.latest_modification.recorded_at}>{state.audit.latest_modification.recorded_at}</time></dd></dl>
     {state.audit.events.length===0?<p>No earlier events on this page.</p>:<ol className="kdg-admin-events">{state.audit.events.map(event=><li key={event.revision}><h3>Revision {event.revision}</h3><dl><dt>Action</dt><dd>{event.command_type==='capture.create'?'Created':'Edited'}</dd><dt>Actual executor</dt><dd>{actorName(event.executor)}</dd>{event.initiator&&<><dt>Initiator</dt><dd>{actorName(event.initiator)}</dd></>}<dt>Recorded at</dt><dd><time dateTime={event.recorded_at}>{event.recorded_at}</time></dd></dl></li>)}</ol>}
     {state.audit.next_cursor&&<button onClick={()=>void portal.auditPage(state.audit.next_cursor!)}>Earlier audit events</button>}
    </section>}
   </>}
   {state.kind==='unavailable'&&<div role="alert"><p>Could not load a complete current review. Please try again.</p><button onClick={()=>void portal.retry()}>Retry</button><button onClick={()=>void portal.firstHistory()}>Return to history</button></div>}
   {state.kind==='denied'&&<div role="alert"><p>Administrator review is not available for your current access.</p><button onClick={()=>void portal.refresh()}>Retry access check</button></div>}
   {state.kind==='signed_out'&&<button onClick={()=>void portal.signIn()}>Sign in</button>}
   {state.kind==='offline'&&<p>Reconnect to verify administrator access and load fresh records.</p>}
  </main>
 </div>;
}
