import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {databaseFiles,syncKdgDatabase} from '../src/kdg-database-pattern.ts';
import {renderApplication} from '../src/application-renderer.ts';
import {installScaffold} from '../src/scaffold-install.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
function fixture(){const parent=join(root,'platform/deployment/.local/schema-pattern');mkdirSync(parent,{recursive:true});return mkdtempSync(join(parent,'proof-'));}
test('KDG schema candidate code and tests match their canonical source and refuse manual edits',()=>{
 syncKdgDatabase(root,true);
 for(const name of Object.keys(databaseFiles())){
  const dir=fixture();syncKdgDatabase(dir);const output=join(dir,'apps/kdg-capture/database-tools');writeFileSync(join(output,'owner.txt'),'owner');writeFileSync(join(output,name),'manual');assert.throws(()=>syncKdgDatabase(dir),/scaffold_conflict/);assert.equal(readFileSync(join(output,name),'utf8'),'manual');assert.equal(readFileSync(join(output,'owner.txt'),'utf8'),'owner');
 }
});
test('actual rendered/installed app emits neutral schema-boundary unit tests with no database activation',()=>{
 const recipe={schema_version:1,owner_id:'schema_sample',owner_kind:'application',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'apps/schema-sample/deployment/manifest.json'};
 const files=renderApplication(recipe,root),hash=v=>createHash('sha256').update(v).digest('hex'),dir=fixture();installScaffold(dir,files,{generator:'builder-v1',template:'application-v1-candidate',recipe:hash(JSON.stringify(recipe)),source:hash(JSON.stringify(files))});
 const python=join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');const run=spawnSync(python,['-I','-B',join(dir,'database-tools/test_owned_migration.py')],{encoding:'utf8',timeout:15000});assert.equal(run.status,0,run.stdout+run.stderr);assert.match(run.stderr,/Ran 10 tests/);
});
