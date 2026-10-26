// Build-time adoption of thin primitives only; no application cache/schema engine.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkScaffold,installScaffold} from './scaffold-install.ts';
const names=['idb.ts','idb.test.mjs'];
const hash=(value:string)=>createHash('sha256').update(value).digest('hex');
export function offlineFiles(){return Object.fromEntries(names.map(name=>[name,{classification:'generated' as const,content:readFileSync(new URL('../templates/application/web/offline-tools/'+name,import.meta.url),'utf8')}]))}
export function syncKdgOffline(root:string,check=false){
 const output=join(root,'apps/kdg-capture/web/offline-tools'),files=offlineFiles();
 const identity={generator:'builder-v1',template:'indexeddb-primitives-v1-candidate',recipe:hash('kdg_capture-indexeddb-primitives-v1'),source:hash(JSON.stringify(files))};
 if(!check)installScaffold(output,files,identity);
 checkScaffold(output);const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
 if(Object.keys(manifest.files).sort().join(',')!==names.slice().sort().join(',')||Object.entries(identity).some(([key,value])=>manifest.identity[key]!==value)||Object.values(manifest.files).some(file=>(file as {classification:string}).classification!=='generated'))throw Error('offline_pattern_invalid');
 for(const [name,file]of Object.entries(files))if(readFileSync(join(output,name),'utf8')!==file.content)throw Error('offline_pattern_drift');
}
