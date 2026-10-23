// Build-time adoption only; candidate has no authority to connect or apply migrations.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkScaffold,installScaffold} from './scaffold-install.ts';
const names=['owned_migration.py','test_owned_migration.py'];
const hash=(v:string)=>createHash('sha256').update(v).digest('hex');
export function databaseFiles(){return Object.fromEntries(names.map(name=>[name,{classification:'generated' as const,content:readFileSync(new URL('../templates/application/database-tools/'+name,import.meta.url),'utf8')}]))}
export function syncKdgDatabase(root:string,check=false){
 const output=join(root,'apps/kdg-capture/database-tools'),files=databaseFiles();
 if(!check)installScaffold(output,files,{generator:'builder-v1',template:'schema-foundation-v1-candidate',recipe:hash('kdg_capture-schema-foundation-v1'),source:hash(JSON.stringify(files))});
 checkScaffold(output);const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
 if(Object.keys(manifest.files).sort().join(',')!==names.slice().sort().join(',')||manifest.identity.generator!=='builder-v1'||manifest.identity.template!=='schema-foundation-v1-candidate'||manifest.identity.recipe!==hash('kdg_capture-schema-foundation-v1')||manifest.identity.source!==hash(JSON.stringify(files))||Object.values(manifest.files).some(file=>(file as {classification:string}).classification!=='generated'))throw Error('database_pattern_invalid');
 for(const [name,file]of Object.entries(files))if(readFileSync(join(output,name),'utf8')!==file.content)throw Error('database_pattern_drift');
}
