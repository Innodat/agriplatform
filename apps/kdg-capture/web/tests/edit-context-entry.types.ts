import {createEditContextEntry} from '../src/edit-context-entry';
import type {AuthEntryOptions} from '../src/auth-entry';
function verify(options:AuthEntryOptions){
 const entry=createEditContextEntry(options);
 // @ts-expect-error private lease must remain hidden
 entry.acquireExecution();
 // @ts-expect-error read requires pinned capture
 entry.load({account_id:'a',org_id:'o'});
 void entry.load({account_id:'a',org_id:'o',capture_id:'c'});
}
void verify;
