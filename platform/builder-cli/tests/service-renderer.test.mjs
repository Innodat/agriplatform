import assert from 'node:assert/strict';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { renderService } from '../src/service-renderer.ts';
import { validateRecipe } from '../src/recipe.ts';
const root = fileURLToPath(new URL('../../../', import.meta.url));
export const recipe = () => ({schema_version:1,owner_id:'bootstrap_service',owner_kind:'service',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','auth.service-owner.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'services/bootstrap-service/deployment/manifest.json'});
test('acceptance: deterministic bounded standalone service files with explicit ownership', () => {
 const first=renderService(recipe(),root); assert.deepEqual(first,renderService(recipe(),root));
 assert.deepEqual(Object.keys(first).sort(),['AGENTS.md','README.md','export_openapi.py','main.py','pyproject.toml','safe_errors.py','tests/test_runtime.py']);
 assert.equal(first['main.py'].classification,'seed');
 for(const [path,file] of Object.entries(first)) {
  assert.ok(!path.startsWith('/') && !path.split('/').includes('..'));
  assert.ok(['seed','generated'].includes(file.classification));
  assert.equal(file.content.includes('{{'),false);
  assert.equal(file.content.includes('platform.deployment'),false);
 }
 assert.match(first['pyproject.toml'].content,/name = "bootstrap-service"/);
 assert.match(first['safe_errors.py'].content,/GENERATED/);
 assert.doesNotMatch(first['main.py'].content,/GENERATED|probe/);
});
test('acceptance: refuse invalid, application and extension recipes before output', () => {
 const application={...recipe(),owner_kind:'application',patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],deployment_manifest:'apps/bootstrap-service/deployment/manifest.json'};
 assert.equal(validateRecipe(application,root),true);
 assert.throws(()=>renderService(application,root),{message:'service_bootstrap_unsupported'});
 for(const input of [null,{}, {...recipe(),owner_id:'../secret'}, {...recipe(),owner_kind:'application'}, {...recipe(),extensions:[{source:'platform/builder-cli/src',destination:'custom'}]}, {...recipe(),extra:'SECRET_PAYLOAD'}]) {
  assert.throws(()=>renderService(input,root),{message:'service_bootstrap_unsupported'});
 }
});

test('accepted boundary owner produces valid package metadata without changing identity',()=>{
 const input={...recipe(),owner_id:'a_',deployment_manifest:'services/a_/deployment/manifest.json'};
 const output=renderService(input,root);
 assert.match(output['pyproject.toml'].content,/name = "a"/);
 assert.equal(input.owner_id,'a_');
 assert.match(output['main.py'].content,/title="a_"/);
 assert.match(output['README.md'].content,/# a_/);
});
