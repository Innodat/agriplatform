import {startKdgLocalFrontend} from './startup';
let active=startKdgLocalFrontend();
window.addEventListener('pagehide',()=>{active?.dispose();active=null;});
window.addEventListener('pageshow',event=>{if(event.persisted&&!active)active=startKdgLocalFrontend();});
