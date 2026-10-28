/** Explicit host only. Existing application startup does not import this module. */
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {AdminPortal} from './AdminPortal.js';
import {createAdminPortal,type AdminPortalOptions} from './admin-portal.js';

export function mountAdminPortalPreview(element:HTMLElement,options:AdminPortalOptions){
 const portal=createAdminPortal({...options,online:options.online??navigator.onLine}),root=createRoot(element);
 flushSync(()=>root.render(<AdminPortal portal={portal} from_date={options.from_date} to_date={options.to_date}/>));
 const offline=()=>{void portal.online(false);},online=()=>{void portal.online(true);};
 window.addEventListener('offline',offline);window.addEventListener('online',online);
 void portal.start();
 return {portal,dispose(){window.removeEventListener('offline',offline);window.removeEventListener('online',online);portal.dispose();flushSync(()=>root.unmount());}};
}
