import {ClosedEntry} from './ClosedEntry';
import {StrictMode} from 'react';
import {flushSync} from 'react-dom';
import type {Root} from 'react-dom/client';
import {EmailCodeEntry} from './EmailCodeEntry';
import {createKdgEmailAuth} from './email-auth';
import {observeBrowserEntry,type BrowserEntryPort,type SessionStoragePort} from './auth/lifecycle';
import './entry-screen.css';

type LocalEntryBrowser=BrowserEntryPort&{readonly localStorage:SessionStoragePort};
export type LocalEntryOptions=Readonly<{
 org:string;url:string;publicKey:string;browser?:LocalEntryBrowser;storage?:SessionStoragePort;
 authRequest?:typeof fetch;request?:typeof fetch;
}>;
/** Explicit local/CI host, no automatic startup or environment/provider selection. */
export function mountKdgLocalEntry(root:Root,options:LocalEntryOptions){
 const {org,url,publicKey,storage,authRequest,request}=options,browser=options.browser??window;
 const orgValid=typeof org==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(org)&&org!=='00000000-0000-0000-0000-000000000000';
 let auth:ReturnType<typeof createKdgEmailAuth>|undefined,failed=!orgValid,disposed=false,refreshing=false;
 function refresh(enabled:boolean){
  if(!auth||enabled===refreshing)return;refreshing=enabled;
  void (enabled?auth.startAutoRefresh():auth.stopAutoRefresh()).catch(()=>{/* Admission still requires the current API/session boundary. */});
 }
 const observer=observeBrowserEntry({browser,paths:['/','/admin'],safePath:'/',anchors:['#kdg-entry-content','#admin-main'],publish:state=>{
  if(disposed)return;
  if(state.route==='entry'&&state.online&&!failed&&!auth){
   try{auth=createKdgEmailAuth({url,publicKey,storage:storage??browser.localStorage,request:authRequest});refreshing=true;}
   catch{failed=true;}
  }
  refresh(state.route==='entry'&&state.online&&!failed);
  // Commit refusal now, before another pending SDK completion can mount admission.
  flushSync(()=>root.render(<StrictMode>{state.route==='entry'&&!failed&&auth?
   <EmailCodeEntry key={browser.location.pathname} surface={browser.location.pathname==='/admin'?'admin':'own'} org={org} auth={auth} request={request} online={state.online}/>:
   <ClosedEntry state={state} failed={failed}/>}</StrictMode>));
 }});
 observer.start();
 return{dispose(){if(disposed)return;disposed=true;observer.dispose();flushSync(()=>root.unmount());refresh(false);}};
}
