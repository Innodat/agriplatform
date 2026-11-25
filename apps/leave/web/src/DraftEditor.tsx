import {useLayoutEffect,useRef,useState} from 'react';
import {TaskSurface,DraftSaveStatus,DraftExitConfirmation,DateEntry,DateRange,dateEntryValue,dateEntryProblem} from '@platform/ui-business';
import {leaveClient,leaveSession} from './leave-session';
import {createDraftEditorController,type EditorState} from './draft-editor-controller';
import type {DraftRead,DraftChoicesResponse,Organization} from './api/leave';
import type {DraftInput} from './draft-input';
import {DraftChoices} from './DraftChoices';
type Active=Extract<DraftRead,{state:'active'}>;
export type SwitchSourceFailure='denied'|'auth_required';
const fieldId=(path:string)=>'draft-'+path.replaceAll('.','-');
function hoursProblem(text:string){
 if(/^ *$/.test(text))return null;
 if(text.length>64)return 'Use at most 32 characters. Your input has not been shortened.';
 const match=/^ *([0-9]+)(?:\.([0-9]+))? *$/.exec(text);
 if(match){const fraction=match[2]??'',denominator=10n**BigInt(fraction.length),amount=BigInt(match[1]!)*denominator+BigInt(fraction||'0');if(amount>0n&&(amount*2n)%denominator===0n)return null;}
 return 'Enter positive hours in 30-minute increments, using a decimal point. Your entered text is preserved.';
}
export function DraftEditor({org,draft,choices,firstChoiceEligible,organizations,onClosed,onDenied,onSwitch,onSwitchSourceLost,paused=false,savedOnly=false}:{org:string;draft:Active;choices:DraftChoicesResponse;firstChoiceEligible:boolean;organizations:readonly Organization[];onClosed:(discarded:boolean)=>void;onDenied:()=>void;onSwitch:(org:string)=>void;onSwitchSourceLost:(failure:SwitchSourceFailure)=>void;paused?:boolean;savedOnly?:boolean}){
 const [state,setState]=useState<EditorState>({input:draft.input,revision:draft.revision,generation:0,status:draft.editability.status==='editable'?'saved':'read_only',exit:'none',discard:'none',discardFailed:false,problems:[],reviewing:false,reviewFailed:false});
 const [firstChoice,setFirstChoice]=useState(firstChoiceEligible),[touched,setTouched]=useState<Set<string>>(()=>new Set());
 const [choiceSeed,setChoiceSeed]=useState({choices,selected:draft.input.leave_type_id}),[renewed,setRenewed]=useState(false);
 const revealedOtherFields=useRef(new Set<string>());
 const controller=useRef<ReturnType<typeof createDraftEditorController>|null>(null);
 const discardOpener=useRef<HTMLButtonElement|null>(null),reviewButton=useRef<HTMLButtonElement|null>(null);
 const exitOpener=useRef<HTMLElement|null>(null),switchTarget=useRef<string|null>(null);
 const callbacks=useRef({onClosed,onDenied,onSwitch,onSwitchSourceLost});callbacks.current={onClosed,onDenied,onSwitch,onSwitchSourceLost};
 useLayoutEffect(()=>{const current=createDraftEditorController({org,initial:draft,client:leaveClient,acquire:leaveSession.acquire,publish:setState});controller.current=current;return()=>{controller.current=null;current.dispose();};},[org,draft.draft_id]);
 const previousExit=useRef(state.exit),previousDiscard=useRef(state.discard),exitHandled=useRef(false);
 useLayoutEffect(()=>{
  const current=controller.current?.snapshot();
  if(!current||exitHandled.current)return;
  const target=switchTarget.current;
  const canRecover=typeof leaveSession.recoverDraft==='function';
  if(target&&current.status==='auth_required'&&canRecover){
   switchTarget.current=null;
   controller.current?.stay();
  }else if(target&&(current.status==='denied'||current.status==='auth_required')){
   exitHandled.current=true;
   callbacks.current.onSwitchSourceLost(current.status);
   return;
  }
  if(current.status==='auth_required'){
   const editor=controller.current;
   if(!editor)return;
   leaveSession.recoverDraft?.(org,draft.draft_id,result=>{
    if(controller.current!==editor)return;
    if(!result.ok){editor.protectedFailure(result.error_id);return;}
    if('choices' in result.value)setChoiceSeed({choices:result.value.choices,selected:result.value.draft.input.leave_type_id});
    setFirstChoice(false);setRenewed(true);
    void editor.resumeAfterAuth(result.value.draft);
   },!editor.hasRenewedPendingSave());
  }
  if(current.status==='denied')callbacks.current.onDenied();
  if(current.exit==='closed'){
   exitHandled.current=true;
   if(target)callbacks.current.onSwitch(target);
   else callbacks.current.onClosed(current.discard==='complete'||current.status==='closed');
  }
  if(previousExit.current==='confirm'&&current.exit==='none'){
   const opener=exitOpener.current;
   if(opener?.isConnected&&!opener.closest('[inert]'))opener.focus();
   else document.getElementById('task-title')?.focus();
  }
  if(previousDiscard.current!=='none'&&current.discard==='none'){
   if(discardOpener.current?.isConnected&&!discardOpener.current.disabled)discardOpener.current.focus();
   else if(reviewButton.current)reviewButton.current.focus();
   else document.getElementById('task-title')?.focus();
  }
  previousExit.current=current.exit;previousDiscard.current=current.discard;
 },[state.exit,state.status,state.discard]);
 const input=state.input,editable=['saved','dirty','saving','failed'].includes(state.status);
 const change=(next:DraftInput)=>controller.current?.change(next);
 const errors=new Map(state.problems.map(problem=>[problem.path,problem.message]));
 const dateErrors=(path:string,text:string)=>{if(touched.has(path)&&!errors.has(path)){const error=dateEntryProblem(text);if(error)errors.set(path,error);}};
 if(input){
  if(input.duration_mode==='full_days'){dateErrors('full_days.start',input.full_days.start.text);dateErrors('full_days.end',input.full_days.end.text);const start=dateEntryValue(input.full_days.start.text),end=dateEntryValue(input.full_days.end.text);if(start&&end&&end<start&&touched.has('full_days.end'))errors.set('full_days.end','End date must be on or after start date. Your dates have not been swapped.');}
  if(input.duration_mode==='half_day')dateErrors('half_day.date',input.half_day.date.text);
  if(input.duration_mode==='hours'){dateErrors('hours.date',input.hours.date.text);if(touched.has('hours.duration')){const error=hoursProblem(input.hours.duration.text);if(error)errors.set('hours.duration',error);}}
 }
 const blur=(path:string)=>()=>setTouched(previous=>new Set([...previous,path]));
 const requestExit=(target:string|null,opener:Element|null=document.activeElement)=>{
  if(controller.current?.snapshot().discard!=='none')return;
  switchTarget.current=target;
  exitOpener.current=opener instanceof HTMLElement?opener:null;
  void controller.current?.close();
 };
 const requestClose=()=>requestExit(null);
 const dateProps=(path:string,label:string,value:string,onChange:(text:string)=>void)=>({id:fieldId(path),label,value,onChange,onBlur:blur(path),error:errors.get(path),disabled:!editable});
 const status=state.status==='saved'?'saved':state.status==='saving'?'saving':state.status==='failed'?'failed':'dirty';
 for(const problem of state.problems)if(problem.path.includes('.')&&problem.path.split('.')[0]!==input?.duration_mode)revealedOtherFields.current.add(problem.path);
 const inactiveProblems=[...revealedOtherFields.current].filter(path=>path.split('.')[0]!==input?.duration_mode).map(path=>({path,message:errors.get(path)}));
 const switching=switchTarget.current!==null;
 const organizationHeading=state.status==='denied'||state.status==='auth_required'?null:organizations.length<2?organizations[0]?.name:<label>Choose organization
  <select value={org} aria-disabled={state.exit==='waiting'||undefined} onChange={event=>{
   const target=event.currentTarget.value;
   if(state.exit==='none'&&target!==org)requestExit(target,event.currentTarget);
  }}>
   {organizations.map(organization=><option key={organization.org_id} value={organization.org_id}>{organization.name}</option>)}
  </select>
 </label>;
 const discardDialog=()=>{
  const editor=controller.current;
  switch(state.discard){
   case 'confirm':return <DraftExitConfirmation question="Discard draft?" description="This removes the entire saved draft and any unsaved changes." stayLabel="Cancel" stay={()=>editor?.cancelDiscard()} leaveLabel="Discard draft" leave={()=>void editor?.confirmDiscard()} destructive/>;
   case 'running':return <DraftExitConfirmation question="Confirming discard…"/>;
   case 'save_retry':return <DraftExitConfirmation question="Your last save could not be confirmed." description="Confirm that save before discarding the draft." stayLabel="Cancel" stay={()=>editor?.cancelDiscard()} leaveLabel="Retry save" leave={()=>void editor?.retryDiscard()}/>;
   case 'discard_retry':return <DraftExitConfirmation question="Discard could not be confirmed." description="Retry to check the outcome of this discard." leaveLabel="Retry discard" leave={()=>void editor?.retryDiscard()}/>;
  }
 };
 const confirmation=discardDialog()??(state.exit==='confirm'?<DraftExitConfirmation
  question={switching?'Your latest changes may not be saved. Switch anyway?':undefined}
  leaveLabel={switching?'Switch anyway':undefined}
  stay={()=>{switchTarget.current=null;controller.current?.stay();}}
  leave={()=>controller.current?.closeAnyway()}
 />:undefined);
 if(paused)return null;
 return <TaskSurface title="Apply for leave" backLabel="Back to My Leave" onClose={requestClose} headerContent={organizationHeading} footer={<>
 {input&&editable&&<DraftSaveStatus status={status} retry={()=>void controller.current?.retry()}/>}
 {editable&&<button ref={discardOpener} type="button" disabled={state.exit!=='none'} onClick={()=>controller.current?.requestDiscard()}>Discard draft</button>}
 <button type="button" onClick={requestClose}>{['closed','denied'].includes(state.status)?'Back to My Leave':'Close'}</button>
 </>} confirmation={confirmation}>
 {state.status==='denied'?<p role="alert">You do not currently have access to this application.</p>:<>
 {savedOnly&&input&&<p role="status">Only your saved changes were restored.</p>}
 {state.discardFailed&&<p role="alert">The draft could not be discarded. Your application is still open.</p>}
 {state.status==='conflict'&&<p role="alert">Your saved application changed. Saving is paused. Your local input is retained until you review the saved draft.</p>}
 {state.status==='closed'&&<p role="status">{state.reason==='closure_unattributed'?'This application was discarded.':'This application was discarded elsewhere. Your local input has not been saved as a new draft.'}</p>}
 {state.status==='read_only'&&<p role="status">{state.reason==='employment_ended'?'Your employment has ended.':'Your current access or employment setup permits reading only.'} Saving is paused.</p>}
 {state.status==='setup_required'&&<p role="status">Employment setup is needed before editing can continue. Your saved application is retained.</p>}
 {state.status==='auth_required'&&<p role="alert">Please sign in again to continue. Saving is paused. Unsaved input may not survive sign-in.</p>}
 {['conflict','read_only','setup_required','auth_required'].includes(state.status)&&<button ref={reviewButton} type="button" disabled={state.reviewing} onClick={()=>{setFirstChoice(false);setTouched(new Set());void controller.current?.review();}}>{state.reviewing?'Loading saved draft…':'Review saved draft'}</button>}
 {state.reviewFailed&&<p role="alert">Your saved application could not be checked. Your local input is unchanged. Try Review saved draft again.</p>}
 {draft.setup_notices.map(notice=><p key={notice.code}>Your work timezone {notice.code==='work_timezone_missing'?'is not set up':'setup is invalid'}. This does not prevent preserving leave input.</p>)}
 {input&&<>
 {errors.size>1&&<nav aria-label="Input errors"><p>Please check these entries. Bounded incomplete input can still be saved.</p><ul>{[...errors].map(([path,message])=><li key={path}><a href={'#'+fieldId(path)} onClick={e=>{e.preventDefault();document.getElementById(fieldId(path))?.focus();}}>{message}</a></li>)}</ul></nav>}
 <DraftChoices org={org} initialChoices={choiceSeed.selected===input.leave_type_id?choiceSeed.choices:undefined} input={input} inputGeneration={state.generation} editable={editable} firstChoiceEligible={firstChoice} preserveStoredChoices={savedOnly||renewed} onChange={(next,eligible)=>{setFirstChoice(eligible);change(next);}} onProtectedFailure={error=>controller.current?.protectedFailure(error)}/>
 {input.duration_mode==='full_days'&&<DateRange start={dateProps('full_days.start','Start date',input.full_days.start.text,text=>change({...input,full_days:{...input.full_days,start:{...input.full_days.start,text}}}))} end={dateProps('full_days.end','End date',input.full_days.end.text,text=>change({...input,full_days:{...input.full_days,end:{...input.full_days.end,text}}}))}/>}
 {input.duration_mode==='half_day'&&<DateEntry {...dateProps('half_day.date','Date',input.half_day.date.text,text=>change({...input,half_day:{date:{...input.half_day.date,text}}}))}/>}
 {input.duration_mode==='hours'&&<><DateEntry {...dateProps('hours.date','Date',input.hours.date.text,text=>change({...input,hours:{...input.hours,date:{...input.hours.date,text}}}))}/><div className="form-field"><label htmlFor={fieldId('hours.duration')}>Hours</label><input id={fieldId('hours.duration')} type="text" inputMode="decimal" value={input.hours.duration.text} disabled={!editable} onChange={e=>change({...input,hours:{...input.hours,duration:{...input.hours.duration,text:e.target.value}}})} onBlur={blur('hours.duration')} aria-invalid={errors.has('hours.duration')} aria-describedby={'hours-hint'+(errors.has('hours.duration')?' hours-error':'')}/><p id="hours-hint" className="field-hint">Use a decimal point and 30-minute increments, for example 1.5.</p>{errors.has('hours.duration')&&<p className="field-error" id="hours-error">{errors.get('hours.duration')}</p>}</div></>}
 {inactiveProblems.length>0&&<section aria-label="Other entries to check"><h4>Other entries to check</h4><p>These entries are kept when you change duration. Shorten them so all your input can be saved.</p>{inactiveProblems.map(problem=>{
  const path=problem.path;
  if(path==='full_days.start'||path==='full_days.end'){const field=path==='full_days.start'?'start':'end';return <DateEntry key={path} {...dateProps(path,`Saved full days ${field} date`,input.full_days[field].text,text=>change({...input,full_days:{...input.full_days,[field]:{...input.full_days[field],text}}}))}/>;}
  if(path==='half_day.date')return <DateEntry key={path} {...dateProps(path,'Saved half-day date',input.half_day.date.text,text=>change({...input,half_day:{date:{...input.half_day.date,text}}}))}/>;
  if(path==='hours.date')return <DateEntry key={path} {...dateProps(path,'Saved hours date',input.hours.date.text,text=>change({...input,hours:{...input.hours,date:{...input.hours.date,text}}}))}/>;
  if(path==='hours.duration')return <div key={path}><label htmlFor={fieldId(path)}>Saved hours</label><input id={fieldId(path)} value={input.hours.duration.text} disabled={!editable} onChange={e=>change({...input,hours:{...input.hours,duration:{...input.hours.duration,text:e.target.value}}})} aria-invalid={errors.has(path)} aria-describedby={errors.has(path)?'inactive-hours-error':undefined}/>{problem.message&&<p id="inactive-hours-error" className="field-error">{problem.message}</p>}</div>;
  return null;
 })}</section>}
 <div className="form-field"><label htmlFor={fieldId('note')}>Note (optional)</label><textarea id={fieldId('note')} value={input.note} disabled={!editable} onChange={e=>change({...input,note:e.target.value})} aria-invalid={errors.has('note')} aria-describedby={'note-hint'+(errors.has('note')?' note-error':'')}/><p id="note-hint" className="field-hint">Up to 4,000 characters.</p>{errors.has('note')&&<p id="note-error" className="field-error">{errors.get('note')}</p>}</div>
 {errors.has('input')&&<p role="alert">{errors.get('input')}</p>}
 </>}
 </>}
 </TaskSurface>;
}
