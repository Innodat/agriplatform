import type {DraftInput} from './draft-input.ts';
import type {DraftChoice,DraftChoicesResponse} from './api/leave.ts';
export type ChoiceChange={input:DraftInput;notice:string|null;firstChoiceEligible:boolean};
export function chooseType(input:DraftInput,choice:DraftChoice|null,firstChoiceEligible:boolean):ChoiceChange{
 let mode=input.duration_mode,notice:string|null=null;
 if(choice===null)mode=null;
 else if(firstChoiceEligible&&mode===null&&choice.permitted_modes.includes('full_days'))mode='full_days';
 else if(mode!==null&&!choice.permitted_modes.includes(mode)){mode=null;notice='Please choose a duration again.';}
 return {input:{...input,leave_type_id:choice?.type_id??null,duration_mode:mode},notice,firstChoiceEligible:choice===null?firstChoiceEligible:false};
}
export function repairChoices(input:DraftInput,response:DraftChoicesResponse,editable:boolean):{input:DraftInput;notice:string|null}{
 const selected=response.selected;
 if(selected.status==='obsolete')return{input:editable?{...input,leave_type_id:null,duration_mode:null}:input,notice:editable?'Please choose a leave type again.':'Your selected leave type is no longer available.'};
 if(selected.status==='available'&&input.duration_mode!==null&&!selected.choice.permitted_modes.includes(input.duration_mode))return{input:editable?{...input,duration_mode:null}:input,notice:editable?'Please choose a duration again.':'Your selected duration is no longer available.'};
 return{input,notice:null};
}
