import {loadEditContext,type PendingEditContext,type EditContextResult} from '../src/edit-context';
const pending:PendingEditContext={account_id:'a',org_id:'o',capture_id:'c'};
// @ts-expect-error read selectors cannot carry write commands
const bad:PendingEditContext={...pending,command_type:'capture.create'};
// @ts-expect-error explicit lease required
loadEditContext({account_id:'a',access_token:'t'},pending,{});
function snapshot(result:EditContextResult){if(result.kind==='loaded'){
 // @ts-expect-error immutable observation
 result.context.capture.revision='2';
 // @ts-expect-error deeply immutable definition
 result.context.capture.definition.questions.push({});
}}
void bad;void snapshot;
