// Shared, dependency-free policy; compatible with the Node 18 Netlify ignore runner.
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const publicFields=['DEPLOY_ENV','PUBLIC_SITE_ORIGIN','PUBLIC_API_ORIGIN','VITE_SUPABASE_URL','VITE_SUPABASE_ANON_KEY'];
export function publicFingerprint(env){
 if(publicFields.some(key=>typeof env[key]!=='string'||!env[key]))throw Error('missing_public_inputs');
 return createHash('sha256').update(JSON.stringify(publicFields.map(key=>[key,env[key]]))).digest('hex');
}
function git(root,...args){return execFileSync('git',args,{cwd:root,encoding:'utf8',stdio:['ignore','pipe','pipe'],maxBuffer:32*1024*1024});}
function inputs(root,revision){
 const files=git(root,'ls-tree','-r','--name-only','-z',revision).split('\0').filter(Boolean);
 const registry=JSON.parse(git(root,'show',revision+':platform/deployment/registry.json'));
 if(!Array.isArray(registry.manifests))throw Error('invalid_registry');
 const roots=['platform/ui-core','platform/ui-business','platform/api-client','platform/app-directory-client','platform/shared'];
 for(const manifest of registry.manifests){
  const app=JSON.parse(git(root,'show',revision+':'+manifest));
  if(app.frontend){const dir=app.frontend.path;if(typeof dir!=='string'||!dir||dir.startsWith('/')||dir.split('/').some(part=>part==='..'||part==='.'))throw Error('invalid_frontend');roots.push(dir.replace(/\/$/,''));}
 }
 for(const file of files)if(/^platform\/.+\/package.json$/.test(file))roots.push(path.posix.dirname(file));
 return {roots,manifests:registry.manifests};
}
export function isFrontendInput(file,policy){
 if(file.startsWith('.yarn/'))return true;
 if(policy.roots.some(root=>file===root||file.startsWith(root+'/'))||policy.manifests.includes(file))return true;
 if(/^apps\/[^/]+\/(web|frontend)(\/|$)/.test(file)||/^apps\/[^/]+\/deployment\/manifest.json$/.test(file))return true;
 if(file==='platform/deployment/registry.json'||file==='netlify.toml'||file==='.github/workflows/production.yml')return true;
 if(!file.includes('/')&&/^(package.*\.json|.*lock.*|\.?npm.*|\.?yarn.*|pnpm.*|\.node-version|\.nvmrc|\.tool-versions|.*config\.[cm]?[jt]s|tsconfig.*\.json|\.browserslistrc|bunfig.toml|\.babelrc.*|\.pnp.*|browserslist)$/.test(file))return true;
 if(/^platform\/deployment\/(build-release\.mjs|frontend-inputs\.mjs|install-frontends\.py|record-production\.py|release\.py)$/.test(file))return true;
 return /^(tools|scripts)\/.*(frontend|netlify|vite|webpack|rollup|esbuild|tailwind|postcss|publish|build)/i.test(file);
}
export function selectChanges(root,baseline,current){
 try{
  if(!/^[a-f0-9]{40}$/.test(baseline||'')||!/^[a-f0-9]{40}$/.test(current||''))throw Error('invalid_revision');
  if(baseline===current)return {build:true,reason:'equal_revision'};
  if(git(root,'rev-parse','--is-shallow-repository').trim()!=='false')throw Error('shallow_history');
  git(root,'merge-base','--is-ancestor',baseline,current);
  const old=inputs(root,baseline),now=inputs(root,current);
  const policy={roots:[...old.roots,...now.roots],manifests:[...old.manifests,...now.manifests]};
  // Disable rename detection: both the deleted old path and added new path count.
  const changed=git(root,'diff','--no-renames','--name-only','-z',baseline,current,'--').split('\0').filter(Boolean);
  return changed.some(file=>isFrontendInput(file,policy))?{build:true,reason:'frontend_inputs_changed'}:{build:false,reason:'no_frontend_inputs_changed'};
 }catch{return {build:true,reason:'uncertain_history_or_inputs'};}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv[2]==='fingerprint')console.log(publicFingerprint(process.env));
 else{
  const native=process.argv[2]==='ignore';
  const result=native&&(process.env.FORCE_FRONTEND_BUILD||'').toLowerCase()==='true'?{build:true,reason:'manual_force'}:selectChanges(process.cwd(),native?process.env.CACHED_COMMIT_REF:process.argv[2],native?process.env.COMMIT_REF:process.argv[3]);
  if(native){console.log('Frontend decision: '+result.reason);process.exitCode=result.build?1:0;}else console.log(JSON.stringify(result));
 }
}
