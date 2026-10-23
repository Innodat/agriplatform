// Narrow build-time local-host adoption in its own managed root; no Auth inventory change.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkScaffold,installScaffold} from './scaffold-install.ts';
const names=['local-entry-host.mjs','test-local-entry-host.mjs'];
const hash=(v:string)=>createHash('sha256').update(v).digest('hex');
export function localHostFiles(){return Object.fromEntries(names.map(name=>[name,{classification:'generated' as const,content:readFileSync(new URL('../templates/application/web/local-host-tools/'+name,import.meta.url),'utf8')}]))}
export function syncKdgLocalHost(root:string,check=false){
 const output=join(root,'apps/kdg-capture/web/local-host-tools'),files=localHostFiles();
 if(!check)installScaffold(output,files,{generator:'builder-v1',template:'local-entry-host-v1-candidate',recipe:hash('kdg_capture-local-entry-host-v1'),source:hash(JSON.stringify(files))});
 checkScaffold(output);const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
 if(Object.keys(manifest.files).sort().join(',')!==names.slice().sort().join(',')||manifest.identity.generator!=='builder-v1'||manifest.identity.template!=='local-entry-host-v1-candidate'||manifest.identity.recipe!==hash('kdg_capture-local-entry-host-v1')||manifest.identity.source!==hash(JSON.stringify(files))||Object.values(manifest.files).some(file=>(file as {classification:string}).classification!=='generated'))throw Error('local_host_pattern_invalid');
 for(const [name,file]of Object.entries(files))if(readFileSync(join(output,name),'utf8')!==file.content)throw Error('local_host_pattern_drift');
}
