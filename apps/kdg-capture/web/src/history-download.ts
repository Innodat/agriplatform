/** Explicit candidate download; never activated by browser startup. */
import {historyCaptures,type PendingHistory,type HistoryOptions} from './history.js';
import type {Session} from './entry';
import type {openHistoryStore} from './history-store';
export async function downloadOwnHistory(store:Awaited<ReturnType<typeof openHistoryStore>>,session:Session,pending:PendingHistory,options:HistoryOptions & {restoreDenied?:boolean}) {
 const fresh=()=>{try{return !options.signal.aborted&&options.isCurrent()===true;}catch{return false;}};
 const pinned=Object.freeze({...pending});let cursor=pinned.cursor;
 do {
  const query={...pinned,...(cursor?{cursor}:{})};
  const response=await historyCaptures(session,query,options);
  if(!fresh())return Object.freeze({kind:'superseded'});
  if(response.kind!=='loaded'){
   if(response.kind==='error'&&response.error_id==='access_denied'){
    const locked=await store.deny(pinned,{signal:options.signal,isCurrent:options.isCurrent});
    if(locked.kind!=='locked')return Object.freeze({kind:'unavailable'});
   }
   return fresh()?response:Object.freeze({kind:'superseded'});
  }
  const imported=await store.importPage(response.page,query,{signal:options.signal,isCurrent:options.isCurrent,restoreDenied:options.restoreDenied});
  if(!fresh())return Object.freeze({kind:'superseded'});
  if(imported.kind!=='committed')return imported;
  cursor=response.page.next_cursor??undefined;
 }while(cursor);
 return Object.freeze({kind:fresh()?'complete':'superseded'});
}
