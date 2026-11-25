import {useEffect,useLayoutEffect,useRef,useState} from 'react';
import {leaveClient,leaveSession} from './leave-session';
import type {DraftChoice,DraftChoicesResponse} from './api/leave';
import type {DraftInput,DurationMode} from './draft-input';
import {emptyInput} from './draft-input';
import {chooseType,repairChoices} from './choice-selection';
import {createChoicesController,selectionNotice,type ChoicesState} from './choices-controller';
const labels:Record<DurationMode,string>={full_days:'Full days',half_day:'Half day',hours:'Hours'};
export type DraftChoicesProps={org:string;input:DraftInput;inputGeneration:number;editable:boolean;firstChoiceEligible:boolean;initialChoices?:DraftChoicesResponse;preserveStoredChoices?:boolean;onChange:(input:DraftInput,firstChoiceEligible:boolean)=>void;onProtectedFailure?:(error:string)=>void};
export function DraftChoices({org,input,inputGeneration,editable,firstChoiceEligible,initialChoices,preserveStoredChoices=false,onChange,onProtectedFailure}:DraftChoicesProps){
 const [state,setState]=useState<ChoicesState>(initialChoices?{kind:'resolved',value:initialChoices,inputGeneration}: {kind:'loading'}),[catalogue,setCatalogue]=useState<DraftChoicesResponse|null>(initialChoices??null),[notice,setNotice]=useState<string|null>(null);
 const latest=useRef({input,inputGeneration,editable,preserveStoredChoices,onChange,onProtectedFailure});latest.current={input,inputGeneration,editable,preserveStoredChoices,onChange,onProtectedFailure};
 const repairedSelection=useRef<{value:string|null}|null>(null),initialSeed=useRef(initialChoices),initialReload=useRef(false),reloadTimer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const cancelReload=()=>{if(reloadTimer.current!==null)clearTimeout(reloadTimer.current);reloadTimer.current=null;};
 const controller=useRef<ReturnType<typeof createChoicesController>|null>(null);
 useLayoutEffect(()=>{
  initialReload.current=false;initialSeed.current=initialChoices;cancelReload();
  const current=createChoicesController({client:leaveClient,acquire:leaveSession.acquire,initial:initialChoices,publish:value=>{
   setState(value);
   if(value.kind==='denied')latest.current.onProtectedFailure?.(value.error_id??'authentication_required');
   if(value.kind!=='resolved'||value.inputGeneration!==latest.current.inputGeneration)return;
   setCatalogue(value.value);
   const repair=repairChoices(latest.current.input,value.value,latest.current.editable);setNotice(previous=>selectionNotice(previous,repair.notice,repair.input));
   if(!latest.current.preserveStoredChoices&&repair.input!==latest.current.input)latest.current.onChange(repair.input,false);
  }});controller.current=current;
  return()=>{cancelReload();initialReload.current=false;controller.current=null;current.dispose();};
 },[org]);
 useLayoutEffect(()=>{
  cancelReload();initialReload.current=!!controller.current?.invalidate()||initialReload.current;
  if(initialReload.current)reloadTimer.current=setTimeout(()=>{reloadTimer.current=null;initialReload.current=false;const value=latest.current;void controller.current?.load(org,value.input.leave_type_id,value.inputGeneration);},250);
  return cancelReload;
 },[inputGeneration]);
 useEffect(()=>{cancelReload();initialReload.current=false;
  const seed=initialSeed.current;initialSeed.current=undefined;
  if(seed){const value=latest.current;const repair=repairChoices(value.input,seed,value.editable);setNotice(previous=>selectionNotice(previous,repair.notice,repair.input));if(!value.preserveStoredChoices&&repair.input!==value.input){const current=controller.current;queueMicrotask(()=>{if(controller.current===current&&!latest.current.preserveStoredChoices&&latest.current.inputGeneration===value.inputGeneration){repairedSelection.current={value:repair.input.leave_type_id};latest.current.onChange(repair.input,false);}});}return;}
  if(repairedSelection.current?.value===latest.current.input.leave_type_id){repairedSelection.current=null;return;}repairedSelection.current=null;
  void controller.current?.load(org,latest.current.input.leave_type_id,latest.current.inputGeneration);
 },[org,input.leave_type_id]);
 const available:DraftChoice[]=[...(catalogue?.choices??[])];
 const selected=catalogue?.selected.status==='available'&&catalogue.selected.choice.type_id===input.leave_type_id?catalogue.selected.choice:available.find(c=>c.type_id===input.leave_type_id);
 if(selected&&!available.some(c=>c.type_id===selected.type_id))available.push(selected);
 const refresh=()=>{cancelReload();initialReload.current=false;void controller.current?.load(org,input.leave_type_id,inputGeneration);};
 const changeType=(value:string)=>{const next=chooseType(input,available.find(c=>c.type_id===value)??null,firstChoiceEligible);controller.current?.invalidate();setNotice(previous=>selectionNotice(previous,next.notice,next.input));onChange(next.input,next.firstChoiceEligible);};
 return <section aria-labelledby="choices-heading"><h4 id="choices-heading">Leave options</h4>
 {state.kind==='loading'&&<p role="status">Loading leave options…</p>}
 {state.kind==='unavailable'&&<p role="alert">Leave options could not be checked. Your input is unchanged.</p>}
 {state.kind==='denied'&&<p role="alert">You do not currently have access to leave options.</p>}
 {(state.kind==='unavailable'||state.kind==='denied')&&<button type="button" onClick={refresh}>Retry leave options</button>}
 <label htmlFor="leave-type">Leave type</label><select id="leave-type" value={input.leave_type_id??''} disabled={!editable||!catalogue||state.kind==='denied'} onChange={event=>changeType(event.target.value)} aria-describedby={notice?'choice-notice':undefined}>
 <option value="">Choose a leave type</option>{input.leave_type_id&&!selected&&<option value={input.leave_type_id}>Selected leave type</option>}{available.map(choice=><option key={choice.type_id} value={choice.type_id}>{choice.name}</option>)}
 </select>
 <label htmlFor="duration-mode">Duration</label><select id="duration-mode" value={input.duration_mode??''} disabled={!editable||!selected||state.kind==='denied'} onChange={event=>{controller.current?.invalidate();const next={...input,duration_mode:(event.target.value||null) as DurationMode|null};setNotice(previous=>selectionNotice(previous,null,next));onChange(next,false);}} aria-describedby={notice?'choice-notice':undefined}>
 <option value="">Choose a duration</option>{input.duration_mode&&!selected?.permitted_modes.includes(input.duration_mode)&&<option value={input.duration_mode}>{labels[input.duration_mode]}</option>}{selected?.permitted_modes.map(mode=><option key={mode} value={mode}>{labels[mode]}</option>)}
 </select>
 {notice&&<p id="choice-notice" role="status">{notice}</p>}
 {catalogue?.choices.length===0&&catalogue.next_cursor===null&&<p>No leave types are currently offered.</p>}
 {catalogue?.next_cursor&&<button type="button" onClick={()=>void controller.current?.load(org,input.leave_type_id,inputGeneration,catalogue.next_cursor)}>More leave types</button>}
 <button type="button" onClick={refresh}>Refresh leave options</button>
 </section>;
}
/** Replaceable E1-CHOICES host. D1/D2 own starting, persistence and saved feedback. */
export function DraftInputHost({org,editable}:{org:string;editable:boolean}){
 const [state,setState]=useState(()=>({input:emptyInput(),generation:0,firstChoiceEligible:true}));
 return <DraftChoices org={org} input={state.input} inputGeneration={state.generation} editable={editable} firstChoiceEligible={state.firstChoiceEligible} onChange={(input,firstChoiceEligible)=>setState(previous=>({input,generation:previous.generation+1,firstChoiceEligible}))}/>;
}
