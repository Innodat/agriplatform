import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { renderService } from '../src/service-renderer.ts';
import { renderApplication } from '../src/application-renderer.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const service={schema_version:1,owner_id:'bootstrap_service',owner_kind:'service',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','auth.service-owner.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'services/bootstrap-service/deployment/manifest.json'};
const application=()=>({...service,owner_id:'bootstrap_application',owner_kind:'application',patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],deployment_manifest:'apps/bootstrap-application/deployment/manifest.json'});
// The historical whole-service hash covered untyped main.py. Typed HealthResponse,
// declared error responses, relative servers and offline owner export intentionally
// change those bytes; pin the unchanged HTTP adapter instead of obscuring that change.
test('characterization: safe HTTP adapter survives typed OpenAPI boundary changes',()=>{
 const files=renderService(service,root);
 assert.equal(createHash('sha256').update(files['safe_errors.py'].content).digest('hex'),'18a1359b2b1f9bb8c79c91644582c9d320bf22ed56d53afac179ff3fce6901df');
 assert.match(files['main.py'].content,/class HealthResponse/);
 assert.equal(files['export_openapi.py'].classification,'seed');
});
test('acceptance: deterministic application file map, literal identity and explicit ownership',()=>{
 const input=application(), files=renderApplication(input,root);
 assert.deepEqual(files,renderApplication(input,root));
 assert.deepEqual(Object.keys(files).sort(),['AGENTS.md','README.md','api/AGENTS.md','api/README.md','api/export_openapi.py','api/main.py','api/pyproject.toml','api/safe_errors.py','api/tests/test_runtime.py','web/index.html','web/package.json','web/scripts/browser-smoke.mjs','web/scripts/proof-support.mjs','web/scripts/test-health.mjs','web/scripts/test-auth-lifecycle.mjs','web/src/App.tsx','web/src/auth/lifecycle.ts','web/src/auth/use-lifecycle.ts','web/src/api/health.ts','web/src/main.tsx','web/src/styles.css','web/tsconfig.json','web/vite.config.ts'].sort());
 for(const [path,file] of Object.entries(files)) {
  assert.ok(!path.includes('..')&&!path.startsWith('/')); assert.ok(['seed','generated'].includes(file.classification));
  assert.ok(!file.content.includes('{{')); assert.equal(file.classification==='generated',file.content.includes('GENERATED'));
 }
 assert.equal(files['web/src/App.tsx'].classification,'seed');
 assert.match(files['api/main.py'].content,/title="bootstrap_application"/);
 assert.match(files['web/src/App.tsx'].content,/bootstrap_application/);
 assert.equal(JSON.parse(files['web/package.json'].content).devDependencies.typescript,'7.0.2');
 const config=JSON.parse(files['web/tsconfig.json'].content);
 assert.deepEqual(config.compilerOptions.types,['node','vite/client']);
 assert.equal(config.compilerOptions.strict,true);
 assert.match(files['web/src/main.tsx'].content,/import '\.\/styles\.css'/);
 const edge=renderApplication({...input,owner_id:'a_',deployment_manifest:'apps/a_/deployment/manifest.json'},root);
 assert.match(edge['api/pyproject.toml'].content,/name = "a"/);
 for(const output of [files,edge]) {assert.match(output['README.md'].content,/cd web/);assert.doesNotMatch(output['README.md'].content,/bootstrap-application|--workspace/);}
});
test('acceptance: invalid, service, extension and token injection recipes refuse output',()=>{
 for(const input of [null,{},service,{...application(),owner_id:'{{OWNER}}'}, {...application(),extra:'SECRET'}, {...application(),extensions:[{source:'platform/builder-cli/src',destination:'web'}]}]) assert.throws(()=>renderApplication(input,root),{message:'application_bootstrap_unsupported'});
});
