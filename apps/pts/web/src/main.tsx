import React,{useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {AppLauncher,useCurrentApps} from '@platform/ui-business';
import {createJsonCache,withDeadline} from '@platform/browser-cache';
import {createAppDirectoryClient} from '@platform/app-directory-client';
import {auth,observeAuthChange,verifiedSessionIdentity,filePreparationIsCurrent,observeCleanupAuth,authCleanupIsCurrent,currentCleanupSession,clearPasswordFlow,passwordFlowFor,consumePasswordReturn,revokeLocalSession,retainCurrentCleanup,finishOriginalAuthLogout,restoreCleanupSession,type AuthCleanupObservation,type Identity,type PasswordFlow} from './auth';
import {establishFiles,clearFiles,fileContext,prepareFileCleanup,pendingFileIdentity,lastFileCleanupIdentity,forgetFileCleanup,beginFileCleanup,retainFileCleanupRefresh,observeFileCleanup,fileCleanupIsCurrent,type FileCleanupObservation} from './fileTransport';
import {completeFileLogout} from './fileLogout';
import type {AuthChangeEvent,Session} from '@supabase/supabase-js';
import {LoginForm} from './LoginForm';
import type {CollectionResponse,PoemResponse,DocumentResponse,Selection,SourcesResponse} from './contracts';
import {SourcesView,RecordFields} from './SourcesView';
import {UsagePanel,UsageBadge,TextBadge} from './UsagePanel';
import {Copy} from 'lucide-react';
import {CollectionStats,PoemLength} from './CollectionStats';
import './style.css';

type Filters={search:string;availability:string;source:string;genre:string;origin:string;dialect:string;status:string};
const defaults:Filters={search:'',availability:'research',source:'',genre:'',origin:'',dialect:'',status:''};
const base=import.meta.env.VITE_PTS_API_URL || 'http://localhost:8010';
const safeLink=(value:unknown)=>typeof value==='string'&&/^https?:\/\//.test(value)?value:undefined;
const directory=createAppDirectoryClient({baseUrl:import.meta.env.VITE_APP_DIRECTORY_URL||'http://localhost:8001'});
const initial=new URLSearchParams(location.search);
const initialFilters={...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>initial.has(k)).map(k=>[k,initial.get(k)!]))};
// This cache contains only selected corpus JSON. Files, exports and authority are excluded.
function corpusShape(value:unknown,path:string):boolean{
 const object=(v:any)=>Boolean(v&&typeof v==='object'&&!Array.isArray(v));
 const strings=(v:any,keys:string[])=>v==null||object(v)&&keys.every(k=>v[k]==null||typeof v[k]==='string');
 const rows=(r:any,keys:string[])=>object(r)&&keys.every(k=>Array.isArray(r[k])&&r[k].every((v:any)=>object(v)&&typeof v.id==='string'&&strings(v,['title','text','note','locator','copying_basis'])));
 const usage=(r:any)=>r.research_usage==null||object(r.research_usage)&&Object.values(r.research_usage).every((u:any)=>strings(u,['label','summary','status'])&&(u?.conditions==null||Array.isArray(u.conditions)&&u.conditions.every((c:unknown)=>typeof c==='string')));
 const poem=(p:any)=>object(p)&&typeof p.id==='string'&&typeof p.title==='string'&&(p.text==null||typeof p.text==='string')&&strings(p.creator,['name'])&&strings(p.geography,['origin_locality','dialect'])&&strings(p.classification,['formal_poetry_type','genre'])&&strings(p.quality,['notes','reviewer_note'])&&strings(p.source,['citation','locator']);
 const selection=(r:any)=>rows(r,['poems','witnesses','sources','rights','source_documents'])&&r.poems.every(poem)&&usage(r);
 const acquisition=(p:any)=>strings(p,['priority','reason','origin','access','next_step','rights_note','source_url','extent','assessed_on','assessment_by'])&&strings(p?.contact,['name','email','url','verified_on']);
 if(!object(value))return false;const row=value as Record<string,any>;
 if(path==='/api/sources')return rows(row,['sources','rights','source_documents'])&&usage(row)&&(row.acquisition==null||object(row.acquisition)&&Object.values(row.acquisition).every(acquisition))&&(row.acquisition_leads==null||rows(row,['acquisition_leads'])&&row.acquisition_leads.every(acquisition));
 if(path.startsWith('/api/poetry?'))return selection(row)&&typeof row.total==='number'&&object(row.filters)&&Object.values(row.filters).every(v=>Array.isArray(v)&&v.every(s=>typeof s==='string'));
 return Boolean(poem(row.poem)&&selection(row.evidence)&&typeof row.citation==='string');
}
function readerCache(account:string){let storage:Storage|undefined;try{storage=localStorage;}catch{/* Network-only memory cache. */}return createJsonCache({app:'pts',api:base,account,format:1,storage,validate:corpusShape});}
const unfinishedSignOut='We could not finish signing you out. Please retry Sign out.';
function App(){
 const [identity,setIdentity]=useState<Identity|null>(null),[authReady,setAuthReady]=useState(false);
 const [fileRecovery,setFileRecovery]=useState(()=>{try{return Boolean(pendingFileIdentity());}catch{return false;}});
 const [cleanupError,setCleanupError]=useState(()=>{try{return pendingFileIdentity()?.pending?unfinishedSignOut:'';}catch{return '';}});
 const [passwordFlow,setPasswordFlow]=useState<PasswordFlow|null>(null),[loginError,setLoginError]=useState('');
 const [view,setView]=useState(initial.get('view')==='sources'?'sources':'poems'),[sources,setSources]=useState<SourcesResponse|null>(null);
 const [applied,setApplied]=useState<Filters>(initialFilters),[draft,setDraft]=useState<Filters>(initialFilters);
 const [poemId,setPoemId]=useState(initial.get('poem')||''),[data,setData]=useState<CollectionResponse|null>(null),[single,setSingle]=useState<PoemResponse|null>(null);
 const [error,setError]=useState(''),[notice,setNotice]=useState(''),[loading,setLoading]=useState(false),[reload,setReload]=useState(0),[copyText,setCopyText]=useState(''),[documentUrl,setDocumentUrl]=useState('');
 const dialog=useRef<HTMLDialogElement>(null),copyDialog=useRef<HTMLDialogElement>(null),filterButton=useRef<HTMLButtonElement>(null);
 const pendingFilters=useRef<Filters|null>(null);
 const authorityEpoch=useRef(0);
 const corpusCache=useRef(readerCache(''));
 const readController=useRef<AbortController|null>(null),readBusy=useRef(false),lastRead=useRef(0),readSelection=useRef('');
 const signingOut=useRef(false);
 type CleanupOperation={observation?:FileCleanupObservation;auth:AuthCleanupObservation;original:Identity|null};
 const cleanupOperation=useRef<CleanupOperation|null>(null);
 // A failed private write must not discard the verified replacement still held
 // by the existing SDK. It remains blocked until original cleanup is complete.
 const replacementRecovery=useRef<Identity|null>(null);
 const acceptSession=useRef<((session:Session|null,event?:AuthChangeEvent)=>void)|null>(null);
 const generation=useRef(0),current=useRef<Identity|null>(null),lastUser=useRef(sessionStorage.getItem('pts-last-user'));
 function clear(invalidateCache=true,abortRead=true){authorityEpoch.current++;generation.current++;if(abortRead)readController.current?.abort();if(invalidateCache)corpusCache.current.clear();setData(null);setSingle(null);setSources(null);setCopyText('');setDocumentUrl('');copyDialog.current?.close();setNotice('');}
 function operationCurrent(operation:CleanupOperation){return cleanupOperation.current===operation&&authCleanupIsCurrent(operation.auth)&&(!operation.observation||fileCleanupIsCurrent(operation.observation));}
 function startOperation(original:Identity|null){let observation;try{observation=observeFileCleanup();}catch{/* Unknown custody stays incomplete on the native path. */}const operation={original,observation,auth:observeCleanupAuth()};cleanupOperation.current=operation;return operation;}
 function mutationObservation(operation:CleanupOperation){if(operation.observation)operation.observation.current=()=>cleanupOperation.current===operation&&authCleanupIsCurrent(operation.auth);return operation.observation;}
 function requireOperation(operation:CleanupOperation){if(!operationCurrent(operation))throw Object.assign(new Error('file_cleanup_superseded'),{code:'file_cleanup_superseded'});}
 async function beginOperation(operation:CleanupOperation,replacement?:Identity){requireOperation(operation);operation.observation=await beginFileCleanup(replacement,mutationObservation(operation));requireOperation(operation);}
 async function forgetOperation(operation:CleanupOperation,onlyEmpty=false){requireOperation(operation);operation.observation=await forgetFileCleanup(onlyEmpty,mutationObservation(operation));requireOperation(operation);}
 const revokeFileSession=(original:Identity,recover=true,operation?:CleanupOperation)=>revokeLocalSession(original,async(original,refreshed)=>{
   if(operation)requireOperation(operation);
   const observation=await retainFileCleanupRefresh(original,refreshed,operation?mutationObservation(operation):undefined);
   if(operation){operation.observation=observation;requireOperation(operation);}
 },recover,operation?()=>operationCurrent(operation):undefined,operation?.auth);
 async function cleanupOriginal(original:Identity,replacement:Identity|undefined,operation:CleanupOperation){
   let mutationError:unknown;
   try{await beginOperation(operation,replacement);}catch(error){mutationError=error;}
   const ownedRaw=!mutationError&&!replacement?operation.observation?.raw:null;
   // Private storage is not a prerequisite for an independent original-token
   // revocation attempt. Without persistence, do not load/refresh SDK custody.
   await completeFileLogout(original,{clear:identity=>clearFiles(identity,mutationObservation(operation)),revoke:identity=>revokeFileSession(identity,!mutationError,operation)});
   // The owner has just proved exact original absence. Another App may have
   // retained a verified rotation and removed that same revoked SDK session.
   // Only already-owned pending original recovery can converge; new native work,
   // foreign scope, replacement or unexplained fields remain superseded.
   if(ownedRaw&&original.sessionId&&!authCleanupIsCurrent(operation.auth)){
     const authSnapshot=observeCleanupAuth();
     if(authSnapshot.raw===null){
       const {data,error}=await currentCleanupSession();
       const observation=observeFileCleanup(),latest=pendingFileIdentity();
       const recoveryBase=(raw:string)=>{const {revision,refreshToken,revocationToken,...base}=JSON.parse(raw);return JSON.stringify(base);};
       if(!error&&!data.session&&cleanupOperation.current===operation&&authCleanupIsCurrent(authSnapshot)&&fileCleanupIsCurrent(observation)&&latest?.pending===true&&latest.id===original.id&&latest.sessionId===original.sessionId&&!latest.replacement&&observation.raw&&recoveryBase(ownedRaw)===recoveryBase(observation.raw)){
         operation.observation=observation;operation.auth.raw=null;
       }
     }
   }
   requireOperation(operation);
   if(mutationError)throw mutationError;
 }
 async function resumeSuperseded(operation:CleanupOperation){
   // Only the sole auth owner may identify the later session. Unreadable custody
   // or failed claims verification is an incomplete recovery, never absence.
   const {data,error}=await currentCleanupSession();if(error)throw error;
   const saved=pendingFileIdentity();
   if(data.session){
     const verified=await verifiedSessionIdentity(data.session,()=>cleanupOperation.current===operation);
     if(!filePreparationIsCurrent(verified))throw new Error('file_cleanup_superseded');
     if(operation.original?.sessionId&&operation.original.id===verified.id&&operation.original.sessionId===verified.sessionId){
       const observation=observeFileCleanup(),latest=pendingFileIdentity();
       if(latest?.id===verified.id&&latest.sessionId===verified.sessionId)await beginFileCleanup(undefined,{...observation,current:()=>filePreparationIsCurrent(verified)});
       throw new Error('file_cleanup_incomplete');
     }
   }else if(saved){
     // Ordinary SDK logout may finish after another tab prepared new native
     // custody for this same original. Retain it as pending under fresh negative
     // observations; a foreign later session/custody is never changed here.
     const authSnapshot=observeCleanupAuth(),observation=observeFileCleanup(),latest=pendingFileIdentity();
     if(authSnapshot.raw===null&&operation.original?.sessionId&&latest?.id===operation.original.id&&latest.sessionId===operation.original.sessionId){
       await beginFileCleanup(undefined,{...observation,current:()=>cleanupOperation.current===operation&&authCleanupIsCurrent(authSnapshot)});
     }
     throw new Error('file_cleanup_incomplete');
   }
   if(cleanupOperation.current!==operation)return;
   cleanupOperation.current=null;replacementRecovery.current=null;current.current=null;
   setCleanupError('');setFileRecovery(false);setLoginError('');setAuthReady(true);
   acceptSession.current?.(data.session);
 }
 useEffect(()=>{
   let active=true,initialized=false,revision=0,switching=false;
   let replacementObservation=0,lastRetainedReplacementObservation=0;
   let pending:{session:Session|null;event?:AuthChangeEvent}|null=null;
   function invalidateChangedAccount(session:Session|null){
     if(session&&current.current&&session.user.id!==current.current.id){clear();setIdentity(null);setPasswordFlow(null);setError('');setAuthReady(false);}
   }
   function accept(session:Session|null,event?:AuthChangeEvent){
     const observation=++revision;
     invalidateChangedAccount(session);
     if(signingOut.current)return;
     let retained:ReturnType<typeof pendingFileIdentity>=null;try{retained=pendingFileIdentity();}catch{/* File custody failure cannot gate ordinary account reads. */}
     const next=session?{id:session.user.id,token:session.access_token,refreshToken:session.refresh_token}:null;
     // New credentials for the same account can identify a different provider
     // session. Ask the existing auth owner before deciding refresh vs replacement.
     if(session&&retained&&session.access_token!==retained.token&&session.access_token!==retained.revocationToken){
       void verifiedSessionIdentity(session,()=>active&&!signingOut.current&&observation===revision).then(verified=>apply(session,event,verified,retained)).catch(()=>{
         if(active&&observation===revision&&!signingOut.current){clear();setIdentity(null);setCleanupError('We could not verify your session. Please retry Sign out.');setAuthReady(true);setFileRecovery(true);}
       });
     }else apply(session,event,next&&retained?{...next,sessionId:retained.sessionId}:next,retained);
   }
   function apply(session:Session|null,event:AuthChangeEvent|undefined,next:Identity|null,retained:ReturnType<typeof pendingFileIdentity>){
     if(!active||signingOut.current)return;
     // Capture recovery/password return state before original-session cleanup;
     // provider refresh or replacement restoration must not consume that callback.
     const flow=passwordFlowFor(session,event);
     if(switching){
       if(next&&retained&&next.sessionId&&next.sessionId!==retained.sessionId){pending={session,event};const operation=cleanupOperation.current;if(operation&&operationCurrent(operation))void beginOperation(operation,next).catch(()=>setCleanupError(unfinishedSignOut));}
       return;
     }
     setFileRecovery(Boolean(retained));
     const previous=retained||current.current;
     const replacement=previous&&next&&(previous.id!==next.id||Boolean(retained&&next.sessionId!==retained.sessionId));
     if(replacement){
       current.current=previous;
       if(retained?.pending&&retained.replacement){
         // The sole auth owner can rotate the replacement while original cleanup
         // is pending. Persist that verified observation without changing either
         // session's authority or discarding the visible transition failure.
         void beginFileCleanup(next!).catch(()=>setCleanupError(unfinishedSignOut));setIdentity(null);setAuthReady(true);setCleanupError(message=>message||unfinishedSignOut);return;
       }
       switching=true;pending={session,event};clear();setIdentity(null);setAuthReady(false);
       const operation=startOperation(previous);
       void (async()=>{
         try{
           replacementRecovery.current=next;
           const original=pendingFileIdentity();
           if(original)await cleanupOriginal(original,next!,operation);
           else await revokeFileSession(previous!,true,operation);
           requireOperation(operation);
           // An explicit original refresh can temporarily replace SDK storage.
           // Restore the separately retained replacement only after exact absence.
           const saved=pendingFileIdentity()?.replacement||replacementRecovery.current;
           const replacement=saved?{access_token:saved.token,refresh_token:saved.refreshToken!}:pending?.session;
           if(replacement){const restored=await restoreCleanupSession({id:next!.id,token:replacement.access_token,refreshToken:replacement.refresh_token},()=>operationCurrent(operation),operation.auth);requireOperation(operation);if(restored.error||!restored.data.session)throw restored.error||new Error('replacement_session_unavailable');pending={session:restored.data.session,event:pending?.event};}
           await forgetOperation(operation);replacementRecovery.current=null;setCleanupError('');
           if(!active)return;
           current.current=null;switching=false;const latest=pending;pending=null;
           if(latest)accept(latest.session,latest.event);
         }catch(error){
           if(!operationCurrent(operation)){
             // Another tab owns the later session/custody. Observe its existing
             // SDK state; never restore this operation's saved replacement.
             switching=false;pending=null;replacementRecovery.current=null;
             if(active)try{await resumeSuperseded(operation);}catch{clear();setIdentity(null);setAuthReady(true);setFileRecovery(true);setCleanupError(unfinishedSignOut);}
             return;
           }
           // Keep the verified replacement durable across both partial orders,
           // explicit original refresh, reload and repeated cleanup attempts.
           let saved;try{saved=pendingFileIdentity()?.replacement;}catch{/* Unknown recovery remains visible; never infer absence. */}
           // A failed observation can leave a newer replacement pair in SDK
           // storage. Preserve it for owner verification on reload/retry rather
           // than overwriting it with the older durable pair that just failed.
           if(saved&&(error as {code?:string})?.code!=='file_cleanup_replacement_unavailable')try{await restoreCleanupSession(saved,()=>operationCurrent(operation),operation.auth);}catch{/* Durable recovery remains visible. */}
           if(!active)return;
           switching=false;pending=null;current.current=previous;setIdentity(null);setAuthReady(true);setFileRecovery(true);
           setCleanupError('We could not finish switching accounts. Please retry Sign out.');
         }
       })();
       return;
     }
     if(current.current?.id!==next?.id||flow){clear(Boolean(current.current)||!next||Boolean(flow)||Boolean(next&&lastUser.current&&lastUser.current!==next.id));if(next)corpusCache.current=readerCache(next.id);setError('');}
     if(next&&lastUser.current&&lastUser.current!==next.id){history.replaceState(null,'',location.pathname);setApplied(defaults);setDraft(defaults);setPoemId('');setView('poems');setNotice('Account changed. Open the collection again.');}
     if(next&&flow==='recovery'){
       const restored=consumePasswordReturn(next.id);
       if(restored){setApplied({...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>restored.has(k)).map(k=>[k,restored.get(k)!]))});setDraft(defaults);setPoemId(restored.get('poem')||'');setView(restored.get('view')==='sources'?'sources':'poems');history.replaceState(null,'',location.pathname+'?'+restored);}
     }
     if(next){lastUser.current=next.id;sessionStorage.setItem('pts-last-user',next.id);}
     current.current=next;setIdentity(next);setPasswordFlow(flow);setLoginError('');setAuthReady(true);
     // Ordinary corpus reads do not wait on the cleanup-only write. Every file
     // action repeats preparation and requires durable browser recovery custody.
     if(next&&retained?.pending)void retainCurrentCleanup(next,retained,async(original,refreshed)=>{await retainFileCleanupRefresh(original,refreshed);},()=>active&&!signingOut.current&&!switching&&current.current===next).catch(()=>{});
     else if(next)void prepareFileCleanup(next).catch(()=>{});
   }
   acceptSession.current=accept;
   const {data}=auth.onAuthStateChange((event,session)=>{
     observeAuthChange(event);
     if(!active||!initialized||event==='INITIAL_SESSION')return;
     invalidateChangedAccount(session);
     let retained:ReturnType<typeof pendingFileIdentity>;try{retained=pendingFileIdentity();}catch{accept(session,event);return;}
     if(session&&retained?.pending&&retained.replacement&&(signingOut.current||switching)){
       // The sole SDK owner can rotate the replacement while loading storage for
       // original-session cleanup. Its existing notification awaits this explicit
       // token check and durable write before SDK storage can become the original.
       // Original-session notifications never supersede a matching replacement.
       revision++;const observation=++replacementObservation;
       return verifiedSessionIdentity(session,()=>active).then(async verified=>{
         const latest=pendingFileIdentity();
         if(!latest?.pending||latest.id!==retained.id||latest.sessionId!==retained.sessionId||observation<lastRetainedReplacementObservation)return;
         const originalMatch=latest.id===verified.id&&latest.sessionId===verified.sessionId;
         const replacementMatch=latest.replacement?.id===verified.id&&latest.replacement.sessionId===verified.sessionId;
         if((!originalMatch&&!replacementMatch)||!filePreparationIsCurrent(verified))return;
         const operation=cleanupOperation.current;
         if(operation){
           if(operation.observation&&!fileCleanupIsCurrent(operation.observation))throw new Error('file_cleanup_superseded');
           // Adopt only the current exact original or captured replacement's
           // owner-verified rotation. Independent provider sessions supersede it.
           operation.auth.raw=observeCleanupAuth().raw;
           requireOperation(operation);
           if(originalMatch){const next=await retainFileCleanupRefresh(latest,{id:verified.id,token:verified.token,refreshToken:verified.refreshToken!},mutationObservation(operation));operation.observation=next;requireOperation(operation);}
           else await beginOperation(operation,verified);
         }else if(replacementMatch)await beginFileCleanup(verified);
         lastRetainedReplacementObservation=observation;
       }).catch(()=>{throw Object.assign(new Error('file_cleanup_replacement_unavailable'),{code:'file_cleanup_replacement_unavailable'});});
     }
     accept(session,event);
   });
   void (async()=>{
     const result=await auth.initialize();
     if(!active)return;
     initialized=true;
     if(result.error){clearPasswordFlow();history.replaceState(null,'',location.pathname+location.search);setLoginError('This sign-in link is invalid or has expired. Request a new reset link or sign in with your password.');setAuthReady(true);return;}
     const atStart=revision;
     const {data,error}=await auth.getSession();
     if(active&&revision===atStart){if(error){setLoginError('We could not restore your session. Please sign in again.');setAuthReady(true);}else accept(data.session);}
   })().catch(()=>{if(active){setLoginError('We could not restore your session. Please sign in again.');setAuthReady(true);}});
   return ()=>{active=false;acceptSession.current=null;data.subscription.unsubscribe();};
 },[]);
 function passwordSaved(){clearPasswordFlow();setPasswordFlow(null);setNotice('Password saved.');setReload(v=>v+1);}
 async function signOut(){
   if(signingOut.current)return;
   signingOut.current=true;clear();
   let initializedOperation:CleanupOperation|undefined;
   let nativeCleanup=false,unknownCustody=false;
   try{
     const operation=startOperation(current.current);
     initializedOperation=operation;
     let previous;
     try{previous=pendingFileIdentity();}
     catch(error){
       unknownCustody=true;
       const original=lastFileCleanupIdentity()||current.current;
       if(original)try{await revokeFileSession(original,false);}catch{/* Incomplete remains visible. */}
       throw error;
     }
     operation.original=previous||current.current;nativeCleanup=Boolean(previous);
     if(previous){
       await cleanupOriginal(previous,previous.replacement||replacementRecovery.current||undefined,operation);
       requireOperation(operation);
       const replacement=pendingFileIdentity()?.replacement||replacementRecovery.current;
       if(replacement){
         const restored=await restoreCleanupSession(replacement,()=>operationCurrent(operation),operation.auth);
         requireOperation(operation);
         if(restored.error||!restored.data.session)throw restored.error||new Error('replacement_session_unavailable');
         await forgetOperation(operation);requireOperation(operation);
         replacementRecovery.current=null;setFileRecovery(false);setCleanupError('');current.current=null;signingOut.current=false;cleanupOperation.current=null;
         acceptSession.current?.(restored.data.session);return;
       }
       await forgetOperation(operation);
     }else{
       // Private custody faults never gate the ordinary provider-local attempt.
       try{await beginOperation(operation);}catch{/* No known native cleanup to complete. */}
     }
     // Private custody may have changed while observing the SDK. Its provider
     // attempt/removal still concerns only the verified original auth session;
     // private ownership is rechecked before any later custody completion.
     await finishOriginalAuthLogout(operation.original,()=>cleanupOperation.current===operation&&authCleanupIsCurrent(operation.auth),operation.auth);
     requireOperation(operation);
     try{await forgetOperation(operation,!nativeCleanup);}catch(error){
       let pending=nativeCleanup||(error as {code?:string})?.code==='file_cleanup_required';
       if(!pending)try{pending=Boolean(pendingFileIdentity());}catch{pending=true;}
       if(pending||!operationCurrent(operation))throw error;
     }
     requireOperation(operation);
     cleanupOperation.current=null;setFileRecovery(false);setCleanupError('');setLoginError('');clearPasswordFlow();clear();current.current=null;setIdentity(null);setPasswordFlow(null);setAuthReady(true);
   }catch(error){
     const operation=initializedOperation;
     if(operation&&!operationCurrent(operation)){
       signingOut.current=false;
       try{await resumeSuperseded(operation);return;}catch{/* Unknown/new original work stays recoverable. */}
     }
     // SDK failures retain their established ordinary retry presentation. Private
     // failures retain the native cleanup retry and never admit old rendered data.
     if(operation&&!unknownCustody&&operationCurrent(operation)&&(error as {code?:string})?.code==='ordinary_auth_logout_failed'){
       setLoginError('We could not sign you out. Please try again.');setError('We could not sign you out. Please try again.');setAuthReady(true);
     }else{setFileRecovery(true);setCleanupError(unfinishedSignOut);setIdentity(null);setAuthReady(true);}
   }finally{signingOut.current=false;}
 }

 const launcher=useCurrentApps(directory,identity&&!passwordFlow&&!cleanupError?{accountId:identity.id,accessToken:identity.token}:null,!authReady);
 useEffect(()=>{const back=()=>{
   const wasFilter=dialog.current?.open;dialog.current?.close();
   if(pendingFilters.current){setApplied(pendingFilters.current);pendingFilters.current=null;filterButton.current?.focus();return;}
   if(wasFilter){filterButton.current?.focus();return;}
   const params=new URLSearchParams(location.search);
   clear(false);setReload(v=>v+1);setPoemId(params.get('poem')||'');setView(params.get('view')==='sources'?'sources':'poems');
   setApplied({...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>params.has(k)).map(k=>[k,params.get(k)!]))});
 };window.addEventListener('popstate',back);return ()=>window.removeEventListener('popstate',back);},[]);
 function navigateView(next:string){if(next===view&&!poemId)return;const params=new URLSearchParams(applied);if(next==='sources')params.set('view','sources');history.pushState(null,'','?'+params);clear(false);setView(next);setPoemId('');window.scrollTo(0,0);}
 function navigatePoem(id:string){if(id===poemId)return;const params=new URLSearchParams(applied);if(id)params.set('poem',id);history.pushState(null,'','?'+params);clear(false);setPoemId(id);window.scrollTo(0,0);}

 function closeFilters(apply=false){if(apply)pendingFilters.current=draft;if(history.state?.ptsFilters)history.back();else{dialog.current?.close();if(apply){setApplied(draft);pendingFilters.current=null;}filterButton.current?.focus();}}
 async function request<T>(path:string,{signal,corpus=false}:{signal?:AbortSignal;corpus?:boolean}={}):Promise<T>{
   if(corpus&&signingOut.current)throw new DOMException('Sign-out in progress','AbortError');
   if(!current.current)throw new Error('Please sign in again to continue.');
   const atStart=current.current.id,epoch=authorityEpoch.current,cache=corpusCache.current;
   return withDeadline(async bounded=>{
     const stillCurrent=()=>!bounded.aborted&&(!corpus||!signingOut.current)&&authorityEpoch.current===epoch&&current.current?.id===atStart;
     const requireCurrent=()=>{if(!stillCurrent())throw new DOMException('Session or request changed','AbortError');};
     const send=async(etag?:string)=>{
       let response=await fetch(base+path,{headers:{Authorization:'Bearer '+current.current!.token,...(etag?{'If-None-Match':etag}:{})},cache:'no-store',signal:bounded});
       if(response.status===401){
         const refreshed=await auth.refreshSession();requireCurrent();
         if(refreshed.data.session?.user.id===atStart){
           response=await fetch(base+path,{headers:{Authorization:'Bearer '+refreshed.data.session.access_token,...(etag?{'If-None-Match':etag}:{})},cache:'no-store',signal:bounded});
         }
       }
       requireCurrent();
       if(!response.ok&&response.status!==304){
         if(response.status===401||response.status===403){clear(true,false);setLoading(false);if(response.status===401)setIdentity(null);}
         const messages:Record<number,string>={401:'Please sign in again to continue.',403:'You do not currently have access to this collection or action.',404:'This poem or document is unavailable.',503:'We could not verify access or complete this request. Please retry.'};
         throw Object.assign(new Error(messages[response.status]||'We could not complete this request. Please retry.'),{authorityFailure:response.status===401||response.status===403});
       }
       return response;
     };
     if(corpus)return cache.read(path,send,stillCurrent) as Promise<T>;
     const response=await send();
     const body=await ((response.headers.get('content-type')||'').includes('json')?response.json():response.text());
     requireCurrent();
     return body as T;
   },{signal,timeoutMs:60_000});
 }
 const query=new URLSearchParams(applied).toString();
 useEffect(()=>{
   if(!identity||passwordFlow||!authReady||cleanupError||signingOut.current)return;
   const serial=++generation.current,controller=new AbortController();readController.current=controller;readBusy.current=true;lastRead.current=Date.now();
   setLoading(true);setError('');
   const path=view==='sources'?'/api/sources':poemId?'/api/poetry/'+encodeURIComponent(poemId):'/api/poetry?'+query+'&lean=true';
   const selection=identity.id+'\n'+path;
   if(readSelection.current!==selection){readSelection.current=selection;setData(null);setSingle(null);setSources(null);}
   request<CollectionResponse|PoemResponse|SourcesResponse>(path,{signal:controller.signal,corpus:true}).then(result=>{
     if(serial===generation.current&&!signingOut.current){if(view==='sources')setSources(result as SourcesResponse);else if(poemId)setSingle(result as PoemResponse);else setData(result as CollectionResponse);}
   }).catch(e=>{if(e.name==='AbortError')return;if(serial===generation.current||e.authorityFailure)setError(e.message||'We could not load the collection. Please retry.');}).finally(()=>{if(readController.current===controller){readBusy.current=false;setLoading(false);}});
   const params=new URLSearchParams(applied);if(view==='sources')params.set('view','sources');else if(poemId)params.set('poem',poemId);
   history.replaceState(history.state,'','?'+params);
   return ()=>{generation.current++;controller.abort();};
 },[identity?.id,identity?.token,query,poemId,view,reload,passwordFlow,authReady,cleanupError]);
 useEffect(()=>{const refresh=()=>{if(document.visibilityState==='visible'&&!signingOut.current&&!readBusy.current&&Date.now()-lastRead.current>=1000)setReload(v=>v+1);};window.addEventListener('focus',refresh);document.addEventListener('visibilitychange',refresh);return ()=>{window.removeEventListener('focus',refresh);document.removeEventListener('visibilitychange',refresh);};},[]);
 const selection:Selection|null=single?.evidence||data;
 const poems=single?[single.poem]:(data?.poems||[]);
 async function copy(id:string){const epoch=authorityEpoch.current;try{const result=await request<PoemResponse>('/api/poetry/'+encodeURIComponent(id));if(epoch!==authorityEpoch.current)return;try{await navigator.clipboard.writeText(result.citation);if(epoch!==authorityEpoch.current)return;setNotice('Copied poem with citation, quality and reuse notes.');}catch{if(epoch!==authorityEpoch.current)return;setCopyText(result.citation);copyDialog.current?.showModal();}}catch(e){setError((e as Error).message);}}
 async function exportResult(format:'json'|'text'){const epoch=authorityEpoch.current;try{const result=await request<unknown>('/api/exports?'+query+'&format='+format);if(epoch!==authorityEpoch.current)return;const blob=new Blob([format==='json'?JSON.stringify(result,null,2):String(result)],{type:format==='json'?'application/json':'text/plain'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='Swahili-poetry-selection.'+(format==='json'?'json':'txt');a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice('Exported current results with source rights and alternate witnesses.');}catch(e){setError((e as Error).message);}}
 async function openDocument(id:string,presentation:'open'|'download'='open'){
   const epoch=authorityEpoch.current, account=current.current?.id;
   try{
     const result=await request<DocumentResponse>('/api/documents/'+encodeURIComponent(id));
     if(epoch!==authorityEpoch.current||current.current?.id!==account)return;
     let url:string|undefined;
     if(result.status==='link_only')url=safeLink(result.url);
     else {
       let identity=current.current!;
       try{await establishFiles(identity);}
       catch(error){
         if((error as {status?:number}).status!==401)throw error;
         const refreshed=await auth.refreshSession();
         if(epoch!==authorityEpoch.current||current.current?.id!==account||!refreshed.data.session||refreshed.data.session.user.id!==account)return;
         identity={id:account!,token:refreshed.data.session.access_token};
         await establishFiles(identity);
       }
       if(epoch!==authorityEpoch.current||current.current?.id!==account)return;
       url=await fileContext(id,presentation,identity);
     }
     if(epoch!==authorityEpoch.current||current.current?.id!==account)return;
     if(!url)throw new Error('The document link is unavailable.');
     setDocumentUrl(url);window.open(url,'_blank','noopener,noreferrer');
     setNotice(result.status==='link_only'?'Opened the original reference. No local copy is held.':'Opened private document. Return here to reopen if your session expires.');
   }catch(e){if(epoch===authorityEpoch.current||((e as {authorityFailure?:boolean}).authorityFailure&&current.current?.id===account))setError((e as Error).message);}
 }
 function filterFields(values:Filters,update:(f:Filters)=>void,prefix:string){return <><label>Show poems<select value={values.availability} onChange={e=>update({...values,availability:e.target.value})}><option value="text">Poems with text</option><option value="research">Ready for team research</option><option value="checked">Source-checked complete texts</option><option value="review">Texts needing proofreading</option><option value="all">All catalogue entries, including missing texts</option></select></label>{(['source','genre','origin','dialect','status'] as const).map(key=><label key={key}>{key==='status'?'Text status':key[0].toUpperCase()+key.slice(1)}<select id={prefix+key} value={values[key]} onChange={e=>update({...values,[key]:e.target.value})}><option value="">All {key==='status'?'statuses':key+'s'}</option>{(data?.filters[key]||[]).map(v=><option key={v} value={v}>{v.replaceAll('_',' ')}</option>)}</select></label>)}</>;}
 function showFilters(){setDraft(applied);history.pushState({ptsFilters:true},'',location.href);dialog.current?.showModal();}
 const changed=Object.keys(defaults).filter(k=>applied[k as keyof Filters]!==defaults[k as keyof Filters]).length;
 return <><header className="shell"><AppLauncher apps={launcher.apps} status={launcher.status} onRetry={launcher.refresh} onRefresh={launcher.refresh} onSignIn={()=>{clear();setIdentity(null);}} currentAppId="pts"/><a href="?" className="brand">PtS</a><span>Swahili Poetry</span>{(identity||fileRecovery)&&<button className="signout" onClick={signOut}>Sign out</button>}</header><main>
 {view==='sources'&&<h1>Sources</h1>}
 {cleanupError&&<div role="alert" className="error">{cleanupError} <button onClick={signOut}>Retry Sign out</button></div>}
 {!authReady?<p role="status">Checking your session…</p>:(!identity||passwordFlow)?<LoginForm key={(identity?.id||'signed-out')+':'+passwordFlow+':'+loginError} flow={passwordFlow} initialError={loginError} onPasswordSaved={passwordSaved}/>:<>
 <>
 <nav className="source-actions" aria-label="Swahili Poetry views"><button aria-current={view==='poems'?'page':undefined} onClick={()=>navigateView('poems')}>Poems</button><button aria-current={view==='sources'?'page':undefined} onClick={()=>navigateView('sources')}>Sources</button></nav>
 {view==='poems'&&!poemId&&<section aria-label="Collection filters" className="panel">
  <div className="simple-search"><label>Search poems<input type="search" aria-label="Search title, poet, place, form or dialect" placeholder="Title, poet, place, form or dialect" value={applied.search} onChange={e=>setApplied({...applied,search:e.target.value})}/></label>
  <label>Dialect<select value={applied.dialect} onChange={e=>setApplied({...applied,dialect:e.target.value})}><option value="">All dialects</option>{(data?.filters.dialect||[]).map(v=><option key={v} value={v}>{v}</option>)}</select></label></div>
  <div className="simple-actions"><label className="check-label"><input type="checkbox" checked={applied.availability==='research'} onChange={e=>setApplied({...applied,availability:e.target.checked?'research':'text'})}/>Ready for team research</label>
  <button ref={filterButton} aria-label={'Filters'+(changed?' ('+changed+')':'')} onClick={showFilters}>More filters{changed?' ('+changed+')':''}</button>{changed>0&&<button className="quiet" onClick={()=>setApplied(defaults)}>Reset filters</button>}</div>
  <details className="scope-note"><summary>What does “ready” mean?</summary><p>A complete text checked against its source, with recorded rights supporting this private, noncommercial AI-training project. Assistant text checks are separate from expert language review. A different purpose or public release needs a new rights assessment.</p><p>Swahili is the language. Kiunguja, Kiamu and Kimvita are dialects. A poem’s place of collection does not establish its dialect.</p></details>
 </section>}
 <p role="status" className="reader-progress">{loading&&<><span className="spinner" aria-hidden="true"/>{data||single||sources?'Checking for updates':'Loading '+(view==='sources'?'sources':'poems')}…</>}</p>{error&&<div role="alert" className="error">{error} <button onClick={()=>{setError('');setLoading(false);setReload(v=>v+1);}}>Retry</button></div>}<p role="status">{notice}</p>{documentUrl&&<p><a href={documentUrl} target="_blank" rel="noreferrer">Open document in a new tab</a></p>}
 {view==='sources'&&sources&&<SourcesView data={sources} onOpenDocument={openDocument}/>}
 {view==='poems'&&poemId&&<button onClick={()=>navigatePoem('')}>Back to results</button>}
 {data&&<CollectionStats poems={data.poems} usage={data.research_usage}/>}
 {data&&<div className="result-tools"><p>{data.total} {applied.availability==='all'?'catalogue entries':'poems and excerpts'} shown</p><button disabled={!data.total} onClick={()=>exportResult('text')}>Download poems</button><details className="download-options"><summary>Other downloads</summary><button disabled={!data.total} onClick={()=>exportResult('json')}>Export results (JSON)</button><button disabled={!data.total} onClick={()=>exportResult('text')}>Export results (text)</button></details></div>}
 {data&&<details className="panel"><summary>Collection references and document notices</summary>{data.source_documents.filter(d=>!d.source_id).map(d=><section key={d.id}><h3>{d.title}</h3><p>{d.copying_basis}</p><button onClick={()=>openDocument(d.id)}>Open reference document</button></section>)}</details>}
 {!loading&&data&&poems.length===0&&<div className="panel"><p>No poems match these filters.</p>{applied.availability==='research'&&<p>Some texts may still need proofreading or a rights assessment for this private project. Browse poems with text to see them.</p>}<button onClick={()=>setApplied(defaults)}>Clear filters</button></div>}
 {poems.map(p=><article key={p.id} id={p.id}>
 <h2><a href={'?'+new URLSearchParams({...applied,poem:p.id})} onClick={e=>{e.preventDefault();navigatePoem(p.id);}}>{p.title}</a></h2>
 <p className="metadata"><b>Poet:</b> {p.creator?.name||'Unattributed'} · <b>Origin:</b> {p.geography?.origin_locality||'Not recorded'}<br/><b>Form:</b> {p.classification?.formal_poetry_type||p.classification?.genre||'Not recorded'} · <b>Dialect:</b> {p.geography?.dialect||'Not recorded'}</p>
 <PoemLength poem={p}/>
 <div className="poem-badges"><UsageBadge usage={selection?.research_usage?.[p.id]}/><TextBadge poem={p}/></div>
 {p.text?<pre className="poem-text" lang="sw">{p.text}</pre>:<p>Text has not been collected for this record.</p>}
 <button className="copy-poem" onClick={()=>copy(p.id)}><Copy size={17} aria-hidden="true"/>Copy poem with citation</button>
 <details className="poem-details"><summary>Usage and source details</summary>
 <UsagePanel usage={selection?.research_usage?.[p.id]}/>
 <details><summary>Text review</summary><p>{p.quality?.notes}</p><p>{p.quality?.reviewer_note||'Independent language review is not recorded.'}</p></details>
 <h3>Citation</h3><p>{p.source?.citation} {p.source?.locator}</p>{safeLink(p.source?.url)&&<a href={p.source.url} target="_blank" rel="noreferrer">Original source reference</a>}
 {selection?.source_documents.filter(d=>d.source_id===p.source_id||selection.witnesses.some(w=>w.poem_id===p.id&&w.source_id===d.source_id)).map(d=><section key={d.id}><h3>{d.title}</h3><button onClick={()=>openDocument(d.id)}>{d.local_path?'Open source document':'Open source reference'}</button>{d.local_path&&<button onClick={()=>openDocument(d.id,'download')}>Download source document</button>}<details><summary>Copying notices</summary><p>{d.copying_basis}</p></details></section>)}
 <details><summary>Licence and evidence</summary>{selection?.sources.filter(s=>s.id===p.source_id||selection.witnesses.some(w=>w.poem_id===p.id&&w.source_id===s.id)).map(s=><section key={s.id}><h4>{s.title}</h4><RecordFields record={selection.rights.find(r=>r.id===s.rights_id)||{}} keys={['licence','scope','assessment','attribution','research_use','publication_and_commercial_use','review_status','assessment_date','evidence_urls']}/></section>)}</details>
 <details><summary>Other source versions</summary>{selection?.witnesses.filter(w=>w.poem_id===p.id).map(w=><section key={w.id}><p>{w.locator}</p><p>{w.note}</p><pre className="witness-text" lang="sw">{w.text}</pre><details><summary>Technical witness record</summary><pre>{JSON.stringify(w,null,2)}</pre></details></section>)}</details>
 <details><summary>Technical record and history</summary><pre>{JSON.stringify(p,null,2)}</pre></details>
 </details></article>)}
 </>
 </>}
 </main>
 <dialog ref={dialog} aria-labelledby="filter-title" onCancel={e=>{e.preventDefault();closeFilters();}}><div className="dialog-head"><h2 id="filter-title">More filters</h2><button onClick={()=>closeFilters()}>Close</button><button onClick={()=>setDraft(defaults)}>Reset filters</button></div><div className="dialog-body">{filterFields(draft,setDraft,'advanced-')}</div><div className="dialog-footer"><button onClick={()=>closeFilters(true)}>Apply filters</button></div></dialog>
 <dialog ref={copyDialog} aria-labelledby="copy-title"><h2 id="copy-title">Copy poem with citation</h2><p>Select and copy this text.</p><textarea aria-label="Poem and citation" value={copyText} readOnly onFocus={e=>e.target.select()}/><button onClick={()=>copyDialog.current?.close()}>Close</button></dialog></>;
}
createRoot(document.getElementById('root')!).render(<App/>);
