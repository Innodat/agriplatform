// Private disposable-proof check; never resolves dependencies for normal generation.
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
const fail=()=>{throw new Error('dependency_provenance_invalid');};
export function qualifyWebDependencies(web, installationRoot) {
 const root=realpathSync(installationRoot);
 function artifact(path) {
  const actual=realpathSync(path),inside=relative(root,actual);
  if(!inside||inside==='..'||inside.startsWith('../')||isAbsolute(inside)) fail();
  return {path:actual,sha256:createHash('sha256').update(readFileSync(actual)).digest('hex')};
 }
 const manifest=JSON.parse(readFileSync(join(web,'package.json')));
 const require=createRequire(join(web,'package.json'));
 const result={packages:{},commands:{}};
 try {
  for(const [name,pin] of Object.entries({...manifest.dependencies,...manifest.devDependencies})) {
   if(!/^\d+\.\d+\.\d+$/.test(pin)) fail();
   // The selected plugin-react package exposes its dist entry, but not package.json.
   const metadata=artifact(name==='@vitejs/plugin-react'
    ? join(dirname(require.resolve(name)),'../package.json')
    : require.resolve(`${name}/package.json`));
   const pkg=JSON.parse(readFileSync(metadata.path));
   if(pkg.name!==name||pkg.version!==pin) fail();
   result.packages[name]={version:pkg.version,metadata};
  }
  for(const [command,name] of [['tsc','typescript'],['vite','vite'],['playwright','@playwright/test'],... (manifest.devDependencies?.['@platform/api-client'] ? [['platform-api-client','@platform/api-client']] : [])]) {
   const metadata=result.packages[name]?.metadata;if(!metadata) fail();
   const pkg=JSON.parse(readFileSync(metadata.path));
   const declared=typeof pkg.bin==='string'?pkg.bin:pkg.bin?.[command];if(!declared) fail();
   const executable=artifact(resolve(dirname(metadata.path),declared));
   let current=resolve(web),bin;
   while(true) {
    const candidate=join(current,'node_modules','.bin',command);
    if(existsSync(candidate)) {bin=artifact(candidate);break;}
    if(current===root) break;
    const next=dirname(current);if(next===current) fail();current=next;
   }
   if(!bin||bin.path!==executable.path) fail();
   result.commands[command]={package:name,...executable};
  }
  if(manifest.devDependencies?.['@platform/api-client']) {
   const owner=result.packages['@platform/api-client'].metadata.path,toolRequire=createRequire(owner);
   for(const [key,name,expectedName,version] of [['codegen','@hey-api/openapi-ts','@hey-api/openapi-ts','0.99.0'],['compatibilityCompiler','typescript','typescript','6.0.3']]) {
    const metadata=artifact(toolRequire.resolve(`${name}/package.json`)),pkg=JSON.parse(readFileSync(metadata.path));
    if(pkg.name!==expectedName||pkg.version!==version) fail();
    const payload=artifact(key==='codegen'?join(dirname(metadata.path),'dist/run.mjs'):toolRequire.resolve(name));
    result[key]={name:pkg.name,version,metadata,payload};
   }
  }
 } catch {fail();}
 return result;
}

export function recordInstallationManifests(root, paths) {
 return Object.fromEntries(paths.map(path=>[path,{sha256:createHash('sha256').update(readFileSync(join(root,path))).digest('hex')} ]));
}
export function verifyInstallationManifests(root, records) {
 for(const [path,record] of Object.entries(records)) {
  if(createHash('sha256').update(readFileSync(join(root,path))).digest('hex')!==record.sha256) throw new Error('installation_manifest_drift');
 }
}
