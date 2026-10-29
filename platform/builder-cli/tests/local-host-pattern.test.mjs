import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {renderApplication} from '../src/application-renderer.ts';
import {installScaffold} from '../src/scaffold-install.ts';
import {createHash} from 'node:crypto';
import {syncKdgLocalHost,localHostFiles} from '../src/kdg-local-host-pattern.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
test('managed local host and behavioral tests match canonical code and reject hand edits',()=>{
 syncKdgLocalHost(root,true);
 for(const target of Object.keys(localHostFiles())){
  const parent=join(root,'platform/deployment/.local/local-host-pattern');mkdirSync(parent,{recursive:true});const dir=mkdtempSync(join(parent,'proof-'));syncKdgLocalHost(dir);syncKdgLocalHost(dir,true);
  const web=join(dir,'apps/kdg-capture/web/local-host-tools');writeFileSync(join(web,'owner.txt'),'owner custom');writeFileSync(join(web,target),'manual');assert.throws(()=>syncKdgLocalHost(dir),/scaffold_conflict/);assert.equal(readFileSync(join(web,'owner.txt'),'utf8'),'owner custom');assert.equal(readFileSync(join(web,target),'utf8'),'manual');
 }
});
test('fresh rendered and installed local host tools pass emitted behavioral tests',()=>{
 const parent=join(root,'platform/deployment/.local/local-host-pattern');mkdirSync(parent,{recursive:true});const dir=mkdtempSync(join(parent,'proof-'));
 const recipe={schema_version:1,owner_id:'local_host_sample',owner_kind:'application',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'apps/local-host-sample/deployment/manifest.json'};
 const files=renderApplication(recipe,root),hash=v=>createHash('sha256').update(v).digest('hex');installScaffold(dir,files,{generator:'builder-v1',template:'application-v1-candidate',recipe:hash(JSON.stringify(recipe)),source:hash(JSON.stringify(files))});
 // A nested Node26 runner must not inherit its parent's child-runner protocol.
 const {NODE_TEST_CONTEXT:parentRunner,...childEnv}=process.env;
 const run=spawnSync(process.execPath,['--test','--test-reporter=spec',join(dir,'web/local-host-tools/test-local-entry-host.mjs')],{env:childEnv,encoding:'utf8',timeout:30000});assert.equal(run.status,0,run.stdout+run.stderr);assert.match(run.stdout,/explicit write routes accept bounded streamed JSON/);assert.match(run.stdout,/tests 10/);
});
