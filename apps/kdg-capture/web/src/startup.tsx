import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {readEmbeddedPublicConfig,observeBrowserEntry} from './auth/lifecycle';
import {parseKdgLocalPublicConfig} from './local-public-config';
import {ClosedEntry} from './ClosedEntry';
import {EntryScreen} from './EntryScreen';
import './entry-screen.css';
/** SDK modules are deliberately absent from the preflight import graph. */
export function startKdgLocalFrontend(){
 const roots=document.querySelectorAll('#root');
 if(roots.length!==1||!(roots[0] instanceof HTMLElement)){
  const route=observeBrowserEntry({browser:window,paths:['/','/admin'],safePath:'/',anchors:['#kdg-entry-content','#admin-main'],publish:()=>{}});route.start();route.dispose();return null;
 }
 const value=readEmbeddedPublicConfig(document,'kdg-local-config');
 const config=value.kind==='value'?parseKdgLocalPublicConfig(value.value,location.origin):null;
 const root=createRoot(roots[0]);let disposed=false,loading=false;
 let mounted:{dispose():void}|undefined;
 const observer=observeBrowserEntry({browser:window,paths:['/','/admin'],safePath:'/',anchors:['#kdg-entry-content','#admin-main'],publish:state=>{
  if(disposed)return;
  if(!config||state.route!=='entry'||!state.online){
   flushSync(()=>root.render(<ClosedEntry state={state} failed={!config}/>));return;
  }
  flushSync(()=>root.render(<EntryScreen state={{kind:'checking'}} online={true} onSignIn={()=>{}} onRetry={()=>{}}/>));
  if(loading)return;loading=true;
  void import('./LocalEntryRoute').then(module=>{
   if(disposed)return;
   const current=observer.state();
   if(current.route!=='entry'||!current.online){loading=false;return;}
   observer.dispose();mounted=module.mountKdgLocalEntry(root,config);
  }).catch(()=>{if(!disposed){loading=false;flushSync(()=>root.render(<ClosedEntry state={observer.state()} failed={true}/>));}});
 }});
 observer.start();
 return{dispose(){if(disposed)return;disposed=true;observer.dispose();if(mounted)mounted.dispose();else flushSync(()=>root.unmount());}};
}
