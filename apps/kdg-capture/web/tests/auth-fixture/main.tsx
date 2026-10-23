// Select a synthetic journey before creating any SDK client or React owner.
import {createRoot} from 'react-dom/client';
import '../../src/entry-screen.css';
const query=new URLSearchParams(location.search);
if(query.has('local-entry')){
 sessionStorage.setItem('local-entry-fixture','1');
 void import('./local-entry').then(module=>module.mountLocalEntry(createRoot(document.getElementById('root')!)));
}else if(query.has('email-code')){
 sessionStorage.removeItem('local-entry-fixture');
 void import('./email-code').then(module=>module.mountEmailCode(createRoot(document.getElementById('root')!)));
}else if(sessionStorage.getItem('local-entry-fixture')==='1'){
 void import('./local-entry').then(module=>module.mountLocalEntry(createRoot(document.getElementById('root')!)));
}else void import('./legacy-entry');
