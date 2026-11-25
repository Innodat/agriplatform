import type {DraftContextV1} from './api/leave';
export function MyLeave({context,apply,open}:{context:DraftContextV1;apply:()=>void;open:(draft:string)=>void}){
 if(context.status==='setup_required')return <p role="status">{context.reason==='employment_missing'?'Employment setup is needed before you can apply for leave.':context.reason==='identity_person_link_required'?'Your account needs a verified person link.':'Your account attribution setup is incomplete.'}</p>;
 const reason=context.editability.status==='read_only'?context.editability.reason:null;
 return <><h3 tabIndex={-1} data-task-return>My Leave</h3>{reason&&<p role="status">{reason==='permission_missing'?'Your current permission allows reading only.':reason==='employment_ended'?'Your employment has ended. Your saved draft is read only.':'Employment periods need to be set up before you can apply for leave.'}</p>}
 {context.editability.status==='editable'&&<button onClick={apply}>Apply for leave</button>}
 {context.active_draft&&<p>You have an unfinished application. <button onClick={()=>open(context.active_draft!.draft_id)}>Open application</button></p>}
 {context.setup_notices.map(n=><p key={n.code}>{n.code==='work_timezone_missing'?'Your work timezone is not set up.':'Your work timezone setup is invalid.'} This does not prevent preserving leave input.</p>)}</>;
}
