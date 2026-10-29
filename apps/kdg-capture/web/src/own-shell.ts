/** Public shell readiness is independent of atomic IndexedDB provision readiness. */
export type ShellState = Readonly<{ready:boolean;updateAvailable:boolean;revision?:string}>;
let current:ShellState=Object.freeze({ready:false,updateAvailable:false});
let registration:ServiceWorkerRegistration|undefined,preparing:Promise<boolean>|undefined;
let activationRequested=false,pendingReload=false;
const watched=new WeakSet<ServiceWorkerRegistration>();
const listeners=new Set<()=>void>();
function publish(state:ShellState){current=Object.freeze(state);for(const listener of listeners)listener();}
export function shellState():ShellState{return current;}
export function subscribeShellUpdate(callback:()=>void):()=>void{listeners.add(callback);return()=>listeners.delete(callback);}
function bounded<T>(promise:Promise<T>,fallback:T,ms=12000):Promise<T>{return new Promise(resolve=>{const timer=setTimeout(()=>resolve(fallback),ms);promise.then(value=>{clearTimeout(timer);resolve(value);},()=>{clearTimeout(timer);resolve(fallback);});});}
async function verify(worker:ServiceWorker):Promise<{ready:boolean;revision?:string}>{
 const channel=new MessageChannel();
 return new Promise(resolve=>{
  const timer=setTimeout(()=>finish({ready:false}),3000);
  const finish=(value:{ready:boolean;revision?:string})=>{clearTimeout(timer);channel.port1.close();channel.port2.close();resolve(value);};
  channel.port1.onmessage=event=>{const data=event.data;finish(data?.kind==='kdg-shell-ready'&&data.ready===true&&/^[a-f0-9]{24}$/.test(data.revision)?{ready:true,revision:data.revision}:{ready:false});};
  try{worker.postMessage({kind:'kdg-shell-ready'},[channel.port2]);}catch{finish({ready:false});}
 });
}
export function prepareOwnShell():Promise<boolean>{
 if(preparing)return preparing;
 preparing=(async()=>{
  try{
   if(location.pathname!=='/'||location.search||location.hash&&!['#kdg-entry-content'].includes(location.hash)||!isSecureContext||!('serviceWorker' in navigator))return false;
   const registered=await bounded(navigator.serviceWorker.register('/sw.js',{scope:'/',updateViaCache:'none'}),undefined);if(!registered)return false;
   registration=registered;
   const refresh=()=>{publish({...current,updateAvailable:pendingReload||Boolean(registered.waiting)});};
   if(!watched.has(registered)){watched.add(registered);registered.addEventListener('updatefound',()=>{registered.installing?.addEventListener('statechange',refresh);refresh();});}
   // navigator.serviceWorker.ready can wait indefinitely, so keep the readiness operation bounded.
   const active=registered.active??(await bounded(navigator.serviceWorker.ready,undefined))?.active;if(!active)return false;
   const result=await verify(active);publish({...result,updateAvailable:pendingReload||Boolean(registered.waiting)});refresh();return result.ready;
  }catch{return false;}
 })().finally(()=>{preparing=undefined;});return preparing;
}
export async function applyShellUpdate(safety:()=>Readonly<{hasUnsavedInput:boolean;activeWork:boolean}>):Promise<boolean>{
 const safe=()=>{const value=safety();return !value.hasUnsavedInput&&!value.activeWork;};
 if(activationRequested||!safe()||location.pathname!=='/')return false;
 if(pendingReload){location.reload();return true;}
 if(!registration?.waiting)return false;
 activationRequested=true;
 const waiting=registration.waiting,result=await verify(waiting);
 if(!result.ready||!safe()||registration.waiting!==waiting){activationRequested=false;return false;}
 // Only the explicitly requesting tab reloads. Input can become dirty even during activation.
 const changed=()=>{
  navigator.serviceWorker.removeEventListener('controllerchange',changed);clearTimeout(timer);activationRequested=false;
  if(safe())location.reload();
  else{pendingReload=true;publish({...current,updateAvailable:true});}
 };
 navigator.serviceWorker.addEventListener('controllerchange',changed);
 const timer=setTimeout(()=>{navigator.serviceWorker.removeEventListener('controllerchange',changed);activationRequested=false;},12000);
 try{waiting.postMessage({kind:'kdg-shell-activate'});return true;}catch{clearTimeout(timer);navigator.serviceWorker.removeEventListener('controllerchange',changed);activationRequested=false;return false;}
}
