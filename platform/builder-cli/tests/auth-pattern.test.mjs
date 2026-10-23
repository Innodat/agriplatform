import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {renderAuthPattern} from '../src/auth-pattern.ts';
import {checkKdgAuthPattern,syncKdgAuthPattern,kdgAuthFiles} from '../src/kdg-auth-pattern.ts';
import {checkScaffold,installScaffold} from '../src/scaffold-install.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
function fixture(){const parent=join(root,'platform/deployment/.local/scaffold-auth-tests-20261023');mkdirSync(parent,{recursive:true,mode:0o700});const dir=mkdtempSync(join(parent,'proof-'));mkdirSync(join(dir,'apps/kdg-capture/web/src'),{recursive:true});return dir;}
test('current KDG generated Auth runtime, React hook and tests exactly match canonical templates',()=>{
 checkKdgAuthPattern(root);assert.equal(Object.keys(renderAuthPattern()).length,3);
 for(const [path,file] of Object.entries(renderAuthPattern())){assert.equal(file.classification,'generated');assert.match(file.content,/GENERATED/);assert.doesNotMatch(file.content,/kdg_capture|Khula|KDG Capture/);}
});
test('managed Auth refresh preserves owner code and refuses edited generated code or tests',()=>{
 for(const target of ['src/auth/lifecycle.ts','src/auth/use-lifecycle.ts','scripts/test-auth-lifecycle.mjs']){
  const dir=fixture(),web=join(dir,'apps/kdg-capture/web');writeFileSync(join(web,'src/owner.ts'),'owner custom');syncKdgAuthPattern(dir);checkKdgAuthPattern(dir);
  assert.equal(readFileSync(join(web,'src/owner.ts'),'utf8'),'owner custom');
  writeFileSync(join(web,target),'// manual edit');assert.throws(()=>checkKdgAuthPattern(dir),/scaffold_conflict/);assert.throws(()=>syncKdgAuthPattern(dir),/scaffold_conflict/);
  assert.equal(readFileSync(join(web,target),'utf8'),'// manual edit');assert.equal(readFileSync(join(web,'src/owner.ts'),'utf8'),'owner custom');
 }
});
test('installed-manifest success is insufficient: canonical drift fails and managed regeneration fixes it',()=>{
 const dir=fixture(),web=join(dir,'apps/kdg-capture/web');syncKdgAuthPattern(dir);
 const oldFiles=kdgAuthFiles();for(const path of ['scripts/test-auth-lifecycle.mjs','src/auth/use-lifecycle.ts'])oldFiles[path]={...oldFiles[path],content:oldFiles[path].content+'\n// previous generated revision\n'};
 const identity=JSON.parse(readFileSync(join(web,'.generated-files.json'))).identity;installScaffold(web,oldFiles,identity);checkScaffold(web);
 assert.throws(()=>checkKdgAuthPattern(dir),/kdg_auth_template_drift/);syncKdgAuthPattern(dir);checkKdgAuthPattern(dir);
});
test('legacy copied Auth refuses execution instead of silently supplying unsafe defaults',async()=>{
 const source=readFileSync(join(root,'platform/builder-cli/templates/web/src/context/AuthContext.tsx'),'utf8');
 const retired=await import('data:text/javascript,'+encodeURIComponent(source));
 assert.throws(()=>retired.AuthProvider(),{message:'legacy_auth_template_retired'});assert.throws(()=>retired.useAuth(),{message:'legacy_auth_template_retired'});
});

test('manifest integrity requires the exact pattern identity, generated classifications and inventory',()=>{
 for(const fault of ['identity','source','classification','inventory']){
  const dir=fixture(),web=join(dir,'apps/kdg-capture/web');syncKdgAuthPattern(dir);
  const path=join(web,'.generated-files.json'),manifest=JSON.parse(readFileSync(path));
  if(fault==='identity')manifest.identity.template='unrelated-pattern';
  if(fault==='source')manifest.identity.source='a'.repeat(64);
  if(fault==='classification')manifest.files['src/auth/lifecycle.ts'].classification='seed';
  if(fault==='inventory')delete manifest.files['scripts/test-auth-lifecycle.mjs'];
  writeFileSync(path,JSON.stringify(manifest));checkScaffold(web);
  assert.throws(()=>checkKdgAuthPattern(dir),/kdg_auth_manifest_invalid/);
 }
});

test('standalone generated proof refuses an unqualified Node before producing output',async()=>{
 const {spawnSync}=await import('node:child_process');const {readdirSync}=await import('node:fs');
 const dir=fixture(),inject=join(dir,'runtime.mjs');writeFileSync(inject,"Object.defineProperty(process,'version',{value:'v24.0.0'});\n");
 const parent=join(root,'platform/deployment/.local/scaffold-auth-lifecycle-20261023');mkdirSync(parent,{recursive:true});const before=readdirSync(parent).sort();
 const result=spawnSync(process.execPath,['--import',inject,join(root,'platform/builder-cli/scripts/prove-auth-lifecycle.mjs')],{cwd:root,encoding:'utf8',timeout:30000});
 assert.notEqual(result.status,0);assert.match(result.stderr,/unqualified_node_runtime/);assert.deepEqual(readdirSync(parent).sort(),before);
});
