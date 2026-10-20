import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, readFileSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { qualifyWebDependencies, recordInstallationManifests, verifyInstallationManifests } from '../scripts/application-dependency-proof.mjs';
function fixture() {
 const parent=mkdtempSync('/tmp/application-dependency-proof-'),root=join(parent,'proof'),web=join(root,'apps/example/web');
 mkdirSync(web,{recursive:true});mkdirSync(join(root,'node_modules/.bin'),{recursive:true});
 const dependencies={typescript:'7.0.2',vite:'8.3.4','@playwright/test':'1.64.0'};
 writeFileSync(join(web,'package.json'),JSON.stringify({dependencies}));
 function pkg(base,name,version,command) {
  const directory=join(base,'node_modules',name);mkdirSync(directory,{recursive:true});
  writeFileSync(join(directory,'package.json'),JSON.stringify({name,version,bin:{[command]:'cli.js'}}));
  writeFileSync(join(directory,'cli.js'),'// synthetic executable identity\n');return directory;
 }
 for(const [name,version] of Object.entries(dependencies)) {
  const command=name==='typescript'?'tsc':name==='vite'?'vite':'playwright';
  const directory=pkg(root,name,version,command);symlinkSync(join(directory,'cli.js'),join(root,'node_modules/.bin',command));
 }
 return {parent,root,web,pkg};
}
test('proof records exact local dependency metadata and tsc/Vite/Playwright executables',()=>{
 const {root,web}=fixture(),result=qualifyWebDependencies(web,root);
 assert.deepEqual(Object.keys(result.commands),['tsc','vite','playwright']);
 for(const identity of Object.values(result.packages)) {assert.ok(identity.metadata.path.startsWith(root+'/'));assert.match(identity.metadata.sha256,/^[a-f0-9]{64}$/);}
});
test('selected plugin-react metadata is bound to its exported dist entry',()=>{
 const {root,web}=fixture(),directory=join(root,'node_modules/@vitejs/plugin-react');
 mkdirSync(join(directory,'dist'),{recursive:true});
 writeFileSync(join(directory,'dist/index.js'),'// fixture');
 writeFileSync(join(directory,'package.json'),JSON.stringify({name:'@vitejs/plugin-react',version:'6.1.2',exports:{'.':'./dist/index.js'}}));
 const manifest=JSON.parse(readFileSync(join(web,'package.json')));manifest.dependencies['@vitejs/plugin-react']='6.1.2';
 writeFileSync(join(web,'package.json'),JSON.stringify(manifest));
 assert.equal(qualifyWebDependencies(web,root).packages['@vitejs/plugin-react'].version,'6.1.2');
});
test('proof refuses ancestor dependency fallback and wrong installed pins',()=>{
 const {parent,root,web,pkg}=fixture();
 pkg(parent,'ancestor-only','1.0.0','unused');
 writeFileSync(join(web,'package.json'),JSON.stringify({dependencies:{'ancestor-only':'1.0.0'}}));
 assert.throws(()=>qualifyWebDependencies(web,root),{message:'dependency_provenance_invalid'});
 const second=fixture();writeFileSync(join(second.root,'node_modules/vite/package.json'),JSON.stringify({name:'vite',version:'8.3.3',bin:{vite:'cli.js'}}));
 assert.throws(()=>qualifyWebDependencies(second.web,second.root),{message:'dependency_provenance_invalid'});
});

test('proof binds actual copied installation manifests and refuses subsequent drift',()=>{
 const {root,web}=fixture();
 const paths=['package.json','platform/copied/package.json'];
 mkdirSync(join(root,'platform/copied'),{recursive:true});
 for(const path of paths) writeFileSync(join(root,path),JSON.stringify({name:path,workspaces:['apps/example/web']}));
 const records=recordInstallationManifests(root,paths);
 assert.doesNotThrow(()=>verifyInstallationManifests(root,records));
 writeFileSync(join(root,paths[0]),JSON.stringify({name:'mutated-root'}));
 assert.throws(()=>verifyInstallationManifests(root,records),{message:'installation_manifest_drift'});
 const updated=recordInstallationManifests(root,paths);
 writeFileSync(join(root,paths[1]),JSON.stringify({name:'mutated-workspace'}));
 assert.throws(()=>verifyInstallationManifests(root,updated),{message:'installation_manifest_drift'});
});

test('proof refuses a collided ambient npm compiler instead of using TS6',()=>{
 const {root,web,pkg}=fixture();const other=pkg(root,'compiler-old','6.0.3','tsc');
 unlinkSync(join(root,'node_modules/.bin/tsc'));symlinkSync(join(other,'cli.js'),join(root,'node_modules/.bin/tsc'));
 assert.throws(()=>qualifyWebDependencies(web,root),{message:'dependency_provenance_invalid'});
});
