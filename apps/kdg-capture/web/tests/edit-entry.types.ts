import {createEditEntry} from '../src/edit-entry';
import type {EditCommand} from '../../contracts/edit-generated/types.gen';
declare const entry:ReturnType<typeof createEditEntry>;
declare const command:EditCommand;
// @ts-expect-error owner leases are hidden
entry.acquireExecution();
// @ts-expect-error original capture is required
entry.edit({account_id:'a',org_id:'o',command});
// @ts-expect-error exact revision cannot be a number
entry.edit({account_id:'a',org_id:'o',capture_id:'c',command:{...command,expected_revision:1}});
async function consume(){
 const result=await entry.edit({account_id:'a',org_id:'o',capture_id:'c',command});
 if(result.kind==='error'){
  if(result.error_id==='kdg_capture.capture_revision_conflict'){
   const status:409=result.status;const revision:string=result.current_revision;void [status,revision];
  }else{
   // @ts-expect-error only conflict carries current revision
   result.current_revision;
  }
 }
 if(result.kind==='committed'){
  // @ts-expect-error matching receipt remains immutable
  result.receipt.result.revision='2';
 }
}
void consume;
