/** Explicit disposable build only; no installed deployment or device claim. */
import {readFileSync,statSync,realpathSync} from 'node:fs';
import {isAbsolute,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {parseKdgLocalPublicConfig} from './src/local-public-config.ts';
import {ownShellBuild} from './scripts/own-shell-build.mjs';
const web=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig(()=>{
 try{
  const path=process.env.KDG_LOCAL_WEB_CONFIG;if(!path||!isAbsolute(path))throw Error();
  const actual=realpathSync(path),stat=statSync(actual);
  if([resolve(path),actual].some(value=>value.startsWith(resolve(web,'..')+sep)||value.split(sep).includes('node_modules'))||!stat.isFile()||stat.size>8192)throw Error();
  const raw=readFileSync(actual,'utf8');if(Buffer.byteLength(raw)>8192)throw Error();
  const input=JSON.parse(raw);if(!input||typeof input!=='object'||Array.isArray(input)||Object.keys(input).length!==6||!Object.hasOwn(input,'api_origin'))throw Error();
  const {api_origin,...config}=input,target=new URL(api_origin);
  if(target.origin!==api_origin||target.protocol!=='http:'||target.hostname!=='127.0.0.1'||!target.port||Number(target.port)===0||!parseKdgLocalPublicConfig(config,'http://127.0.0.1:5177'))throw Error();
  const json=JSON.stringify(config).replaceAll('<','\\u003c').replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029');
  return {root:web,envDir:false,envPrefix:[],publicDir:false,tsconfig:resolve(web,'tsconfig.auth.json'),plugins:[react(),{name:'kdg-explicit-public-build-config',transformIndexHtml(html){const pattern=/<script id="kdg-local-config" type="application\/json">[\s\S]*?<\/script>/g;if([...html.matchAll(pattern)].length!==1)throw Error('kdg_shell_configuration_invalid');return html.replace(pattern,()=>'<script id="kdg-local-config" type="application/json">'+json+'</script>');}},ownShellBuild()],build:{emptyOutDir:false}};
 }catch{throw Error('kdg_shell_configuration_invalid');}
});
