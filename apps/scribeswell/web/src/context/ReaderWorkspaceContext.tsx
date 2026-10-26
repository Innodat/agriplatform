import {createContext,useContext,useEffect,useLayoutEffect,useRef,useState,type ReactNode,type SetStateAction,type MutableRefObject} from 'react';
import {useReaderWorkspace} from '@/hooks/useReaderWorkspace';
import {readWorkspace,writeWorkspace,type PrivateSetup,type PrivateSelection} from '@/lib/workspace-storage';
import {verifyWorkspaceIdentity} from '@/lib/supabase';
import {useAuth} from './AuthContext';
type Fields=Map<string,unknown>;
type Controller=ReturnType<typeof useReaderWorkspace>;
type DeviceContext={retainPrivateForRetry:()=>void;clearRememberedResource:(study:string,note?:string)=>void;privateIntent:number|undefined;privateRestoreFailure:()=>void;remembered:PrivateSetup|undefined;verifiedAccount:string|undefined;privateProjection:MutableRefObject<()=>PrivateSelection[]>;forgetRemembered:(key?:string)=>void;storageNotice:string;retryStorage:()=>void;deviceReady:boolean;checkpoint:()=>void};
const Context=createContext<(Controller&DeviceContext&{root:React.RefObject<HTMLDivElement|null>;views:Map<string,Fields>;redraw:()=>void;latest:MutableRefObject<Controller>})|null>(null);
export function ReaderWorkspaceProvider({children}:{children:ReactNode}){
 const {session,loading}=useAuth();
 const root=useRef<HTMLDivElement>(null),controller=useReaderWorkspace(root),views=useRef(new Map<string,Fields>()),[,render]=useState(0),latest=useRef(controller);latest.current=controller;
 const [privateIntent,setPrivateIntent]=useState<number>(),[privateSuspended,setPrivateSuspended]=useState(false);
 const [storageNotice,setStorageNotice]=useState(''),[deviceReady,setDeviceReady]=useState(false),[retry,setRetry]=useState(0),[remembered,setRemembered]=useState<PrivateSetup>(),[verified,setVerified]=useState<{account:string;token:string;session:NonNullable<typeof session>}>();
 const liveSession=useRef(session);liveSession.current=session;
 const observedAccount=useRef<{ready:boolean;id?:string}>({ready:false});
 if(!loading){if(observedAccount.current.ready&&observedAccount.current.id!==session?.user.id){controller.deviceIntent.current++;}observedAccount.current={ready:true,id:session?.user.id};}
 const privateProjection=useRef<()=>PrivateSelection[]>(()=>[]),pending=useRef<PrivateSetup|undefined>(undefined),boot=useRef(false),hold=useRef(true),failed=useRef(false),last=useRef('');
 const retainPrivateForRetry=()=>{
  const current=liveSession.current;
  if(current){const value:PrivateSetup={v:1,updated:Date.now(),account:current.user.id,tabs:privateProjection.current()};pending.current=value;setRemembered(value);}
  setPrivateSuspended(true);setVerified(undefined);setPrivateIntent(undefined);setStorageNotice('Private reading context not restored.');
 };
 useEffect(()=>{setPrivateSuspended(false);},[session]);
 const [accountReady,setAccountReady]=useState<string>();
 const storageSequence=useRef(0),storageFailure=useRef(0);
 function storageFailed(operation:number){storageFailure.current=Math.max(storageFailure.current,operation);failed.current=true;setStorageNotice('Reading setup not remembered.');}
 const readGeneration=useRef(0),checking=useRef<string|undefined>(undefined);
 const timers=useRef<{debounce?:ReturnType<typeof setTimeout>;max?:ReturnType<typeof setTimeout>}>({});
 const mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;clearTimeout(timers.current.debounce);clearTimeout(timers.current.max);};},[]);
 const forgetRemembered=(key?:string)=>{const value=pending.current;if(!value)return;const next={...value,tabs:key?value.tabs.filter(t=>t.tabKey!==key):[]};pending.current=next;setRemembered(next);};
 const clearRememberedResource=(study:string,note?:string)=>{
  const value=pending.current;if(!value)return;
  const tabs=value.tabs.flatMap(selection=>{if(selection.study!==study||note&&selection.note!==note)return [selection];if(!note)return [];return [{tabKey:selection.tabKey,incarnation:selection.incarnation,study}];});
  const next={...value,tabs};pending.current=next;setRemembered(next);
 };
 function safePrivate():PrivateSetup|undefined{
  const current=liveSession.current;
  if(privateSuspended||!current||verified?.account!==current.user.id||verified.token!==current.access_token||verified.session!==current)return;
  return {v:1,updated:Date.now(),account:verified.account,tabs:privateProjection.current()};
 }
 const write=useRef<()=>void>(()=>{});
 write.current=()=>{
  clearTimeout(timers.current.debounce);clearTimeout(timers.current.max);timers.current={};
  if(!boot.current||hold.current||failed.current||latest.current.historyHeld||latest.current.devicePending)return;
  const pub=latest.current.deviceProjection(),priv=safePrivate();
  const projection=JSON.stringify([ {...pub,updated:0},priv?{...priv,updated:0}:null ]);
  if(projection===last.current)return;
  const operation=++storageSequence.current;
  void writeWorkspace(pub,priv).then(()=>{if(mounted.current){last.current=projection;if(operation>=storageFailure.current){failed.current=false;setStorageNotice(value=>value==='Reading setup not remembered.'?'':value);}}},()=>{if(mounted.current)storageFailed(operation);});
 };
 function checkpoint(){
  if(!boot.current||hold.current||failed.current)return;
  clearTimeout(timers.current.debounce);timers.current.debounce=setTimeout(()=>write.current(),250);
  if(!timers.current.max)timers.current.max=setTimeout(()=>write.current(),2000);
 }
 controller.onCheckpoint.current=checkpoint;
 controller.removed.current=key=>{views.current.delete(key);forgetRemembered(key);};
 useEffect(()=>{
  const live=new Set(controller.tabs.map(tab=>tab.tabKey));for(const key of views.current.keys())if(!live.has(key))views.current.delete(key);for(const key of controller.inherited.current.keys())if(!live.has(key))controller.inherited.current.delete(key);
 });
 // The first entry was captured by the controller before any checkpoint. Reads never block public rendering.
 useEffect(()=>{
  const generation=++readGeneration.current,operation=++storageSequence.current;let active=true;
  hold.current=true;setDeviceReady(false);
  void readWorkspace().then(result=>{
   if(!active||generation!==readGeneration.current)return;
   boot.current=true;failed.current=false;last.current='';
   if(result.public){const applied=latest.current.restoreDevice(result.public,retry>0);hold.current=!applied;if(!applied)setStorageNotice('Remembered reading setups are ready.');}
   else hold.current=false;
   setDeviceReady(true);if(!hold.current)checkpoint();
  },()=>{if(active){boot.current=true;storageFailed(operation);setDeviceReady(true);}});
  return()=>{active=false;};
 },[retry]);
 // Install completion is identified by the controller's own result, never by URL equality.
 useEffect(()=>{if(controller.deviceInstalled>0){hold.current=false;setStorageNotice('');checkpoint();}},[controller.deviceInstalled]);
 useEffect(()=>{
  let active=true;const account=session?.user.id,retained=pending.current?.account===session?.user.id?pending.current:undefined;
  setVerified(undefined);setPrivateIntent(undefined);checking.current=undefined;pending.current=retained;setRemembered(retained);setAccountReady(undefined);
  if(loading||!account||!deviceReady||hold.current)return;
  const operation=++storageSequence.current;
  void readWorkspace(account).then(result=>{if(active&&liveSession.current?.user.id===account){pending.current=retained??result.private;setRemembered(pending.current);setAccountReady(account);}},()=>{if(active)storageFailed(operation);});
  return()=>{active=false;};
 },[session?.user.id,loading,deviceReady,retry,controller.deviceInstalled]);
 const hasPrivate=privateProjection.current().length>0;
 useEffect(()=>{
  const current=session;if(privateSuspended||hold.current||!current||accountReady!==current.user.id||verified?.account===current.user.id&&verified.token===current.access_token&&verified.session===current||checking.current===current.access_token)return;
  if(!pending.current?.tabs.length&&!privateProjection.current().length)return;
  const intent=latest.current.deviceIntent.current,token=current.access_token,account=current.user.id,cancel=new AbortController();checking.current=token;
  void verifyWorkspaceIdentity(token,cancel.signal).then(result=>{
   if(cancel.signal.aborted||liveSession.current?.access_token!==token||liveSession.current?.user.id!==account||liveSession.current!==current)return;
   checking.current=undefined;
   if('id'in result&&result.id===account){setVerified({account,token,session:current});setPrivateIntent(intent);if(latest.current.deviceIntent.current===intent)setStorageNotice('');else setStorageNotice('Private reading context not restored.');}
   else setStorageNotice('Private reading context not restored.');
  });return()=>{cancel.abort();if(checking.current===token)checking.current=undefined;};
 },[session,remembered,deviceReady,accountReady,hasPrivate,privateSuspended]);
 useEffect(()=>{checkpoint();});
 useLayoutEffect(()=>{
  const intent=(event:Event)=>{if((event.target as Element)?.closest?.('dialog[aria-label="Restore remembered reading setups"]'))return;latest.current.deviceIntent.current++;};
  const node=root.current;for(const event of ['input','pointerdown','keydown','wheel','touchmove'])node?.addEventListener(event,intent,true);
  const flush=()=>write.current();window.addEventListener('pagehide',flush);document.addEventListener('visibilitychange',flush);
  return()=>{for(const event of ['input','pointerdown','keydown','wheel','touchmove'])node?.removeEventListener(event,intent,true);window.removeEventListener('pagehide',flush);document.removeEventListener('visibilitychange',flush);};
 },[]);
 return <Context.Provider value={{...controller,root,views:views.current,redraw:()=>render(n=>n+1),latest,remembered,retainPrivateForRetry,clearRememberedResource,privateIntent,privateRestoreFailure:()=>setStorageNotice('Private reading context not restored.'),verifiedAccount:!privateSuspended&&verified?.session===session?verified?.account:undefined,privateProjection,forgetRemembered,storageNotice,retryStorage:()=>{failed.current=false;setPrivateSuspended(false);setRetry(n=>n+1);},deviceReady:deviceReady&&!hold.current,checkpoint}}>{children}</Context.Provider>;
}
export function useWorkspace(){const value=useContext(Context);if(!value)throw Error('ReaderWorkspaceProvider required');return value;}
/** Setters belong to the originating live view, including after an intentional switch. */
export function useTabState<T>(name:string,initial:T|(()=>T),inherit=false):[T,(value:SetStateAction<T>)=>void]{
 const owner=useWorkspace(),key=owner.workspace.tabKey;
 let fields=owner.views.get(key);if(!fields){fields=new Map();owner.views.set(key,fields);}
 if(!fields.has(name)){
  const origin=owner.inherited.current.get(key),source=origin?owner.views.get(origin):undefined;
  fields.set(name,inherit&&source?.has(name)?source.get(name):typeof initial==='function'?(initial as ()=>T)():initial);
 }
 const captured=fields;
 return [fields.get(name) as T,value=>{
  if(owner.views.get(key)!==captured||!owner.latest.current.tabs.some(tab=>tab.tabKey===key))return;
  captured.set(name,typeof value==='function'?(value as (prior:T)=>T)(captured.get(name) as T):value);owner.redraw();owner.checkpoint();
 }];
}
export function useTabRef<T>(name:string,initial:T):MutableRefObject<T>{return useTabState(`ref:${name}`,()=>({current:initial}))[0];}
