import {createReadEntry} from '../src/read-entry';
import type {AuthEntryOptions} from '../src/auth-entry';
function verify(options:AuthEntryOptions){
 const entry=createReadEntry(options);
 // @ts-expect-error private lease must remain hidden
 entry.acquireExecution();
 // @ts-expect-error read requires pinned capture
 entry.read({account_id:'a',org_id:'o'});
 void entry.read({account_id:'a',org_id:'o',capture_id:'c'});
}
void verify;
