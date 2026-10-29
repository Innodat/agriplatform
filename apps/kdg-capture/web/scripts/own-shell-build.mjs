/** KDG-owned shell: emitted production bytes only; no development module caching. */
import {createHash} from 'node:crypto';
// Neutral shadcn primary/background from entry-screen.css; a document symbol, not a logo.
const icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><title>Observation document</title><rect width="192" height="192" rx="24" fill="#ffffff"/><g fill="none" stroke="#171717" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"><path d="M64 36h48l24 24v96H56V36h8Z"/><path d="M112 36v24h24M76 88h40M76 112h40M76 136h24"/></g></svg>';
const manifest=JSON.stringify({id:'/',name:'KDG Capture',short_name:'KDG Capture',start_url:'/',scope:'/',display:'standalone',background_color:'#ffffff',theme_color:'#171717',icons:[{src:'/icon.svg',sizes:'any',type:'image/svg+xml',purpose:'any'}]});
export function ownShellBuild(){return {name:'kdg-public-built-shell',apply:'build',enforce:'post',generateBundle(_options,bundle){
 const files=Object.entries(bundle).filter(([name,item])=>name==='index.html'||(/^assets\/[A-Za-z0-9_./-]+\.(?:js|css)$/.test(name)&&(item.type==='chunk'||item.type==='asset'))).map(([name,item])=>[name==='index.html'?'/':'/'+name,item.type==='chunk'?item.code:item.source]);
 if(!files.some(([name])=>name==='/'))throw Error('kdg_shell_index_missing');
 files.push(['/manifest.webmanifest',manifest],['/icon.svg',icon]);files.sort(([a],[b])=>a.localeCompare(b));
 const digest=createHash('sha256');for(const [name,source] of files)digest.update(name).update('\0').update(source).update('\0');
 const revision=digest.digest('hex').slice(0,24),assets=files.map(([name])=>name);
 const source=`// Generated from exact built public bytes; retained caches are never deleted.\nconst REVISION=${JSON.stringify(revision)},CACHE='kdg-shell-'+REVISION,ASSETS=${JSON.stringify(assets)};
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE),controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
 try{for(const path of ASSETS){const response=await fetch(new Request(path,{cache:'reload',credentials:'omit',redirect:'error',signal:controller.signal}));if(!response.ok||response.type==='opaque')throw Error('shell_asset_unavailable');await cache.put(path,response);}}finally{clearTimeout(timer);}
})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('message',event=>{
 if(event.data?.kind==='kdg-shell-ready')event.waitUntil((async()=>{let ready=false;try{const cache=await caches.open(CACHE);ready=(await Promise.all(ASSETS.map(path=>cache.match(path)))).every(Boolean);}catch{}event.ports[0]?.postMessage({kind:'kdg-shell-ready',revision:REVISION,ready});})());
 if(event.data?.kind==='kdg-shell-activate')event.waitUntil(self.skipWaiting());
});
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==self.location.origin||url.search||url.hash)return;
 // Exact own root only. API, Auth, provider, admin and other navigations stay network-only.
 if(request.mode==='navigate'){
  if(url.pathname!=='/')return;
  event.respondWith(fetch(request).catch(async()=>{const cached=await (await caches.open(CACHE)).match('/');return cached??Response.error();}));return;
 }
 if(ASSETS.includes(url.pathname)){event.respondWith((async()=>{const cached=await (await caches.open(CACHE)).match(url.pathname);return cached??fetch(request);})());return;}
 // A live older tab may still request its retained content-hashed assets after explicit activation.
 if(/^\\/assets\\/[A-Za-z0-9_./-]+\\.(?:js|css)$/.test(url.pathname))event.respondWith((async()=>{
  for(const name of await caches.keys()){if(!/^kdg-shell-[a-f0-9]{24}$/.test(name))continue;const cached=await (await caches.open(name)).match(url.pathname);if(cached)return cached;}
  return fetch(request);
 })());
});\n`;
 this.emitFile({type:'asset',fileName:'sw.js',source});this.emitFile({type:'asset',fileName:'manifest.webmanifest',source:manifest});this.emitFile({type:'asset',fileName:'icon.svg',source:icon});
 }};}
