import {useLayoutEffect,useState} from 'react';
import {AdminPortal} from './AdminPortal';
import {createAdminPortal,type AdminPortalController} from './admin-portal';
import type {AuthEntryProps} from './AuthEntry';
/** App-owned all-read composition. One controller per stable Auth/scope/launch owner. */
export function AdminEntry({auth,org,request,beginSignIn,online=true,timeoutMs}:AuthEntryProps){
 const [mounted,setMounted]=useState<{portal:AdminPortalController;from:string;to:string}|null>(null);
 useLayoutEffect(()=>{
  const to=new Date().toISOString().slice(0,10),from=to.slice(0,4)+'-01-01';
  const portal=createAdminPortal({auth,org_id:org,request,beginSignIn,online,timeoutMs,from_date:from,to_date:to});
  setMounted({portal,from,to});void portal.start();
  return()=>portal.dispose();
  // Connectivity changes invalidate the same controller; they do not replace Auth ownership.
 },[auth,org,request,beginSignIn,timeoutMs]);
 useLayoutEffect(()=>{if(mounted)void mounted.portal.online(online);},[mounted,online]);
 return mounted?<AdminPortal portal={mounted.portal} from_date={mounted.from} to_date={mounted.to} onSignIn={beginSignIn}/>:<p role="status">Checking administrator access…</p>;
}
