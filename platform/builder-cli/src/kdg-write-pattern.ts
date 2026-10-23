// Build-time code/test synchronization only; no database or authorization activation.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkScaffold,installScaffold} from './scaffold-install.ts';
const names=['transaction_context.py','test_transaction_context.py'];
const hash=(value:string)=>createHash('sha256').update(value).digest('hex');
export function writeFiles(){return Object.fromEntries(names.map(name=>[name,{classification:'generated' as const,content:readFileSync(new URL('../templates/application/write-tools/'+name,import.meta.url),'utf8')}]))}
export function syncKdgWrite(root:string,check=false){
 const output=join(root,'apps/kdg-capture/write-tools'),files=writeFiles();
 const identity={generator:'builder-v1',template:'write-context-v1-candidate',recipe:hash('kdg_capture-write-context-v1'),source:hash(JSON.stringify(files))};
 if(!check)installScaffold(output,files,identity);
 checkScaffold(output);const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
 if(Object.keys(manifest.files).sort().join(',')!==names.slice().sort().join(',')||Object.entries(identity).some(([key,value])=>manifest.identity[key]!==value)||Object.values(manifest.files).some(file=>(file as {classification:string}).classification!=='generated'))throw Error('write_pattern_invalid');
 for(const [name,file]of Object.entries(files))if(readFileSync(join(output,name),'utf8')!==file.content)throw Error('write_pattern_drift');
}
