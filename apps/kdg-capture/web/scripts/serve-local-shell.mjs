// Disposable loopback built-shell host. No provider setup, credentials or release claims.
import {createServer} from 'node:http';
import {readFileSync,readdirSync,lstatSync,realpathSync} from 'node:fs';
import {isAbsolute,join,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual} from 'node:util';
import {createLocalEntryHost} from '../local-host-tools/local-entry-host.mjs';
import {kdgLocalApiRoutes} from '../local-api-routes.mjs';
const invalid=()=>{throw Error('kdg_local_shell_configuration_invalid');};
const appRoot=fileURLToPath(new URL('../../',import.meta.url));
const within=(path,root)=>path===root||path.startsWith(root+sep);
const loopback=url=>['http:','https:'].includes(url.protocol)&&['localhost','127.0.0.1','[::1]'].includes(url.hostname);
// Repeat the closed public input check at this independent non-Vite process edge.
// Never load SDK, environment-derived public values or arbitrary TS/source modules.
function publicInput(value){
 if(Object.keys(value).sort().join(',')!==['auth_public_key','auth_url','environment_kind','org_id','schema_version'].join(','))invalid();
 if(value.schema_version!==1||!['local_disposable','ci_disposable'].includes(value.environment_kind)||typeof value.org_id!=='string'||!/^([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})$/.test(value.org_id)||value.org_id==='00000000-0000-0000-0000-000000000000')invalid();
 const auth=new URL(value.auth_url);if(typeof value.auth_url!=='string'||!loopback(auth)||auth.username||auth.password||auth.pathname!=='/'||auth.search||auth.hash||typeof value.auth_public_key!=='string')invalid();
 let publicOnly=/^sb_publishable_[A-Za-z0-9_-]{10,}$/.test(value.auth_public_key);
 if(!publicOnly){const parts=value.auth_public_key.split('.');publicOnly=parts.length===3&&JSON.parse(Buffer.from(parts[1],'base64url').toString('utf8')).role==='anon';}
 if(!publicOnly)invalid();
 return value;
}
function load({dist,configFile}){
 if(!isAbsolute(dist??'')||!isAbsolute(configFile??''))invalid();
 const root=realpathSync(dist),config=realpathSync(configFile);
 if(root!==resolve(dist)||!lstatSync(root).isDirectory()||[resolve(configFile),config].some(path=>within(path,root)||within(path,resolve(appRoot))||path.split(sep).includes('node_modules'))||!lstatSync(config).isFile()||lstatSync(config).size>8192)invalid();
 const raw=readFileSync(config,'utf8');if(Buffer.byteLength(raw)>8192)invalid();
 const input=JSON.parse(raw);if(!input||typeof input!=='object'||Array.isArray(input)||Object.keys(input).length!==6||!Object.hasOwn(input,'api_origin'))invalid();
 const {api_origin:apiOrigin,...candidate}=input,publicConfig=publicInput(candidate);
 const files=new Map();let total=0;
 const add=(path,type,cache)=>{
  const filename=join(root,path),stat=lstatSync(filename);if(!stat.isFile()||stat.isSymbolicLink()||stat.size>8388608)invalid();
  total+=stat.size;if(total>33554432||files.size>=256)invalid();files.set('/'+path,{body:readFileSync(filename),type,cache});
 };
 add('index.html','text/html; charset=utf-8','no-store');add('sw.js','application/javascript; charset=utf-8','no-store');add('manifest.webmanifest','application/manifest+json','no-cache');add('icon.svg','image/svg+xml','no-cache');
 const assets=join(root,'assets');if(!lstatSync(assets).isDirectory()||lstatSync(assets).isSymbolicLink())invalid();
 for(const entry of readdirSync(assets,{withFileTypes:true})){if(entry.isSymbolicLink()||entry.isDirectory())invalid();if(/^[A-Za-z0-9_-]+\.(?:js|css)$/.test(entry.name))add('assets/'+entry.name,entry.name.endsWith('.js')?'application/javascript; charset=utf-8':'text/css; charset=utf-8','public, max-age=31536000, immutable');}
 const matches=[...files.get('/index.html').body.toString('utf8').matchAll(/<script id="kdg-local-config" type="application\/json">([\s\S]*?)<\/script>/g)];
 if(matches.length!==1||!isDeepStrictEqual(JSON.parse(matches[0][1]),publicConfig))invalid();
 return {files,apiOrigin,publicConfig};
}
export function createLocalShellServer(options){
 try{
  const {files,apiOrigin,publicConfig}=load(options);let proxy;
  createLocalEntryHost({scriptId:'kdg-local-config',publicConfig,apiOrigin,routes:kdgLocalApiRoutes}).plugins[0].configureServer({middlewares:{use:fn=>proxy=fn}});
  const failure=(res,status)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify({error_id:status===405?'method_not_allowed':status===422?'validation_failed':'not_found',error:'The request could not be completed.'}));};
  const server=createServer((req,res)=>{
   const address=server.address();if(!address||typeof address!=='object'||req.headers.host!=='127.0.0.1:'+address.port)return failure(res,404);
   proxy(req,res,()=>{
    const path=(req.url??'').split('?')[0],file=files.get(path==='/'||path==='/admin'?'/index.html':path);
    if(!file||path==='/index.html')return failure(res,404);
    if(!['GET','HEAD'].includes(req.method))return failure(res,405);
    if(req.headers['transfer-encoding']||(req.headers['content-length']&&req.headers['content-length']!=='0')){res.shouldKeepAlive=false;return failure(res,422);}
    res.writeHead(200,{'Content-Type':file.type,'Content-Length':file.body.length,'Cache-Control':file.cache,'X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:file.body);
   });
  });server.requestTimeout=13000;server.headersTimeout=12000;return server;
 }catch{invalid();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  if(process.argv.length!==2)invalid();const raw=process.env.KDG_LOCAL_SHELL_PORT??'5177';if(!/^(?:0|[1-9][0-9]{0,4})$/.test(raw)||Number(raw)>65535)invalid();
  const server=createLocalShellServer({dist:process.env.KDG_LOCAL_SHELL_DIST,configFile:process.env.KDG_LOCAL_WEB_CONFIG});
  server.once('error',()=>{console.error('kdg_local_shell_start_failed');process.exitCode=1;});
  server.listen(Number(raw),'127.0.0.1',()=>console.log(JSON.stringify({kind:'kdg_local_shell_ready',origin:'http://127.0.0.1:'+server.address().port})));
  let stopping=false;const stop=()=>{if(stopping)return;stopping=true;server.close();const deadline=setTimeout(()=>{server.closeAllConnections();process.exitCode=1;},13000);deadline.unref();server.once('close',()=>clearTimeout(deadline));};process.once('SIGTERM',stop);process.once('SIGINT',stop);
 }catch{console.error('kdg_local_shell_configuration_invalid');process.exitCode=1;}
}
