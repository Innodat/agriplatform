import {useCallback,useEffect,useRef,useState} from 'react';
import {AppDirectoryError,type AppDirectoryClient,type AppEntry} from '@platform/app-directory-client';
export type LauncherStatus='loading'|'complete'|'sign_in_required'|'authentication_required'|'access_denied'|'unavailable';
export interface LauncherSession {accountId:string;accessToken:string;generation?:string|number;}
export interface CurrentAppsState {apps:AppEntry[];status:LauncherStatus;refresh:()=>void;}
/** Host identity binds each observation; token refresh and account changes mask it during render. */
export function useCurrentApps(client:AppDirectoryClient,session:LauncherSession|null,sessionLoading=false):CurrentAppsState {
  const key=JSON.stringify([session?.accountId,session?.accessToken,session?.generation,sessionLoading]);
  // A restored key starts a new observation even if its earlier result is retained.
  const current=useRef({key});
  if(current.current.key!==key)current.current={key};
  const binding=current.current;
  const [revision,setRevision]=useState(0);
  const activeRevision=useRef(revision);activeRevision.current=revision;
  const [observation,setObservation]=useState<{binding:typeof binding;revision:number;apps:AppEntry[];status:LauncherStatus}|null>(null);
  const refresh=useCallback(()=>setRevision(value=>value+1),[]);
  useEffect(()=>{
    if(sessionLoading||!session)return;
    let active=true;const controller=new AbortController();
    const accept=(apps:AppEntry[],status:LauncherStatus)=>{
      if(active&&current.current===binding&&activeRevision.current===revision)setObservation({binding,revision,apps,status});
    };
    client.getCurrentApps({token:session.accessToken,signal:controller.signal}).then(result=>accept(result.apps,result.protected_access_status)).catch(error=>{
      if(error instanceof AppDirectoryError&&error.errorId==='request_cancelled')return;
      accept([],error instanceof AppDirectoryError&&error.errorId==='authentication_required'?'authentication_required':error instanceof AppDirectoryError&&error.errorId==='access_denied'?'access_denied':'unavailable');
    });
    return ()=>{active=false;controller.abort();};
  },[client,binding,revision]);
  useEffect(()=>{
    const focus=()=>{if(document.visibilityState==='visible')refresh();};
    window.addEventListener('focus',focus);document.addEventListener('visibilitychange',focus);
    return ()=>{window.removeEventListener('focus',focus);document.removeEventListener('visibilitychange',focus);};
  },[refresh]);
  if(sessionLoading)return {apps:[],status:'loading',refresh};
  if(!session)return {apps:[],status:'sign_in_required',refresh};
  if(observation?.binding!==binding||observation.revision!==revision)return {apps:[],status:'loading',refresh};
  return {apps:observation.apps,status:observation.status,refresh};
}
