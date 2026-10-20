import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
const proofParent=fileURLToPath(new URL('../../deployment/.local/scaffold-generation',import.meta.url));
const proofNames=()=>existsSync(proofParent)?readdirSync(proofParent).sort():[];
const script=fileURLToPath(new URL('../scripts/test-generation.mjs',import.meta.url));
function run(env,args=[]) {return spawnSync(process.execPath,[script,...args],{env:{PATH:'/usr/bin:/bin',...env},encoding:'utf8'});}
test('bootstrap refuses missing or relative tools and supplied output target safely',()=>{
 for(const env of [{},{SCAFFOLD_UV:'uv',SCAFFOLD_PYTHON:'/missing/SECRET_PAYLOAD'},{SCAFFOLD_UV:'/missing/SECRET_PAYLOAD'}]) {
  const result=run(env);assert.equal(result.status,1);assert.equal(result.stderr,'');
  assert.deepEqual(JSON.parse(result.stdout),{error:'configured_tool_invalid',bootstrap_only:true,generation_ready:false});
 }
 const result=run({},['--output','SECRET_PAYLOAD']); assert.equal(result.status,1);
 assert.equal(JSON.parse(result.stdout).error,'arguments_invalid');
 assert.equal(result.stdout.includes('SECRET_PAYLOAD'),false);
});

function fixtureTools(uvVersion='uv 0.13.1',pythonInfo={version:'3.15.0',implementation:'CPython',free_threaded:false},lockBody='process.exit(99);') {
 const directory=mkdtempSync('/tmp/scaffold-tool-guard-');
 const uv=join(directory,'uv.mjs'),python=join(directory,'python.mjs');
 const visits=join(directory,'uv-visits.log');
 writeFileSync(uv,`#!${process.execPath}
import {appendFileSync,chmodSync} from 'node:fs';
import {join} from 'node:path';
appendFileSync(${JSON.stringify(visits)},process.argv.slice(2).join(' ')+'\\n');
if(process.argv[2]==='--version') console.log(${JSON.stringify(uvVersion)}); else { ${lockBody} }`,{mode:0o700});
 writeFileSync(python,`#!${process.execPath}
console.log(${JSON.stringify(JSON.stringify(pythonInfo))});`,{mode:0o700});
 return {directory,visits,env:{SCAFFOLD_UV:uv,SCAFFOLD_PYTHON:python,UV_CACHE_DIR:directory}};
}
test('successful probes reject unsupported uv/Python/implementation/free-threaded values before output',()=>{
 const cases=[['uv 0.13.0',undefined],['uv 0.13.1',{version:'3.14.0',implementation:'CPython',free_threaded:false}],
  ['uv 0.13.1',{version:'3.15.0',implementation:'PyPy',free_threaded:false}],
  ['uv 0.13.1',{version:'3.15.0',implementation:'CPython',free_threaded:true}]];
 for(const [uv,python] of cases) {
  const fixture=fixtureTools(uv,python);
  const before=proofNames();
  const result=run(fixture.env);
  assert.deepEqual(proofNames(),before);
  assert.ifError(result.error);assert.equal(result.status,1);assert.equal(result.stderr,'');
  assert.deepEqual(JSON.parse(result.stdout),{error:'configured_tool_version_invalid',bootstrap_only:true,generation_ready:false});
  assert.equal(readFileSync(fixture.visits,'utf8'),'--version\n');
 }
});
test('unwritable proof manifest retains failed proof and emits only safe failure JSON',()=>{
 const fixture=fixtureTools('uv 0.13.1',undefined,"chmodSync(join(process.cwd(),'..','proof.json'),0o400); process.exit(1);");
 const result=run(fixture.env);
 assert.ifError(result.error);assert.equal(result.status,1);assert.equal(result.stderr,'');
 const output=JSON.parse(result.stdout);
 assert.equal(output.error,'bootstrap_failed');assert.equal(output.failure_recording_failed,true);
 assert.equal(output.bootstrap_only,true);assert.equal(output.generation_ready,false);
 assert.ok(existsSync(join(output.proof,'output','main.py')));
 assert.ok(existsSync(join(output.proof,'lock.log')));
 assert.equal(JSON.parse(readFileSync(join(output.proof,'proof.json'),'utf8')).status,'incomplete');
 assert.ok(!existsSync(join(output.proof,'output','uv.lock')));
 assert.ok(!existsSync(join(output.proof,'first')));
 assert.equal(readFileSync(fixture.visits,'utf8').split('\n').filter(Boolean).length,2);
});
