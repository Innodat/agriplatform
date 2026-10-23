import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdirSync,mkdtempSync,readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {renderApplication} from '../src/application-renderer.ts';
import {installScaffold} from '../src/scaffold-install.ts';
import {writeFiles,syncKdgWrite} from '../src/kdg-write-pattern.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
test('rendered application supplies bounded context and executable behavioral tests',()=>{
 const recipe={schema_version:1,owner_id:'write_sample',owner_kind:'application',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'apps/write-sample/deployment/manifest.json'};
 const files=renderApplication(recipe,root);
 assert.ok(files['write-tools/transaction_context.py'],'application must emit bounded transaction context');
 assert.ok(files['write-tools/test_transaction_context.py'],'application must emit its behavioral tests');
 assert.match(files['write-tools/transaction_context.py'].content,/def outcome_lock\(/,'application must emit scoped transaction operation locking');
 const parent=join(root,'platform/deployment/.local/write-context');mkdirSync(parent,{recursive:true});
 const output=mkdtempSync(join(parent,'proof-')),hash=value=>createHash('sha256').update(value).digest('hex');
 installScaffold(output,files,{generator:'builder-v1',template:'application-v1-candidate',recipe:hash(JSON.stringify(recipe)),source:hash(JSON.stringify(files))});
 const python=process.env.SCAFFOLD_WRITE_TEST_PYTHON||join(root,'platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python');
 const run=spawnSync(python,['-I','-B',join(output,'write-tools/test_transaction_context.py')],{encoding:'utf8',timeout:15000});
 assert.equal(run.status,0,run.stdout+run.stderr);assert.match(run.stderr,/OK/);
});
test('KDG code and emitted tests stay synchronized and protect owner/manual edits',()=>{
 syncKdgWrite(root,true);
 const parent=join(root,'platform/deployment/.local/write-context');mkdirSync(parent,{recursive:true});
 for(const name of Object.keys(writeFiles())){
  const dir=mkdtempSync(join(parent,'parity-'));syncKdgWrite(dir);
  const output=join(dir,'apps/kdg-capture/write-tools');
  writeFileSync(join(output,'owner.txt'),'owner');syncKdgWrite(dir);
  assert.equal(readFileSync(join(output,'owner.txt'),'utf8'),'owner');
  writeFileSync(join(output,name),'manual');
  assert.throws(()=>syncKdgWrite(dir),/scaffold_conflict/);
  assert.equal(readFileSync(join(output,name),'utf8'),'manual');
 }
});
