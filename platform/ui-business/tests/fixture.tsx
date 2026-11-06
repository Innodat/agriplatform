import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import {AppLauncher,useCurrentApps,type LauncherSession} from '../src/index';
import {createAppDirectoryClient} from '../../app-directory-client/src/index';
const client=createAppDirectoryClient({baseUrl:location.origin});
function Fixture(){
 const [session,setSession]=useState<LauncherSession|null>({accountId:'first',accessToken:'first'});
 Object.assign(window,{setLauncherSession:setSession});
 const state=useCurrentApps(client,session);
 return <><AppLauncher apps={state.apps} status={state.status} onRetry={state.refresh} onRefresh={state.refresh}/><a href="#after">After launcher</a><div data-observation data-status={state.status}>{state.status}</div></>;
}
createRoot(document.getElementById('root')!).render(<Fixture/>);
