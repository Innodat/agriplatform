import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {selectChanges, publicFingerprint} from '../frontend-inputs.mjs';
function fixture(t){
 const root=mkdtempSync(path.join(tmpdir(),'frontend-history-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
 const write=(name,value='fixture')=>{mkdirSync(path.dirname(path.join(root,name)),{recursive:true});writeFileSync(path.join(root,name),value);};
 git('init','-q');git('config','user.email','fixture@example.test');git('config','user.name','Fixture');
 write('platform/deployment/registry.json',JSON.stringify({manifests:['apps/demo/deployment/manifest.json']}));
 write('apps/demo/deployment/manifest.json',JSON.stringify({frontend:{path:'custom/browser'}}));
 write('custom/browser/main.js');write('platform/new-shared/package.json','{}');write('platform/new-shared/index.js');write('apps/demo/web/old.js');
 git('add','.');git('commit','-qm','baseline');const base=git('rev-parse','HEAD');
 const commit=()=>{git('add','-A');git('commit','-qm','change');return git('rev-parse','HEAD');};
 return {root,git,write,base,commit};
}
test('backend-only changes skip; unpublished frontend commits remain included',t=>{
 const f=fixture(t);f.write('services/access/main.py');let head=f.commit();assert.equal(selectChanges(f.root,f.base,head).build,false);
 f.write('custom/browser/main.js','changed');f.commit();f.write('docs/general.md');head=f.commit();assert.equal(selectChanges(f.root,f.base,head).build,true);
});
test('deleted and renamed old frontend paths and discovered shared packages build',t=>{
 const f=fixture(t);f.git('mv','apps/demo/web/old.js','server.js');assert.equal(selectChanges(f.root,f.base,f.commit()).build,true);
 const base=f.git('rev-parse','HEAD');f.write('platform/new-shared/index.js','changed');assert.equal(selectChanges(f.root,base,f.commit()).build,true);
});
test('missing, invalid, equal and nonancestor baselines build',t=>{
 const f=fixture(t);for(const base of ['', 'missing',f.base])assert.equal(selectChanges(f.root,base,f.base).build,true);
 f.write('services/a.py');const future=f.commit();assert.equal(selectChanges(f.root,future,f.base).build,true);
});
test('public fingerprint is reproducible and includes the public key, excludes credentials',()=>{
 const env={DEPLOY_ENV:'production',PUBLIC_SITE_ORIGIN:'https://site.test',PUBLIC_API_ORIGIN:'https://api.test',VITE_SUPABASE_URL:'https://db.test',VITE_SUPABASE_ANON_KEY:'sb_publishable_fixture'};
 assert.equal(publicFingerprint(env),publicFingerprint({...env,NETLIFY_AUTH_TOKEN:'private'}));
 assert.notEqual(publicFingerprint(env),publicFingerprint({...env,VITE_SUPABASE_ANON_KEY:'sb_publishable_rotated'}));
});
test('frontend configuration, registry changes and future frontends rebuild',t=>{
 const f=fixture(t);
 for(const name of ['.yarn/releases/yarn.cjs','.yarn/plugins/plugin.cjs','.yarn/patches/dependency.patch','package.json','package-lock.json','.npmrc','.nvmrc','tsconfig.json','netlify.toml','apps/future/frontend/main.ts','platform/deployment/build-release.mjs','platform/deployment/install-frontends.py','tools/build-browser.mjs','apps/new/deployment/manifest.json']){
  const base=f.git('rev-parse','HEAD');f.write(name,'{}');assert.equal(selectChanges(f.root,base,f.commit()).build,true,name);
 }
});
test('backend infrastructure and general documentation skip together',t=>{
 const f=fixture(t);for(const name of ['apps/demo/api/main.py','apps/demo/migrations/v1.py','platform/deployment/wireguard/runner.py','platform/deployment/terraform/main.tf','platform/deployment/host-release.py','docs/readme.md'])f.write(name);
 assert.equal(selectChanges(f.root,f.base,f.commit()).build,false);
});
test('deleted registered input and removed registry mapping rebuild',t=>{
 const f=fixture(t);f.git('rm','custom/browser/main.js');assert.equal(selectChanges(f.root,f.base,f.commit()).build,true);
 const base=f.git('rev-parse','HEAD');f.write('platform/deployment/registry.json',JSON.stringify({manifests:[]}));assert.equal(selectChanges(f.root,base,f.commit()).build,true);
});
test('unavailable manifest history never authorizes skip',t=>{
 const f=fixture(t);f.write('apps/demo/deployment/manifest.json','broken json');const base=f.commit();f.write('docs/a.md');assert.equal(selectChanges(f.root,base,f.commit()).build,true);
});

test('native ignore uses exit zero only for a safe skip and force overrides it',t=>{
 const f=fixture(t);f.write('services/access/main.py');const current=f.commit();
 const detector=fileURLToPath(new URL('../frontend-inputs.mjs',import.meta.url));
 const run=extra=>spawnSync(process.execPath,[detector,'ignore'],{cwd:f.root,env:{...process.env,CACHED_COMMIT_REF:f.base,COMMIT_REF:current,...extra}}).status;
 assert.equal(run({}),0);for(const force of ['true','TRUE','True'])assert.equal(run({FORCE_FRONTEND_BUILD:force}),1);assert.equal(run({FORCE_FRONTEND_BUILD:'false'}),0);assert.equal(run({CACHED_COMMIT_REF:''}),1);assert.equal(run({CACHED_COMMIT_REF:current}),1);
});
test('shallow history rebuilds conservatively',t=>{
 const f=fixture(t);f.write('services/a.py');const current=f.commit();
 const clone=mkdtempSync(path.join(tmpdir(),'frontend-shallow-'));t.after(()=>rmSync(clone,{recursive:true,force:true}));
 execFileSync('git',['clone','-q','--depth=1','file://'+f.root,clone]);
 assert.equal(selectChanges(clone,f.base,current).build,true);
});
