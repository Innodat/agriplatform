// Isolated strict TypeScript and synthetic setup transport/Auth proof; no persistence or startup.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,symlinkSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root=process.cwd(),owner='apps/kdg-capture',retained=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root');
assert.equal(process.version,'v26.11.1');assert.equal(JSON.parse(readFileSync(join(retained,'node_modules/typescript/package.json'))).version,'7.0.2');
const proof=join(root,'platform/deployment/.local/kdg-provision-contract-20261026/client-'+randomUUID());mkdirSync(proof,{recursive:true,mode:0o700});
const capsule=join(proof,'capsule');mkdirSync(capsule);writeFileSync(join(capsule,'package.json'),'{"type":"module","private":true}');symlinkSync(join(retained,'node_modules'),join(capsule,'node_modules'));
const sources=['web/src/provision.ts','web/src/provision-entry.ts','web/tsconfig.provision.json','web/tests/provision.types.ts','contracts/provision-generated/types.gen.ts','web/src/read-validation.ts','web/src/read.ts','web/src/entry.ts','web/src/own-observation.ts','web/src/auth-entry.ts','web/src/auth/lifecycle.ts','web/tsconfig.auth.json','contracts/generated/types.gen.ts','contracts/read-generated/types.gen.ts','web/tests/read-fixture.mjs','web/tests/provision-fixture.mjs','web/tests/provision.test.mjs','web/tests/provision-entry.test.mjs','web/tests/provision-proof.mjs'].map(x=>owner+'/'+x);
const hash=x=>createHash('sha256').update(x).digest('hex'),captured={};for(const name of sources){const value=readFileSync(name),to=join(capsule,name);mkdirSync(resolve(to,'..'),{recursive:true});writeFileSync(to,value);captured[name]=hash(value);}
writeFileSync(join(capsule,'tsconfig.json'),JSON.stringify({extends:join(capsule,owner,'web/tsconfig.provision.json'),compilerOptions:{noEmit:false,rootDir:join(capsule,owner),outDir:join(capsule,'compiled')},files:[join(capsule,owner,'web/src/provision.ts'),join(capsule,owner,'web/src/provision-entry.ts'),join(capsule,owner,'web/tests/provision.types.ts')]}));
let passed=false,testCounts,executedTests=[];
try{
 const configured=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,owner,'web/tsconfig.provision.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'configured-types.log'),configured.stdout+configured.stderr);assert.equal(configured.status,0,'actual_provision_config_failed');
 const types=spawnSync(process.execPath,[join(retained,'node_modules/typescript/bin/tsc'),'-p',join(capsule,'tsconfig.json')],{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'types.log'),types.stdout+types.stderr);assert.equal(types.status,0,'strict_types_failed');
 const tests=spawnSync(process.execPath,['--test','--test-reporter=tap','--test-concurrency=1',join(capsule,owner,'web/tests/provision.test.mjs'),join(capsule,owner,'web/tests/provision-entry.test.mjs')],{encoding:'utf8',timeout:60000});writeFileSync(join(proof,'unit.log'),tests.stdout+tests.stderr);assert.equal(tests.status,0,'behavior_failed');testCounts=Object.fromEntries(['tests','pass','fail','skipped','cancelled','todo'].map(key=>[key,Number(tests.stdout.match(new RegExp('^# '+key+' ([0-9]+)$','m'))?.[1])]));assert.ok(testCounts.tests>0&&testCounts.pass===testCounts.tests&&testCounts.fail===0&&testCounts.skipped===0&&testCounts.cancelled===0);executedTests=[...tests.stdout.matchAll(/^# Subtest: (.*)$/gm)].map(x=>x[1]);passed=true;
}finally{
 const unchanged=sources.every(x=>hash(readFileSync(x))===captured[x]);const record={passed:passed&&unchanged,proof,test_counts:testCounts,executed_tests:executedTests,source_sha256:captured,source_unchanged:unchanged,node:process.version,typescript:'7.0.2',limitations:['synthetic transport only; no live Auth/Access or database']};writeFileSync(join(proof,'result.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({passed:record.passed,proof}));if(!record.passed)process.exitCode=1;
}
