import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
const script=fileURLToPath(new URL('../scripts/test-generation-application.mjs',import.meta.url));
const parent=fileURLToPath(new URL('../../deployment/.local/scaffold-application',import.meta.url));
const names=()=>existsSync(parent)?readdirSync(parent).sort():[];
const run=(env={},args=[])=>spawnSync(process.execPath,[script,...args],{env:{PATH:'/usr/bin:/bin',...env},encoding:'utf8'});
test('application bootstrap rejects missing paths and supplied output without writing',()=>{
 const before=names();
 for(const [env,args,error] of [[{},[],'configured_tool_invalid'],[{SCAFFOLD_NPM:'npm'},[],'configured_tool_invalid'],[{},['--output','SECRET'],'arguments_invalid']]) {
  const result=run(env,args);assert.equal(result.status,1);assert.equal(result.stderr,'');
  assert.deepEqual(JSON.parse(result.stdout),{error,bootstrap_only:true,generation_ready:false});
 }
 assert.deepEqual(names(),before);
});
function tools({npm='12.2.0',python='3.15.0',uv='uv 0.13.1',browser='Chromium 156.0.8078.4'}={}) {
 const directory=mkdtempSync('/tmp/scaffold-application-guard-');
 const paths={};
 for(const [name,version] of Object.entries({npm,python,uv,browser})) {
  const path=join(directory,`${name}.mjs`);paths[name]=path;
  const output=name==='python'?JSON.stringify({version,implementation:'CPython',free_threaded:false,executable:path}):version;
  writeFileSync(path,`#!${process.execPath}\nif(process.argv.includes('--version')||process.argv.includes('-c')) console.log(${JSON.stringify(output)}); else process.exit(42);\n`,{mode:0o700});
 }
 return {SCAFFOLD_NPM:paths.npm,SCAFFOLD_UV:paths.uv,SCAFFOLD_PYTHON:paths.python,SCAFFOLD_CHROMIUM:paths.browser,SCAFFOLD_NPM_CACHE:directory,UV_CACHE_DIR:directory};
}
test('application bootstrap refuses wrong versions and missing caches before output',()=>{
 const before=names();
 for(const options of [{npm:'12.1.0'},{python:'3.14.0'},{uv:'uv 0.13.0'},{browser:'unknown'}]) {
  const result=run(tools(options));assert.equal(result.status,1);assert.equal(JSON.parse(result.stdout).error,'configured_tool_version_invalid');assert.equal(result.stderr,'');
 }
 const env=tools();delete env.SCAFFOLD_NPM_CACHE;
 assert.equal(JSON.parse(run(env).stdout).error,'configured_cache_invalid');
 assert.deepEqual(names(),before);
});
test('application bootstrap retains fresh failed output and canonical lock provenance',()=>{
 const before=names();const result=run(tools());assert.equal(result.status,1);assert.equal(result.stderr,'');
 const output=JSON.parse(result.stdout);assert.equal(output.error,'bootstrap_stage_failed');
 assert.equal(names().length,before.length+1);
 for(const name of before) assert.ok(names().includes(name));
 const manifest=JSON.parse(readFileSync(join(output.proof,'proof.json')));
 assert.equal(manifest.status,'failed');assert.equal(manifest.bootstrap_only,true);assert.equal(manifest.generation_ready,false);
 assert.equal(manifest.commands.at(-1).label,'npm-lock');assert.equal(manifest.commands.at(-1).exit_code,42);
 assert.ok(manifest.root_lock.base_sha256);assert.ok(existsSync(join(output.proof,'root/apps/bootstrap-application/web/src/App.tsx')));
 assert.equal(existsSync(join(output.proof,'root/apps/bootstrap-application/web/package-lock.json')),false);
});
