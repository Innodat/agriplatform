import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {syncKdgOffline,offlineFiles} from '../src/kdg-offline-pattern.ts';
import {checkScaffold,installScaffold} from '../src/scaffold-install.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
test('KDG primitive and generated behavior tests match canonical templates',()=>{
 syncKdgOffline(root,true);
 for(const [name,file] of Object.entries(offlineFiles())){
  assert.equal(file.classification,'generated');assert.match(file.content,/GENERATED/);assert.doesNotMatch(file.content,/Khula|kdg_capture|read\.own/);
 }
});
test('managed primitive/tests refuse manual edits and preserve owner code',()=>{
 for(const name of ['idb.ts','idb.test.mjs']){
  const fixture=mkdtempSync(join(tmpdir(),'kdg-offline-owner-')),output=join(fixture,'apps/kdg-capture/web/offline-tools');
  syncKdgOffline(fixture);writeFileSync(join(output,'owner.txt'),'application-owned');writeFileSync(join(output,name),'manual');
  assert.throws(()=>syncKdgOffline(fixture,true),/scaffold_conflict/);assert.throws(()=>syncKdgOffline(fixture),/scaffold_conflict/);
  assert.equal(readFileSync(join(output,name),'utf8'),'manual');assert.equal(readFileSync(join(output,'owner.txt'),'utf8'),'application-owned');
 }
});
test('canonical primitive drift fails even if installed manifest is consistent',()=>{
 const fixture=mkdtempSync(join(tmpdir(),'kdg-offline-drift-')),output=join(fixture,'apps/kdg-capture/web/offline-tools');syncKdgOffline(fixture);
 const files=offlineFiles();files['idb.ts'].content+='\n// previous revision\n';const identity=JSON.parse(readFileSync(join(output,'.generated-files.json'))).identity;
 installScaffold(output,files,identity);checkScaffold(output);assert.throws(()=>syncKdgOffline(fixture,true),/offline_pattern_drift|offline_pattern_invalid/);
 syncKdgOffline(fixture);syncKdgOffline(fixture,true);
});
