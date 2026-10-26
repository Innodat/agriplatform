import {openHistoryStore} from '../src/history-store';
declare const store:Awaited<ReturnType<typeof openHistoryStore>>;
async function check(){
 const begun=await store.beginSetupRefresh();
 if(begun.kind==='started')await store.importProvision({},begun.ticket,{restoreDenied:true});
 const opened=await store.openCreate('id');
 if(opened.kind==='opened'){
  // @ts-expect-error original evidence remains immutable
  opened.reviewed.child.child_id='other';
  await store.saveCreate(opened.reviewed,{capture_id:'id',operation_id:'op'},{});
 }
 const actions=await store.readCreateActions({limit:30});
 if(actions.kind==='available'){
  // @ts-expect-error command bytes remain immutable
  actions.actions[0].pending.command.child_id='other';
 }
 // @ts-expect-error refresh tickets required
 store.importProvision({});
 // @ts-expect-error stable identities required
 store.saveCreate({},{});
}
void check;
