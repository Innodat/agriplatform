import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync, symlinkSync, rmSync, readdirSync, lstatSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join, relative, resolve } from 'node:path';
import { test } from 'node:test';
const root = fileURLToPath(new URL('../../../', import.meta.url));
const cli = join(root, 'platform/builder-cli/src/cli.ts');
const fixture = mkdtempSync(join(root, 'platform/builder-cli/tests/fixture-'));
const ref = name => relative(root, join(fixture, name)).replaceAll('\\', '/');
writeFileSync(join(fixture, 'source.md'), 'authority');
writeFileSync(join(fixture, 'contract.md'), 'contract');
mkdirSync(join(fixture, 'custom')); mkdirSync(join(fixture, 'custom2'));
mkdirSync(join(fixture, 'custom/nested'));
symlinkSync(join(fixture, 'source.md'), join(fixture, 'link.md'));
symlinkSync(join(fixture, 'custom'), join(fixture, 'link-dir'));
const base = () => ({schema_version:1, owner_id:'test_owner', owner_kind:'application', sources:[ref('source.md')], contracts:[ref('contract.md')], patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'], extensions:[], deployment_manifest:'apps/test-owner/deployment/manifest.json'});
const run = (args, cwd=root) => spawnSync(process.execPath, [cli, ...args], {cwd, encoding:'utf8'});
const absentDestinations = [
 'apps/test-owner', 'apps/test-owner/deployment', 'apps/test-owner/deployment/manifest.json',
 'services/test_owner', 'services/test_owner/deployment', 'services/test_owner/deployment/first.json',
];
function assertDestinationsAbsent() {
 for (const path of absentDestinations) assert.throws(() => lstatSync(join(root,path)), {code:'ENOENT'});
}
const snapshot = path => readdirSync(path).sort().map(name => { const p=join(path,name), stat=lstatSync(p); return [name, stat.isSymbolicLink()?'symlink':stat.isDirectory()?snapshot(p):readFileSync(p,'base64')]; });
function check(recipe, expected='recipe_valid', cwd=root) {
 const config=join(fixture,'recipe.json'); writeFileSync(config,JSON.stringify(recipe)); const before=snapshot(fixture);
 assertDestinationsAbsent();
 const result=run(['--config', cwd===root?relative(root,config):config],cwd);
 assertDestinationsAbsent();
 assert.ifError(result.error);
 assert.equal(result.status,expected==='recipe_valid'?0:1,JSON.stringify({recipe,stderr:result.stderr}));
 const output=JSON.parse(result.stdout); assert.equal(output[expected==='recipe_valid'?'recipe_valid':'error'],expected==='recipe_valid'?true:expected);
 if(expected==='recipe_valid') assert.deepEqual(output,{recipe_valid:true,generation_ready:false});
 assert.deepEqual(snapshot(fixture),before,'CLI must be read-only');
 assert.equal((result.stdout+result.stderr).includes('SECRET_PAYLOAD'),false);
}
test('acceptance: app and service CLI validate without output or authority',()=>{
 check(base()); const service=base(); service.owner_kind='service';service.patterns=service.patterns.filter(p=>!p.startsWith('web.')&&!p.startsWith('auth.')).concat('auth.service-owner.v1');service.deployment_manifest='services/test_owner/deployment/first.json';check(service,'recipe_valid','/tmp');
 const extended=base();extended.extensions=[{source:ref('custom'),destination:'modules/one'},{source:ref('custom2'),destination:'modules/two'}];check(extended);
});
test('documented npm workspace command resolves config relative to invocation directory', () => {
 const config=join(fixture,'npm-recipe.json'); writeFileSync(config,JSON.stringify(base()));
 const before=snapshot(fixture);
 assertDestinationsAbsent();
 const npmArgs=['run','validate:recipe','--workspace','platform/builder-cli','--','--config',relative(root,config)];
 const result=process.env.npm_execpath
   ? spawnSync(process.execPath,[process.env.npm_execpath,...npmArgs],{cwd:root,encoding:'utf8'})
   : spawnSync('npm',npmArgs,{cwd:root,encoding:'utf8'});
 assert.ifError(result.error);
 assert.equal(result.status,0,result.stdout+result.stderr);
 assert.ok(result.stdout.includes('{"recipe_valid":true,"generation_ready":false}'));
 assert.deepEqual(snapshot(fixture),before);
 assertDestinationsAbsent();
});
test('strict shape, bounds, uniqueness and unsupported combinations',()=>{
 for(const mutate of [r=>r.sources='source.md',r=>r.contracts=[42],r=>r.patterns=null,r=>r.extensions={},r=>r.schema_version='1',r=>r.owner_id=42,r=>r.owner_kind=null,r=>r.deployment_manifest=42,r=>delete r.contracts,r=>delete r.extensions,r=>r.contracts=[],r=>r.sources=[''],r=>r.sources=['x'.repeat(513)],r=>r.sources=Array.from({length:101},(_,i)=>`missing-${i}.md`),r=>r.extra='SECRET_PAYLOAD',r=>r.schema_version=2,r=>r.owner_id='x',r=>r.owner_kind='worker',r=>r.sources=[],r=>r.contracts=Array(101).fill(ref('contract.md')),r=>r.sources.push(r.sources[0]),r=>r.contracts=[r.sources[0]],r=>r.patterns.push(r.patterns[0]),r=>r.patterns=[],r=>r.extensions=[{source:ref('custom'),destination:'x',extra:true}],r=>r.owner_id='a'.repeat(65),r=>r.deployment_manifest='a'.repeat(513),r=>r.patterns.push('SECRET_PAYLOAD'),r=>r.patterns.push('auth.service-owner.v1'),r=>r.patterns=r.patterns.filter(p=>p!=='saving.none.v1'),r=>r.owner_kind='service',r=>r.extensions=Array(101).fill({source:ref('custom'),destination:'x'})]){const r=base();mutate(r);check(r,'recipe_invalid');}
});
test('unsafe references, extension overlap and owner manifest boundaries',()=>{
 for(const mutate of [r=>r.sources=['file:secret'],r=>r.contracts=['file\0secret'],r=>r.extensions=[{source:ref('custom'),destination:'a'},{source:ref('custom2'),destination:'a'}],r=>r.sources=['missing.md'],r=>r.sources=['../escape'],r=>r.sources=['/absolute/SECRET_PAYLOAD'],r=>r.sources=[ref('link.md')],r=>r.sources=[ref('custom')],r=>r.sources=[`${ref('custom')}/../source.md`],r=>r.sources=[`${ref('custom')}//file`],r=>r.contracts=[ref('link-dir/child')],r=>r.extensions=[{source:ref('missing'),destination:'x'}],r=>r.extensions=[{source:ref('link-dir'),destination:'x'}],r=>r.extensions=[{source:ref('custom'),destination:'../x'}],r=>r.extensions=[{source:ref('custom'),destination:'/x'}],r=>r.extensions=[{source:ref('custom'),destination:'a/./b'}],r=>r.extensions=[{source:ref('custom'),destination:'a\\b'}],r=>r.extensions=[{source:ref('custom'),destination:'a'},{source:ref('custom2'),destination:'a/b'}],r=>r.extensions=[{source:ref('custom'),destination:'a'},{source:ref('custom/nested'),destination:'b'}],r=>r.deployment_manifest='services/test-owner/deployment/x.json',r=>r.deployment_manifest='apps/another/deployment/x.json',r=>r.deployment_manifest='apps/test-owner/deployment/../x.json',r=>r.deployment_manifest='apps/test-owner/deployment',r=>r.deployment_manifest='/apps/test-owner/deployment/x.json']){const r=base();mutate(r);check(r,'recipe_invalid');}
});
test('CLI misuse and malformed JSON yield safe stable identifiers',()=>{
 for(const args of [[],['--config'],['--unknown','SECRET_PAYLOAD'],['--config','x','--config','y'],['--config','x','--output','y'],['--config=x']]){const result=run(args);assert.ifError(result.error);assert.equal(result.status,1);assert.deepEqual(JSON.parse(result.stdout),{error:'arguments_invalid'});assert.equal(result.stderr,'');}
 const config=join(fixture,'bad.json');writeFileSync(config,'SECRET_PAYLOAD{');const result=run(['--config',config]);assert.equal(result.status,1);assert.deepEqual(JSON.parse(result.stdout),{error:'config_unreadable'});assert.equal(result.stderr,'');
 assert.deepEqual(JSON.parse(run(['--config',join(fixture,'missing.json')]).stdout),{error:'config_unreadable'});
});
test.after(()=>rmSync(fixture,{recursive:true,force:true}));
