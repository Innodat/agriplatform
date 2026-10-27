// Explicit synthetic adapter qualification; private source/output custody per invocation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,chmodSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const acceptanceOnly=process.argv.includes('--acceptance-only');
const root=process.cwd(),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v26.11.1');
const tsc=join(root,'platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules/typescript/bin/tsc');
const paths=[
 'apps/kdg-capture/web/src/admin-edit.ts','apps/kdg-capture/web/src/read-validation.ts','apps/kdg-capture/web/src/read.ts','apps/kdg-capture/web/src/entry.ts',
 'apps/kdg-capture/contracts/admin-edit-generated/types.gen.ts','apps/kdg-capture/contracts/read-generated/types.gen.ts','apps/kdg-capture/contracts/generated/types.gen.ts',
 'apps/kdg-capture/write-candidate/admin-edit-openapi.json',
 'apps/kdg-capture/web/tsconfig.json','apps/kdg-capture/web/tsconfig.admin-edit-adapter.json','apps/kdg-capture/web/tests/admin-edit-adapter.types.ts',
 'apps/kdg-capture/web/tests/admin-edit-adapter.test.mjs','apps/kdg-capture/web/tests/admin-edit-adapter-proof.mjs','apps/kdg-capture/web/package.json'
];
const proof=join(root,'platform/deployment/.local/kdg-admin-edit-adapter-20261027/run-'+randomUUID()),capsule=join(proof,'capsule');
mkdirSync(capsule,{recursive:true,mode:0o700});
const sources=Object.fromEntries(paths.map(path=>{const bytes=readFileSync(join(root,path)),destination=join(capsule,path);mkdirSync(dirname(destination),{recursive:true,mode:0o700});writeFileSync(destination,bytes,{mode:0o400});return[path,hash(bytes)];}));
const commands=[];let passed=false;
const run=(name,args)=>{
 const result=spawnSync(process.execPath,args,{cwd:capsule,encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024});
 const log=join(proof,name+'.log');writeFileSync(log,(result.stdout??'')+(result.stderr??''),{mode:0o400});
 const record={name,command:[process.execPath,...args],exit_code:result.status,signal:result.signal,error_code:result.error?.code??null,log};commands.push(record);
 if(result.status!==0||result.error)throw Error(name+'_failed');return result.stdout;
};
try{
 assert.match(run('toolchain',[tsc,'--version']),/Version 7\.0\.2\s*$/);
 run('strict-types-and-emit',[tsc,'--project',join(capsule,'apps/kdg-capture/web/tsconfig.admin-edit-adapter.json'),'--noEmit','false','--rootDir',join(capsule,'apps/kdg-capture'),'--outDir',join(capsule,'compiled')]);
 writeFileSync(join(capsule,'compiled/package.json'),'{"type":"module"}\n',{mode:0o400});
 run('behavior',['--test','--test-isolation=none',...(acceptanceOnly?['--test-name-pattern=administrator explicit PUT returns matching immutable original operation receipt']:[]),join(capsule,'apps/kdg-capture/web/tests/admin-edit-adapter.test.mjs')]);
 passed=true;
}catch(error){writeFileSync(join(proof,'failure.log'),String(error?.stack??error)+'\n',{mode:0o400});}
finally{
 const unchanged=paths.every(path=>hash(readFileSync(join(root,path)))===sources[path]);
 const result={passed:passed&&unchanged,proof,mode:acceptanceOnly?'named-put-receipt-acceptance-only':'all-focused-behavior',node:process.version,typescript:'7.0.2',source_sha256:sources,source_unchanged:unchanged,commands,limits:['synthetic fetch/stream consumer only; no UI/Auth wiring or activation','no native SQL, real services/accounts, storage or deployment']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o400});chmodSync(join(proof,'result.json'),0o400);
 console.log(JSON.stringify({passed:result.passed,proof}));if(!result.passed)process.exitCode=1;
}
