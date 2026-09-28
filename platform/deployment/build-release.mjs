// Build only explicit frontend artifacts; never publish repository files.
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {publicFingerprint} from './frontend-inputs.mjs';
import {mkdtemp,rm,mkdir,cp,readdir,readFile,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
export function validateInputs(input){
 const required=['DEPLOY_ENV','PUBLIC_SITE_ORIGIN','PUBLIC_API_ORIGIN','VITE_SUPABASE_URL','VITE_SUPABASE_ANON_KEY'];
 for(const field of required)if(!input[field])throw Error(`Missing ${field}`);
 if(!['staging','production'].includes(input.DEPLOY_ENV))throw Error('Invalid DEPLOY_ENV');
 for(const field of ['PUBLIC_SITE_ORIGIN','PUBLIC_API_ORIGIN','VITE_SUPABASE_URL']){
  const url=new URL(input[field]);
  if(url.protocol!=='https:'||url.username||url.password||url.pathname!=='/'||input[field].endsWith('/')||url.search||url.hash)throw Error(`Invalid ${field}`);
 }
 if(input.DEPLOY_ENV==='staging' && (input.PUBLIC_SITE_ORIGIN==='https://scribeswell.com'||input.PUBLIC_API_ORIGIN==='https://api.scribeswell.com'||input.VITE_SUPABASE_URL==='https://gjbsnxmbhxsvcblzgfts.supabase.co'))throw Error('Staging cannot use production targets');
 const key=input.VITE_SUPABASE_ANON_KEY||'';
 let publicKey=/^sb_publishable_[A-Za-z0-9_-]+$/.test(key);
 if(!publicKey)try{publicKey=key.split('.').length===3&&JSON.parse(Buffer.from(key.split('.')[1],'base64url')).role==='anon';}catch{}
 if(!publicKey) throw Error('VITE_SUPABASE_ANON_KEY must be a public publishable or anon key');
 return {VITE_SUPABASE_URL:input.VITE_SUPABASE_URL,VITE_SUPABASE_ANON_KEY:key,VITE_PLATFORM_ORIGIN:input.PUBLIC_SITE_ORIGIN,VITE_MICROSOFT_SIGN_IN_ENABLED:'false'};
}
export function redirectsFor(apps){
 const nested=apps.filter(app=>app.frontend.base!=='/').sort((a,b)=>b.frontend.base.length-a.frontend.base.length);
 return nested.map(app=>`${app.frontend.base.slice(0,-1)} ${app.frontend.base} 301\n${app.frontend.base}* ${app.frontend.base}index.html 200`).concat(apps.some(app=>app.frontend.base==='/')?'/* /index.html 200':[]).join('\n')+'\n';
}
export const hasSecretToken = text => /sb_secret_[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/.test(text) && (/sb_secret_[A-Za-z0-9_-]{16,}/.test(text) || [...text.matchAll(/eyJ[A-Za-z0-9_-]*\.([A-Za-z0-9_-]+)\.[A-Za-z0-9_-]+/g)].some(match=>{try{return JSON.parse(Buffer.from(match[1],'base64url')).role==='service_role';}catch{return false;}}));
export async function build(){
 const inputs=validateInputs(process.env); // Validate before modifying outputs.
 const isolated=await mkdtemp(path.join(tmpdir(),'scribeswell-build-'));
 const output=path.join(root,'platform/deployment/public-release');
 // Do not forward arbitrary process credentials or ignored VITE_* local settings.
 const env={PATH:process.env.PATH,HOME:process.env.HOME,SystemRoot:process.env.SystemRoot,NODE_ENV:'production',...inputs,RELEASE_ENV_DIR:isolated};
 try{
  await rm(output,{recursive:true,force:true});await mkdir(output,{recursive:true});
  const manifestResult=spawnSync('python3',['platform/deployment/release.py','list'],{cwd:root,encoding:'utf8'});
  if(manifestResult.status!==0)throw Error('Invalid release manifests');
  const apps=JSON.parse(manifestResult.stdout).filter(app=>app.frontend);
  for(const app of apps){
   const base=app.frontend.base,target=path.join(output,base.slice(1));
   const cwd=path.join(root,app.frontend.path);
   const run=spawnSync('npm',['run','build','--','--emptyOutDir'],{cwd,env:{...env,...Object.fromEntries(Object.entries(app.frontend.api_variables||{}).map(([key,suffix])=>[key,process.env.PUBLIC_API_ORIGIN+suffix])),VITE_APP_BASE:base},stdio:'inherit'});
   if(run.status!==0)throw Error(`${app.id} build failed`);
   await cp(path.join(cwd,'dist'),target,{recursive:true});
  }
  async function audit(dir){for(const entry of await readdir(dir,{withFileTypes:true})){
   const name=path.join(dir,entry.name);
   if(entry.isSymbolicLink())throw Error('Artifact contains symlink');
   if(entry.isDirectory()){await audit(name);continue;}
   if(!/\.(html|js|css|woff2?|ttf|svg|png|ico|webp|jpg|jpeg|txt)$/.test(name))throw Error('Unexpected static artifact extension');
   if(/\.(html|js|css)$/.test(name)){const contents=await readFile(name,'utf8');if(hasSecretToken(contents)||/localhost:8010|localhost:8001/.test(contents))throw Error('Unsafe configuration in artifact');}
  }}
  await audit(output);
  await writeFile(path.join(output,'_redirects'),redirectsFor(apps));
  await writeFile(path.join(output,'release-identity.json'),JSON.stringify({public_build_fingerprint:publicFingerprint(process.env),sha:process.env.RELEASE_SHA||null,environment:process.env.DEPLOY_ENV,site:process.env.PUBLIC_SITE_ORIGIN,api:process.env.PUBLIC_API_ORIGIN,supabase_url:process.env.VITE_SUPABASE_URL,release_attempt:process.env.GITHUB_RUN_ID&&process.env.GITHUB_RUN_ATTEMPT?process.env.GITHUB_RUN_ID+'-'+process.env.GITHUB_RUN_ATTEMPT:null})+'\n');
  console.log('Static release ready: platform/deployment/public-release');
 }catch(error){await rm(output,{recursive:true,force:true});throw error;}finally{await rm(isolated,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) build().catch(error=>{console.error(error.message);process.exitCode=1;});
