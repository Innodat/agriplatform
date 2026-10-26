import {createHistoryEntry} from '../src/history-entry';
import type {AuthEntryOptions} from '../src/auth-entry';
function verify(options:AuthEntryOptions){
 const entry=createHistoryEntry(options);
 // @ts-expect-error private lease must remain hidden
 entry.acquireExecution();
 // @ts-expect-error history requires pinned dates
 entry.history({account_id:'a',org_id:'o'});
 void entry.history({account_id:'a',org_id:'o',from_date:'2026-10-01',to_date:'2026-10-26'});
}
void verify;
