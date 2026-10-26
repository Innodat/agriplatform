import type {AdminEditContext, AdminEditContextData, AdminEditContextResponse, AdminEditContextError} from '../../contracts/admin-edit-context-generated';
import type {CaptureDetail} from '../../contracts/read-generated';
type Equal<A,B>=(<T>()=>T extends A?1:2) extends (<T>()=>T extends B?1:2)?true:false;
type Assert<T extends true>=T;
type ExactContext=Assert<Equal<keyof AdminEditContext,'capture'|'editable_fields'>>;
type ExactCapture=Assert<Equal<AdminEditContext['capture'],CaptureDetail>>;
type ExactEditable=Assert<Equal<AdminEditContext['editable_fields'],['observation_date','answers']>>;
declare const result:AdminEditContextResponse;
const capture:CaptureDetail=result.capture;
const context:AdminEditContext=result;
const input:AdminEditContextData={path:{capture_id:'c'},url:'/api/v1/admin/captures/{capture_id}/edit-context'};
// @ts-expect-error current read provides no offline observation
const observation=result.read_observation;
// @ts-expect-error current edit check grants no reusable authority
const edit=result.edit_observation;
// @ts-expect-error no expiry or offline lease
const expiry=result.expires_at;
// @ts-expect-error no command or receipt
const command=result.command_type;
// @ts-expect-error no outcome
const outcome=result.status;
// @ts-expect-error no actor label
const actor=result.capture.actor_name;
// @ts-expect-error only the exact original mutable fields
const editable:AdminEditContext['editable_fields']=['child_id','answers'];
// @ts-expect-error no query selectors
const query:AdminEditContextData={...input,query:{org_id:'o'}};
// @ts-expect-error no request body or write proposal
const body:AdminEditContextData={...input,body:{answers:{}}};
// @ts-expect-error original owner cannot be selected
const owner:AdminEditContextData={...input,path:{capture_id:'c',owner_account_id:'a'}};
declare const error:AdminEditContextError;
const safe:string=error.error_id;
void capture;void context;void observation;void edit;void expiry;void command;void outcome;void actor;void editable;void query;void body;void owner;void safe;
