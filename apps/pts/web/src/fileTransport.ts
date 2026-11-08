/** The proven shared transport leaves Supabase in auth.ts as the only auth owner. */
import {createNativeFileClient} from '@platform/ui-business';
import {filePreparationIsCurrent,type Identity} from './auth';
const client=createNativeFileClient({fileOrigin:import.meta.env.VITE_PTS_FILE_ORIGIN||'',frontendOrigin:location.origin});
const cleanupKey='pts-file-cleanup-v1';
type CleanupRecord=Identity&{sessionId:string;pending?:boolean;replacement?:Identity};
let cleanupGeneration=0;
// Failed persistence cannot become file authority. Keep only this loaded tab's
// cleanup recovery, tied to the exact shared observation it failed to replace.
// Another tab's mutation/clear supersedes it even before a storage event arrives.
let unpersisted:{raw:string|null;record:CleanupRecord}|null=null;
let lastObserved:CleanupRecord|null=null;
function retained(raw=localStorage.getItem(cleanupKey)):CleanupRecord|null{
 if(!raw)return null;
 const value=JSON.parse(raw);
 // Completed cleanup retains only a secret-free freshness marker. Removing the
 // key would make no-record -> prepare -> clear indistinguishable from no change.
 if(value?.version===1&&value.cleared===true&&typeof value.revision==='string'&&Object.keys(value).every(key=>['version','cleared','revision'].includes(key)))return null;
 if(value?.version!==1||typeof value.id!=='string'||typeof value.sessionId!=='string'||typeof value.token!=='string'||(value.refreshToken!==undefined&&typeof value.refreshToken!=='string')||(value.revocationToken!==undefined&&typeof value.revocationToken!=='string'))throw new Error('file_cleanup_recovery_unavailable');
 if(value.replacement&&(typeof value.replacement.id!=='string'||typeof value.replacement.sessionId!=='string'||typeof value.replacement.token!=='string'||typeof value.replacement.refreshToken!=='string'))throw new Error('file_cleanup_recovery_unavailable');
 return value;
}
export function pendingFileIdentity():CleanupRecord|null{
 const raw=localStorage.getItem(cleanupKey);
 if(unpersisted&&unpersisted.raw!==raw)unpersisted=null;
 return lastObserved=unpersisted?.record||retained(raw);
}
/** Revocation attempt only, when storage cannot be read; never read/setup authority. */
export function lastFileCleanupIdentity():Identity|null{return lastObserved;}
/** Private mutation observation only; never authentication or file authority. */
export type FileCleanupObservation={raw:string|null;current?:()=>boolean};
export function observeFileCleanup():FileCleanupObservation{return {raw:localStorage.getItem(cleanupKey)};}
export function fileCleanupIsCurrent(observation:FileCleanupObservation):boolean{
 try{return localStorage.getItem(cleanupKey)===observation.raw;}catch{return false;}
}
function requireObservation(observation?:FileCleanupObservation){if(observation&&(!fileCleanupIsCurrent(observation)||(observation.current&&!observation.current())))throw Object.assign(new Error('file_cleanup_superseded'),{code:'file_cleanup_superseded'});}
function failedMutation(record:CleanupRecord|null,raw:string|null,generation:number){
 if(record&&generation===cleanupGeneration&&localStorage.getItem(cleanupKey)===raw){
  unpersisted={raw,record:{...record,pending:true}};lastObserved=unpersisted.record;
 }
}
function write(record:CleanupRecord|null){
 const revision=crypto.randomUUID();
 const raw=JSON.stringify(record?{version:1,...record,revision}:{version:1,cleared:true,revision});
 localStorage.setItem(cleanupKey,raw);unpersisted=null;lastObserved=record;return raw;
}
function mutate<T>(operation:()=>T):Promise<T>{
 // localStorage has no compare-and-set. Keep each actual read/compare/write in
 // one brief cross-tab lock, with neither owner HTTP nor auth work inside it.
 if(!navigator.locks)return Promise.reject(new Error('file_cleanup_recovery_unavailable'));
 return navigator.locks.request(cleanupKey,{signal:AbortSignal.timeout(2000)},operation);
}
export function forgetFileCleanup(onlyEmpty=false,observation?:FileCleanupObservation){cleanupGeneration++;return mutate(()=>{
 requireObservation(observation);
 // Ordinary auth cannot erase native work another tab prepared while provider
 // logout was in flight. Keep that exact cleanup recoverable after the attempt.
 const record=onlyEmpty?pendingFileIdentity():null;
 if(record){write({...record,pending:true});throw Object.assign(new Error('file_cleanup_required'),{code:'file_cleanup_required'});}
 return {raw:write(null)};
});}
export async function beginFileCleanup(replacement?:Identity,observation?:FileCleanupObservation){
 requireObservation(observation);
 const generation=++cleanupGeneration,raw=localStorage.getItem(cleanupKey),previous=pendingFileIdentity();
 if(previous&&replacement&&(!replacement.sessionId||!replacement.refreshToken))throw new Error('file_cleanup_session_mismatch');
 const candidate=previous?{...previous,pending:true,replacement:replacement||previous.replacement}:null;
 try{return await mutate(()=>{
  // A newer tab's write wins; never reconstruct a stale original/replacement.
  if(generation!==cleanupGeneration||localStorage.getItem(cleanupKey)!==raw)throw new Error('file_cleanup_superseded');
  requireObservation(observation);return {raw:write(candidate)};
 });}catch(error){if(!observation?.current||observation.current())failedMutation(candidate,raw,generation);throw error;}
}
export async function retainFileCleanupRefresh(original:Identity,refreshed:{id:string;token:string;refreshToken:string},observation?:FileCleanupObservation){
 requireObservation(observation);
 const generation=++cleanupGeneration,raw=localStorage.getItem(cleanupKey),record=pendingFileIdentity();
 if(!record||record.id!==original.id||record.sessionId!==original.sessionId||refreshed.id!==record.id)throw new Error('file_cleanup_session_mismatch');
 const candidate={...record,revocationToken:refreshed.token,refreshToken:refreshed.refreshToken};
 try{return await mutate(()=>{
  if(generation!==cleanupGeneration||localStorage.getItem(cleanupKey)!==raw)throw new Error('file_cleanup_superseded');
  requireObservation(observation);return {raw:write(candidate)};
 });}catch(error){if(!observation?.current||observation.current())failedMutation(candidate,raw,generation);throw error;}
}
export async function prepareFileCleanup(identity:Identity,recovery=false,owner?:FileCleanupObservation){
 // Observe auth before the owner wait: an older response cannot downgrade a
 // newer credential/rotation or any other tab's completed cleanup. Persist the
 // observation even without custody so its absence cannot produce an ABA race.
 const generation=++cleanupGeneration;
 const observation=await mutate(()=>{
  requireObservation(owner);
  if(generation!==cleanupGeneration)throw new Error('file_cleanup_superseded');
  const previous=pendingFileIdentity();
  if(previous?.pending&&!recovery)throw new Error('file_cleanup_required');
  const raw=write(previous);if(owner)owner.raw=raw;return raw;
 });
 const pair=await client.prepare(identity);
 requireObservation(owner);
 // A failed ordinary-tab mutation may leave the shared marker unchanged. The
 // existing auth owner reads physical SDK storage before any late credential
 // write; delivered events alone cannot establish that freshness. Cleanup-only
 // original recovery remains valid even with a different current SDK session.
 if(!recovery&&!filePreparationIsCurrent(identity))throw new Error('file_cleanup_superseded');
 if(generation!==cleanupGeneration||localStorage.getItem(cleanupKey)!==observation)throw new Error('file_cleanup_superseded');
 if(pair.account_id!==identity.id)throw new Error('file_cleanup_session_mismatch');
 const previous=pendingFileIdentity();
 if(previous&&(previous.id!==pair.account_id||previous.sessionId!==pair.session_id))throw new Error('file_cleanup_required');
 // The exact successful owner receipt is cleanup evidence even if its final
 // local write fails. Native establishment still requires that write to succeed.
 const candidate={...previous,id:identity.id,sessionId:pair.session_id,token:previous?.token||identity.token,refreshToken:identity.refreshToken||previous?.refreshToken,revocationToken:previous?.revocationToken,pending:previous?.pending||false};
 try{await mutate(()=>{
  requireObservation(owner);
  if(generation!==cleanupGeneration||localStorage.getItem(cleanupKey)!==observation||(!recovery&&!filePreparationIsCurrent(identity)))throw new Error('file_cleanup_superseded');
  const raw=write(candidate);if(owner)owner.raw=raw;
 });}catch(error){
  // A revoked/replaced SDK observation cannot recreate even volatile custody.
  // Preserve only a still-current successful receipt after persistence failure.
  if((!owner?.current||owner.current())&&(recovery||filePreparationIsCurrent(identity)))failedMutation(candidate,observation,generation);
  throw error;
 }

 return pair;
}
async function present<T>(operation:()=>Promise<T>):Promise<T>{
 try{return await operation();}
 catch(error){
  const status=(error as {status?:number})?.status;
  throw Object.assign(new Error(status===401?'Please sign in again to reopen this document.':status===403?'You do not currently have access to this document.':'We could not open the document. Please retry.'),{status});
 }
}
export function establishFiles(identity:Identity){return present(async()=>{await prepareFileCleanup(identity);await client.establish(identity);});}
export function clearFiles(identity:Identity,owner?:FileCleanupObservation){return present(async()=>{
 try{return await client.clear(identity);}
 catch(error){
  if((error as {status?:number}).status!==401)throw error;
  // An unreceipted, still-live login can prepare cleanup without document grants.
  // Preparation failure is visible;401 is never interpreted as completed cleanup.
  requireObservation(owner);
  await prepareFileCleanup(identity,true,owner);requireObservation(owner);return await client.clear(identity);
 }
});}
export function fileContext(id:string,presentation:'open'|'download',identity:Identity){return present(()=>client.context(id,presentation,identity));}
