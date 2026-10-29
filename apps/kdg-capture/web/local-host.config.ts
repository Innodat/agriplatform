/** Opt-in disposable development host; never a release or provider setup command. */
import {readFileSync,statSync,realpathSync} from 'node:fs';
import {isAbsolute,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {parseKdgLocalPublicConfig} from './src/local-public-config';
import {createLocalEntryHost} from './local-host-tools/local-entry-host.mjs';
import {kdgLocalApiRoutes} from './local-api-routes.mjs';
const web=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig(()=>{
 try{
  const path=process.env.KDG_LOCAL_WEB_CONFIG;
  // Explicit file outside the application and served dependency roots; never search .env.
  if(!path||!isAbsolute(path))throw Error();
  const actual=realpathSync(path),stat=statSync(actual);
  if([resolve(path),actual].some(value=>value.startsWith(resolve(web,'..')+sep)||value.split(sep).includes('node_modules'))||!stat.isFile()||stat.size>8192)throw Error();
  const raw=readFileSync(path,'utf8');if(Buffer.byteLength(raw)>8192)throw Error();
  const input=JSON.parse(raw);if(!input||typeof input!=='object'||Array.isArray(input)||Object.keys(input).length!==6||!Object.hasOwn(input,'api_origin'))throw Error();
  const {api_origin,...publicConfig}=input;
  if(!parseKdgLocalPublicConfig(publicConfig,'http://127.0.0.1:5177'))throw Error();
  const host=createLocalEntryHost({scriptId:'kdg-local-config',publicConfig,apiOrigin:api_origin,routes:kdgLocalApiRoutes});
  return {...host,root:web,tsconfig:resolve(web,'tsconfig.auth.json'),plugins:[react(),...host.plugins,{name:'local-listen-notice',configureServer(server){server.httpServer?.once('listening',()=>{const address=server.httpServer?.address();if(address&&typeof address==='object')console.log('KDG local web: http://127.0.0.1:'+address.port);});}}],server:{...host.server,port:5177,fs:{strict:true,allow:[web,resolve(web,'../contracts')],deny:['.env','.env.*','**/.git/**','**/tests/**','**/local-host.config.ts']}}};
 }catch{throw Error('kdg_local_host_configuration_invalid');}
});
