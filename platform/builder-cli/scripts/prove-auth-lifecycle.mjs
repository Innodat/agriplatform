// Internal fresh-output Auth pattern proof, no arbitrary output target or dependency installation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {renderApplication} from '../src/application-renderer.ts';
import {installScaffold,checkScaffold} from '../src/scaffold-install.ts';
assert.equal(process.version,'v26.11.1','unqualified_node_runtime');
if(process.argv.length>3||(process.argv[2]&&process.argv[2]!=='--acceptance-only'))throw new Error('arguments_invalid');
const root=fileURLToPath(new URL('../../../',import.meta.url)),hash=v=>createHash('sha256').update(v).digest('hex');
const directory=join(root,'platform/deployment/.local/scaffold-auth-lifecycle-20261023');mkdirSync(directory,{recursive:true,mode:0o700});
const proof=mkdtempSync(join(directory,'proof-')),output=join(proof,'application');
const recipe={schema_version:1,owner_id:'auth_sample',owner_kind:'application',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'apps/auth-sample/deployment/manifest.json'};
const files=renderApplication(recipe,root),identity={generator:'builder-v1',template:'application-v1-candidate',recipe:hash(JSON.stringify(recipe)),source:hash(JSON.stringify(files))};
let passed=false;const checks=[];
try{
 installScaffold(output,files,identity);checkScaffold(output);checks.push('actual_renderer_installer');
 const args=['--test'];if(process.argv.includes('--acceptance-only'))args.push('--test-name-pattern','bootstrap admits');args.push(join(output,'web/scripts/test-auth-lifecycle.mjs'));
 const tests=spawnSync(process.execPath,args,{encoding:'utf8',timeout:30000});writeFileSync(join(proof,'tests.log'),tests.stdout+tests.stderr);assert.equal(tests.status,0,'generated_behavior_failed');checks.push('generated_behavior');
 writeFileSync(join(output,'web/src/App.tsx'),'// owner custom seed\n');writeFileSync(join(output,'custom.txt'),'owner custom');installScaffold(output,files,identity);checkScaffold(output);
 assert.equal(readFileSync(join(output,'web/src/App.tsx'),'utf8'),'// owner custom seed\n');assert.equal(readFileSync(join(output,'custom.txt'),'utf8'),'owner custom');checks.push('owner_custom_preserved');passed=true;
}finally{
 const result={passed,checks,proof,output,recipe,identity,node:process.version,generated_sha256:Object.fromEntries(Object.entries(files).filter(([,f])=>f.classification==='generated').map(([p,f])=>[p,hash(f.content)])),limitations:['synthetic injected owner boundary','internal candidate, not public generator or provider configuration']};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');if(!passed)process.exitCode=1;process.stdout.write(JSON.stringify({passed,proof})+'\n');
}
