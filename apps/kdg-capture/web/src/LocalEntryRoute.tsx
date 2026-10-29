import {ClosedEntry} from './ClosedEntry';
import {EntryScreen} from './EntryScreen';
import {StrictMode} from 'react';
import {flushSync} from 'react-dom';
import type {Root} from 'react-dom/client';
import {EmailCodeEntry} from './EmailCodeEntry';
import {observeBrowserEntry,type BrowserEntryPort,type SessionStoragePort} from './auth/lifecycle';
import './entry-screen.css';
type KdgEmailAuth=ReturnType<typeof import('./email-auth')['createKdgEmailAuth']>;
type LocalEntryBrowser=BrowserEntryPort&{readonly localStorage:SessionStoragePort};
export type LocalEntryOptions=Readonly<{org:string;url:string;publicKey:string;browser?:LocalEntryBrowser;storage?:SessionStoragePort;authRequest?:typeof fetch;request?:typeof fetch}>;
/** One stable own composition survives offline startup and first lazy SDK acquisition. */
export function mountKdgLocalEntry(root:Root,options:LocalEntryOptions){
 const {org,url,publicKey,storage,authRequest,request}=options,browser=options.browser??window;
 const orgValid=typeof org==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(org)&&org!=='00000000-0000-0000-0000-000000000000';
 let auth:KdgEmailAuth|undefined,failed=!orgValid,disposed=false,refreshing=false,loading=false;
 function refresh(enabled:boolean){if(!auth||enabled===refreshing)return;refreshing=enabled;void(enabled?auth.startAutoRefresh():auth.stopAutoRefresh()).catch(()=>{});}
 const observer=observeBrowserEntry({browser,paths:['/','/admin'],safePath:'/',anchors:['#kdg-entry-content','#admin-main'],publish:render});
 function render(state:ReturnType<typeof observer.state>){
  if(disposed)return;
  if(state.route==='entry'&&state.online&&!failed&&!auth&&!loading){
   loading=true;
   void import('./email-auth').then(module=>{
    loading=false;if(disposed||observer.state().route!=='entry'||!observer.state().online)return;
    try{auth=module.createKdgEmailAuth({url,publicKey,storage:storage??browser.localStorage,request:authRequest});refreshing=true;}catch{failed=true;}
    render(observer.state());
   }).catch(()=>{loading=false;if(!disposed){failed=true;render(observer.state());}});
  }
  refresh(state.route==='entry'&&state.online&&!failed);
  flushSync(()=>root.render(<StrictMode>{state.route==='entry'&&!failed&&(browser.location.pathname==='/'||auth)?
   <EmailCodeEntry key={browser.location.pathname} surface={browser.location.pathname==='/admin'?'admin':'own'} org={org} auth={auth} request={request} online={state.online}/>:
   state.route==='entry'&&!failed&&state.online?<EntryScreen state={{kind:'checking'}} online={true} onSignIn={()=>{}} onRetry={()=>{}}/>:<ClosedEntry state={state} failed={failed}/>}</StrictMode>));
 }
 observer.start();return {dispose(){if(disposed)return;disposed=true;observer.dispose();flushSync(()=>root.unmount());refresh(false);}};
}
