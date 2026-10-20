import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { syncBuiltinESMExports } from 'node:module';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { installScaffold, checkScaffold, recoverScaffold } from '../src/scaffold-install.ts';
const identity = {generator:'builder-v1',template:'application-v1-candidate',recipe:'a'.repeat(64),source:'b'.repeat(64)};
const files = {'base.txt':{classification:'generated',content:'generated'},'seed.txt':{classification:'seed',content:'seed'}};
function fixture(t) {
  const repo=fs.mkdtempSync(join(tmpdir(),'extensions-'));
  t.after(()=>fs.rmSync(repo,{recursive:true,force:true}));
  fs.mkdirSync(join(repo,'source')); fs.writeFileSync(join(repo,'source/module.ts'),'export const text = "initial";\n');
  return {repo,root:join(repo,'output'),input:{repositoryRoot:repo,declarations:[{source:'source',destination:'web/custom'}]}};
}
const install=(f,fault)=>installScaffold(f.root,files,identity,fault,f.input);
const read=(f,path)=>fs.readFileSync(join(f.root,path),'utf8');
test('explicit import copies exact bytes with separate versioned provenance and preserves owner maintenance without source reads',t=>{
 const f=fixture(t); install(f);
 assert.equal(read(f,'web/custom/module.ts'),'export const text = "initial";\n');
 const manifest=JSON.parse(read(f,'.generated-files.json'));
 assert.equal(manifest.extensions.schema_version,1);
 assert.equal(manifest.extensions.imports[0].source,'source');
 assert.equal(manifest.extensions.imports[0].destination,'web/custom');
 assert.match(manifest.extensions.imports[0].files['module.ts'],/^[a-f0-9]{64}$/);
 assert.equal(manifest.files['web/custom/module.ts'],undefined);
 fs.writeFileSync(join(f.root,'web/custom/module.ts'),'owner');
 fs.writeFileSync(join(f.root,'web/custom/added.ts'),'added');
 fs.rmSync(join(f.repo,'source'),{recursive:true});
 install(f); checkScaffold(f.root);
 assert.equal(read(f,'web/custom/module.ts'),'owner');
 assert.equal(read(f,'web/custom/added.ts'),'added');
 fs.rmSync(join(f.root,'web/custom/module.ts')); install(f); checkScaffold(f.root);
 assert.equal(fs.existsSync(join(f.root,'web/custom/module.ts')),false);
});
test('unsafe sources and declarations refuse the complete plan before output bytes',t=>{
 const cases = [
  f=>fs.symlinkSync('missing',join(f.repo,'source/dangling')),
  f=>fs.symlinkSync(join(f.repo,'source/module.ts'),join(f.repo,'source/link')),
  f=>{fs.mkdirSync(join(f.repo,'outside'));fs.symlinkSync(join(f.repo,'outside'),join(f.repo,'source/linked'));},
  f=>fs.writeFileSync(join(f.repo,'source/binary'),Buffer.from([0xff,0])),
  f=>fs.writeFileSync(join(f.repo,'source/nul'),'a\0b'),
  f=>fs.writeFileSync(join(f.repo,'source/huge'),'a'.repeat(1024*1024+1)),
  f=>{let path=join(f.repo,'source');for(let i=0;i<17;i++){path=join(path,'nested');fs.mkdirSync(path)}},
  f=>{for(let i=0;i<1001;i++)fs.writeFileSync(join(f.repo,'source',String(i)),'x')},
  f=>{for(let i=0;i<9;i++)fs.writeFileSync(join(f.repo,'source',String(i)),'a'.repeat(1024*1024))},
  f=>fs.mkdirSync(join(f.repo,'source/.git')),
  f=>fs.writeFileSync(join(f.repo,'source/.scaffold-install-state'),'metadata'),
  f=>fs.writeFileSync(join(f.repo,'source/back\\slash'),'bad'),
  f=>fs.writeFileSync(join(f.repo,'source/CON.txt'),'bad'),
  f=>{assert.equal(spawnSync('mkfifo',[join(f.repo,'source/fifo')]).status,0)},
  f=>{f.input.declarations[0].source='../escape'},
  f=>{f.input.declarations.push({source:'source',destination:'other'})},
  f=>{fs.mkdirSync(join(f.repo,'source/nested'));f.input.declarations.push({source:'source/nested',destination:'other'})},
  f=>{f.input.declarations[0].destination='../escape'},
  f=>{f.input.declarations[0].destination='.git/custom'},
  f=>{f.input.declarations[0].source='output';fs.mkdirSync(f.root)},
  f=>{f.input.declarations[0].source='source';f.root=join(f.repo,'source/output')},
 ];
 for(const mutate of cases){const f=fixture(t);mutate(f);assert.throws(()=>install(f),/^Error: scaffold_[a-z_]+$/);assert.equal(fs.existsSync(join(f.root,'base.txt')),false);assert.equal(fs.existsSync(join(f.root,'.generated-files.json')),false)}
});
test('all destination collisions and overlap are rejected before generated replacement',t=>{
 const cases=[
  f=>{fs.mkdirSync(join(f.root,'web/custom'),{recursive:true})},
  f=>{fs.mkdirSync(join(f.root,'web'),{recursive:true});fs.writeFileSync(join(f.root,'web/custom'),'owner')},
  f=>{fs.mkdirSync(join(f.root,'web/custom'),{recursive:true});fs.writeFileSync(join(f.root,'web/custom/owner'),'owner')},
  f=>{f.input.declarations[0].destination='base.txt/child'},
  f=>{f.input.declarations[0].destination='base.txt'},
  f=>{f.input.declarations[0].destination='seed.txt'},
  f=>{f.input.declarations.push({source:'source',destination:'web'})},
  f=>{f.input.declarations.push({source:'source',destination:'web/custom/nested'})},
  f=>{f.input.declarations.push({...f.input.declarations[0]})},
  f=>{fs.mkdirSync(f.root);fs.symlinkSync('missing',join(f.root,'web'))},
 ];
 for(const mutate of cases){const f=fixture(t);mutate(f);assert.throws(()=>install(f),/scaffold_/);assert.equal(fs.existsSync(join(f.root,'base.txt')),false);assert.equal(fs.existsSync(join(f.root,'.generated-files.json')),false)}
});
test('installed declarations and generated/custom ownership cannot change or be adopted',t=>{
 const f=fixture(t);install(f);const before=read(f,'.generated-files.json');
 for(const declarations of [[],[{source:'new-source',destination:'web/custom'}],[{source:'source',destination:'other'}]]){
  assert.throws(()=>installScaffold(f.root,files,identity,undefined,{repositoryRoot:f.repo,declarations}),/scaffold_ownership_invalid/);
  assert.equal(read(f,'.generated-files.json'),before);
 }
 assert.throws(()=>installScaffold(f.root,{...files,'web/custom/module.ts':{classification:'generated',content:'stolen'}},identity,undefined,f.input),/scaffold_ownership_invalid/);
 assert.throws(()=>installScaffold(f.root,files,{...identity,recipe:'c'.repeat(64)},undefined,f.input),/scaffold_identity_invalid/);
 const legacy=fixture(t);installScaffold(legacy.root,files,identity);installScaffold(legacy.root,files,identity);checkScaffold(legacy.root);
 assert.equal(JSON.parse(read(legacy,'.generated-files.json')).extensions,undefined);
 assert.throws(()=>install(legacy),/scaffold_ownership_invalid/);
});
test('strict explicit metadata version and ownership inventory validation',t=>{
 for(const mutate of [m=>m.extensions.schema_version=2,m=>delete m.extensions.schema_version,m=>m.extensions.extra=true,m=>m.extensions.imports[0].files['module.ts']='bad',m=>m.extensions.imports[0].destination='base.txt',m=>m.extensions.imports[0].files['../escape']='a'.repeat(64)]){
  const f=fixture(t);install(f);const m=JSON.parse(read(f,'.generated-files.json'));mutate(m);fs.writeFileSync(join(f.root,'.generated-files.json'),JSON.stringify(m));
  assert.throws(()=>checkScaffold(f.root),/scaffold_manifest_invalid/);
  assert.throws(()=>install(f),/scaffold_manifest_invalid/);
 }
});
const installerURL=new URL('../src/scaffold-install.ts',import.meta.url).href;
function killed(f,position){
 const child=spawnSync(process.execPath,['--input-type=module','-e',`import {installScaffold} from ${JSON.stringify(installerURL)};installScaffold(${JSON.stringify(f.root)},${JSON.stringify(files)},${JSON.stringify(identity)},{afterWrite(count){if(count===${position})process.kill(process.pid,'SIGKILL')}},${JSON.stringify(f.input)});`]);
 assert.equal(child.signal,'SIGKILL',child.stderr.toString());
}
test('caught failures and real SIGKILL restore complete pre-import bytes, including after manifest write',t=>{
 for(const mode of ['caught','killed'])for(const position of [3,4]){
  const f=fixture(t);fs.mkdirSync(f.root);fs.writeFileSync(join(f.root,'docs.md'),'owner docs');
  if(mode==='caught')assert.throws(()=>install(f,{afterWrite(count){if(count===position)throw Error('injected')}}),/scaffold_install_failed/);
  else{killed(f,position);assert.throws(()=>checkScaffold(f.root),/scaffold_recovery_required/);recoverScaffold(f.root)}
  assert.equal(read(f,'docs.md'),'owner docs');
  for(const path of ['base.txt','seed.txt','web/custom/module.ts','.generated-files.json','.scaffold-install-lock','.scaffold-install-state'])assert.equal(fs.existsSync(join(f.root,path)),false,path);
  install(f);checkScaffold(f.root);
 }
});
test('unknown imported edits after interruption refuse rollback without erasing any bytes',t=>{
 const f=fixture(t);killed(f,4);fs.writeFileSync(join(f.root,'web/custom/module.ts'),'owner after crash');
 assert.throws(()=>recoverScaffold(f.root),/scaffold_recovery_uncertain/);
 assert.equal(read(f,'web/custom/module.ts'),'owner after crash');assert.equal(read(f,'base.txt'),'generated');
});
test('replay never probes absent source and keeps exact installed provenance',t=>{
 const f=fixture(t);install(f);const manifest=read(f,'.generated-files.json');
 fs.rmSync(join(f.repo,'source'),{recursive:true});
 const methods=['readFileSync','readdirSync','lstatSync','existsSync'],originals=Object.fromEntries(methods.map(k=>[k,fs[k]]));
 for(const method of methods)fs[method]=function(path,...args){assert.equal(String(path).startsWith(join(f.repo,'source')),false,`source ${method}`);return originals[method].call(this,path,...args)};
 syncBuiltinESMExports();
 try{install(f);checkScaffold(f.root)}finally{for(const method of methods)fs[method]=originals[method];syncBuiltinESMExports()}
 assert.equal(read(f,'.generated-files.json'),manifest);
});
test('real ENOSPC during imported replacement rolls back known bytes and keeps documentation',t=>{
 const f=fixture(t);fs.mkdirSync(f.root);fs.writeFileSync(join(f.root,'docs.md'),'owner docs');
 const original=fs.writeFileSync;let triggered=false;
 fs.writeFileSync=function(path,data,...args){if(!triggered&&String(path).endsWith('/replacement')&&Buffer.from(data).toString()==='export const text = "initial";\n'){triggered=true;original.call(this,path,'partial',...args);return original.call(this,'/dev/full',data)}return original.call(this,path,data,...args)};
 syncBuiltinESMExports();try{assert.throws(()=>install(f),/scaffold_install_failed/)}finally{fs.writeFileSync=original;syncBuiltinESMExports()}
 assert.equal(triggered,true);assert.equal(read(f,'docs.md'),'owner docs');assert.equal(fs.existsSync(join(f.root,'base.txt')),false);assert.equal(fs.existsSync(join(f.root,'web/custom/module.ts')),false);
});
test('imports retain generated conflict, live writer exclusion and failed-rerun preservation',t=>{
 const f=fixture(t);install(f);fs.writeFileSync(join(f.root,'web/custom/module.ts'),'owner');
 assert.throws(()=>install(f,{afterWrite(){assert.throws(()=>install(f),/scaffold_busy/);assert.throws(()=>recoverScaffold(f.root),/scaffold_busy/);throw Error('injected')}}),/scaffold_install_failed/);
 assert.equal(read(f,'web/custom/module.ts'),'owner');checkScaffold(f.root);
 fs.writeFileSync(join(f.root,'base.txt'),'generated drift');
 assert.throws(()=>install(f),/scaffold_conflict/);assert.equal(read(f,'base.txt'),'generated drift');assert.equal(read(f,'web/custom/module.ts'),'owner');
});
test('equivalent declaration property order and two disjoint imports replay without sources',t=>{
 const f=fixture(t);fs.mkdirSync(join(f.repo,'second'));fs.writeFileSync(join(f.repo,'second/another.ts'),'export const another = 2;\n');
 f.input.declarations.push({source:'second',destination:'api/custom'});install(f);
 assert.equal(read(f,'web/custom/module.ts'),'export const text = "initial";\n');assert.equal(read(f,'api/custom/another.ts'),'export const another = 2;\n');
 const manifest=read(f,'.generated-files.json'),imports=JSON.parse(manifest).extensions.imports;
 assert.equal(imports.length,2);assert.equal(imports[1].source,'second');assert.equal(imports[1].destination,'api/custom');assert.match(imports[1].files['another.ts'],/^[a-f0-9]{64}$/);
 fs.rmSync(join(f.repo,'source'),{recursive:true});fs.rmSync(join(f.repo,'second'),{recursive:true});
 f.input.declarations=f.input.declarations.map(({source,destination})=>({destination,source}));install(f);checkScaffold(f.root);assert.equal(read(f,'.generated-files.json'),manifest);
});
function byteSnapshot(root){
 return Object.fromEntries(fs.readdirSync(root,{recursive:true}).filter(path=>fs.lstatSync(join(root,path)).isFile()).sort().map(path=>[path,fs.readFileSync(join(root,path)).toString('base64')]));
}
test('initial recovery refuses unknown import children and replaced empty import roots before all mutation',t=>{
 for(const mutation of ['owner-added','empty-file','empty-symlink']){
  const f=fixture(t);
  if(mutation!=='owner-added'){fs.mkdirSync(join(f.repo,'empty'));f.input.declarations.push({source:'empty',destination:'empty-root'})}
  killed(f,4);
  if(mutation==='owner-added')fs.writeFileSync(join(f.root,'web/custom/owner-added.ts'),'unknown owner bytes');
  else if(mutation==='empty-file')fs.writeFileSync(join(f.root,'empty-root'),'replacement root');
  else fs.symlinkSync('missing',join(f.root,'empty-root'));
  const before=byteSnapshot(f.root),manifest=read(f,'.generated-files.json');
  assert.throws(()=>recoverScaffold(f.root),/scaffold_recovery_uncertain/);
  const after=byteSnapshot(f.root);delete after['.scaffold-recovery-claim/owner.json'];assert.deepEqual(after,before);assert.equal(read(f,'.generated-files.json'),manifest);
  assert.equal(fs.existsSync(join(f.root,'.scaffold-install-state/journal.json')),true);assert.equal(fs.existsSync(join(f.root,'.scaffold-install-lock/owner.json')),true);
  if(mutation==='empty-symlink')assert.equal(fs.lstatSync(join(f.root,'empty-root')).isSymbolicLink(),true);
 }
});
test('exclusive initial publication preserves owner bytes appearing after complete preflight',t=>{
 const f=fixture(t),original=fs.writeFileSync;let injected=false;
 fs.writeFileSync=function(path,data,...args){const result=original.call(this,path,data,...args);if(!injected&&String(path).endsWith('/replacement')&&Buffer.from(data).toString()==='export const text = "initial";\n'){injected=true;original.call(this,join(f.root,'web/custom/module.ts'),'late owner bytes')}return result};
 syncBuiltinESMExports();try{assert.throws(()=>install(f),/scaffold_recovery_uncertain/)}finally{fs.writeFileSync=original;syncBuiltinESMExports()}
 assert.equal(injected,true);assert.equal(read(f,'web/custom/module.ts'),'late owner bytes');assert.equal(read(f,'base.txt'),'generated');assert.equal(fs.existsSync(join(f.root,'.scaffold-install-state/journal.json')),true);assert.equal(fs.existsSync(join(f.root,'.scaffold-install-lock/owner.json')),true);
});
test('source traversal stops at shared entry budget and reliably closes directory handles',t=>{
 const f=fixture(t);for(let i=0;i<1005;i++)fs.writeFileSync(join(f.repo,'source',`file-${i}`),'x');
 const originalOpen=fs.opendirSync,originalRead=fs.readdirSync;let entries=0,closed=false;
 fs.opendirSync=function(path,...args){const handle=originalOpen.call(this,path,...args);if(String(path)===join(f.repo,'source')){const read=handle.readSync.bind(handle),close=handle.closeSync.bind(handle);handle.readSync=function(){entries++;return read()};handle.closeSync=function(){closed=true;return close()}}return handle};
 fs.readdirSync=function(path,...args){assert.notEqual(String(path),join(f.repo,'source'),'source must not be materialized by readdirSync');return originalRead.call(this,path,...args)};
 syncBuiltinESMExports();try{assert.throws(()=>install(f),/scaffold_extension_limit/)}finally{fs.opendirSync=originalOpen;fs.readdirSync=originalRead;syncBuiltinESMExports()}
 assert.equal(entries,1001);assert.equal(closed,true);assert.equal(fs.existsSync(join(f.root,'base.txt')),false);
});
