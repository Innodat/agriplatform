// App-owned installer; shared template sources remain managed by builder-cli.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {databaseFiles} from '../../../platform/builder-cli/src/kdg-database-pattern.ts';
import {checkScaffold,installScaffold} from '../../../platform/builder-cli/src/scaffold-install.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const output=join(root,'apps/scribeswell/studies-database-tools');
const files=databaseFiles();
const hash=v=>createHash('sha256').update(v).digest('hex');
const identity={generator:'builder-v1',template:'personal-notes-database-v1',recipe:hash('scribeswell-studies-v1'),source:hash(JSON.stringify(files))};
if(!process.argv.includes('--check'))installScaffold(output,files,identity);
checkScaffold(output);
const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
if(JSON.stringify(manifest.identity)!==JSON.stringify(identity))throw Error('studies_database_pattern_invalid');
for(const [name,file] of Object.entries(files))if(readFileSync(join(output,name),'utf8')!==file.content)throw Error('studies_database_pattern_drift');
