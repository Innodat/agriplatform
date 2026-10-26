import {readCapture,type PendingRead,type ReadResult} from '../src/read';
const pending:PendingRead={account_id:'a',org_id:'o',capture_id:'c'};
// @ts-expect-error read selectors cannot carry write commands
const bad:PendingRead={...pending,command_type:'capture.create'};
// @ts-expect-error explicit lease required
readCapture({account_id:'a',access_token:'t'},pending,{});
function snapshot(result:ReadResult){if(result.kind==='loaded'){
 // @ts-expect-error immutable observation
 result.snapshot.revision='2';
 // @ts-expect-error deeply immutable definition
 result.snapshot.definition.questions.push({});
}}
void bad;void snapshot;
