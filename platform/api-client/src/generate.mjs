// Build-time only. Owner OpenAPI is authority; no shared runtime SDK.
import {createHash} from 'node:crypto';
import {existsSync,lstatSync,mkdtempSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,isAbsolute,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {qualifyTool} from './tooling.mjs';
import {spawnSync} from 'node:child_process';
import {checkScaffold,installScaffold} from '../../builder-cli/src/scaffold-install.ts';
const hash=value=>createHash('sha256').update(value).digest('hex');
const fail=code=>{throw new Error(`api_client_${code}`);};
function safePath(path,kind) {
 let part=resolve(path);
 while(true){try{const stat=lstatSync(part);if(stat.isSymbolicLink()||(part===resolve(path)&&!(kind==='file'?stat.isFile():stat.isDirectory())))fail('input_invalid');}catch(e){if(e.code!=='ENOENT')throw e;}
 const next=dirname(part);if(next===part)break;part=next;}
}
function loadSchema(path){
 safePath(path,'file');let value;
 try {if(lstatSync(path).size>8*1024*1024)fail('schema_invalid');value=JSON.parse(readFileSync(path,'utf8'));}catch{fail('schema_invalid');}
 if(!value||!/^3\.[01]\.\d+$/.test(value.openapi)||!value.info||typeof value.info.title!=='string'||typeof value.info.version!=='string'||!value.paths||Array.isArray(value.paths)||typeof value.paths!=='object')fail('schema_invalid');
 function visit(node,depth=0){if(depth>100)fail('schema_invalid');if(!node||typeof node!=='object')return;
 for(const [key,child] of Object.entries(node)){if((key==='$ref'||key==='$dynamicRef')&&(typeof child!=='string'||!child.startsWith('#/')))fail('schema_invalid');visit(child,depth+1);}}
 visit(value);return value;
}
export function generateClient({schema,output,check=false}){
 let temporary;
 try{
 if(typeof schema!=='string'||typeof output!=='string'||typeof check!=='boolean'||!schema||!output||/^[a-z]+:\/\//i.test(schema))fail('input_invalid');
 const input=resolve(schema),target=resolve(output);safePath(target,'directory');
 if(input===target||input.startsWith(target+'/')||target===dirname(input))fail('input_invalid');
 const document=loadSchema(input),source=hash(JSON.stringify(document));
 if(existsSync(target))checkScaffold(target);else if(check)fail('stale');
 const executable=qualifyTool().cli;temporary=mkdtempSync(join(tmpdir(),'platform-api-client-'));
 const exported=join(temporary,'openapi.json'),generated=join(temporary,'output');writeFileSync(exported,JSON.stringify(document));
 // Explicit config disables discovery. Only the upstream types plugin runs; no SDK/client runtime.
 const config=join(temporary,'openapi-ts.config.mjs');writeFileSync(config,`export default {input:${JSON.stringify(exported)},output:${JSON.stringify(generated)},plugins:['@hey-api/typescript']};\n`);
 const result=spawnSync(process.execPath,['--import',fileURLToPath(new URL('./compat.mjs',import.meta.url)),executable,'--file',config,'--silent','--no-log-file'],{cwd:temporary,encoding:'utf8',timeout:60000,maxBuffer:1024*1024,env:{PATH:dirname(process.execPath),HOME:temporary,NO_COLOR:'1'}});
 if(result.error||result.status!==0)fail('generation_failed');
 const names=readdirSync(generated).sort();if(names.join(',')!=='index.ts,types.gen.ts')fail('output_invalid');
 const files=Object.fromEntries(names.map(name=>{safePath(join(generated,name),'file');return [name,{classification:'generated',content:readFileSync(join(generated,name),'utf8')}];}));
 const identity={generator:'platform-api-client',template:'hey-api-0.99.0-types-v1',recipe:hash('app-owned-openapi-types-v1'),source};
 if(check){const manifest=JSON.parse(readFileSync(join(target,'.generated-files.json'),'utf8'));
 if(JSON.stringify(manifest.identity)!==JSON.stringify(identity)||Object.keys(manifest.files).sort().join(',')!==names.join(',')||names.some(name=>readFileSync(join(target,name),'utf8')!==files[name].content))fail('stale');
 }else installScaffold(target,files,identity);
 return {source,files:Object.fromEntries(names.map(name=>[name,hash(files[name].content)]))};
 }catch(error){if(error instanceof Error&&/^(api_client|scaffold)_[a-z_]+$/.test(error.message))throw error;fail('io_failed');}
 finally{if(temporary)rmSync(temporary,{recursive:true,force:true});}
}
