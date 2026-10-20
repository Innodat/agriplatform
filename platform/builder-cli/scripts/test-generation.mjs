// Internal candidate bootstrap only. No public generation command or supplied target.
import { runBounded } from './process-runner.mjs';
import { createHash } from 'node:crypto';
import { chmodSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderService } from '../src/service-renderer.ts';
const root = fileURLToPath(new URL('../../../', import.meta.url));
const builder = join(root, 'platform/builder-cli');
const parent = join(root, 'platform/deployment/.local/scaffold-generation');
const hash = value => createHash('sha256').update(value).digest('hex');
let proof, manifest;
const preflight = [];
const clean = {PATH:'/usr/bin:/bin', LC_ALL:'C.UTF-8'};
function fail(identifier) { throw new Error(identifier); }
function tool(name) {
 const value=process.env[name];
 if (!value || !isAbsolute(value) || !existsSync(value) || !statSync(value).isFile()) fail('configured_tool_invalid');
 return value;
}
function persist() {
 if (proof) writeFileSync(join(proof,'proof.json'),JSON.stringify(manifest,null,2)+'\n',{mode:0o600});
}
function run(label, executable, args, env=clean, cwd=builder) {
 const result=runBounded(executable,args,{cwd,env});
 const record={label,command:[executable,...args],cwd,environment:env,exit_code:result.status,
  signal:result.signal,completed:!result.error,
  error_code:result.error?.code??null,group_termination:result.groupTermination};
 const log=(result.stdout??'')+(result.stderr??'');
 record.log_sha256=hash(log);
 if (manifest) {
  manifest.commands.push(record);
  writeFileSync(join(proof,`${label}.log`),log,{mode:0o600});
  persist();
 } else preflight.push({record,log});
 if (result.error || result.status!==0) fail('bootstrap_stage_failed');
 return result.stdout.trim();
}
try {
 if (process.argv.length!==2) fail('arguments_invalid');
 const uv=tool('SCAFFOLD_UV'), python=tool('SCAFFOLD_PYTHON'), cache=process.env.UV_CACHE_DIR;
 if (!cache || !isAbsolute(cache) || !existsSync(cache) || !lstatSync(cache).isDirectory()) fail('configured_cache_invalid');
 // No fallback to host Python or downloaded runtimes. Version checks precede output.
 const uvVersion=run('uv-version',uv,['--version']);
 const pythonInfo=JSON.parse(run('python-version',python,['-I','-B','-c',"import json, platform, sysconfig; print(json.dumps({'version':platform.python_version(),'implementation':platform.python_implementation(),'free_threaded':bool(sysconfig.get_config_var('Py_GIL_DISABLED'))}))"]));
 const pythonVersion=pythonInfo.version;
 if (!/^uv 0\.13\.1(?:\s|$)/.test(uvVersion) || pythonVersion!=='3.15.0' || pythonInfo.implementation!=='CPython' || pythonInfo.free_threaded) fail('configured_tool_version_invalid');
 const recipe={schema_version:1,owner_id:'bootstrap_service',owner_kind:'service',
  sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],
  contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],
  patterns:['api.owner-http.v1','auth.service-owner.v1','errors.safe-envelope.v1','saving.none.v1'],
  extensions:[],deployment_manifest:'services/bootstrap-service/deployment/manifest.json'};
 const files=renderService(recipe,root);
 // Refuse redirected fixed-parent components; never adopt any previous run.
 let current=root;
 for (const segment of relative(root,parent).split('/')) {
  current=join(current,segment);
  if (!existsSync(current)) mkdirSync(current,{mode:0o700});
  if (lstatSync(current).isSymbolicLink() || !lstatSync(current).isDirectory()) fail('proof_parent_invalid');
 }
 proof=mkdtempSync(join(parent,'proof-')); chmodSync(proof,0o700);
 const output=join(proof,'output'); mkdirSync(output,{mode:0o700});
 manifest={schema_version:1,bootstrap_only:true,generation_ready:false,status:'incomplete',
  recipe,recipe_sha256:hash(JSON.stringify(recipe)),template_version:'service-v1-candidate',
  tool_versions:{uv:uvVersion,python:pythonVersion,node:process.version},
  configured_tools:{uv,python,cache},qualification_host:{platform:process.platform,architecture:process.arch},sources:{},files:{},commands:[],environments:[]};
 for(const {record,log} of preflight) {
  manifest.commands.push(record);
  writeFileSync(join(proof,`${record.label}.log`),log,{mode:0o600});
 }
 const sources=['src/recipe.ts','src/service-renderer.ts','scripts/test-generation.mjs','scripts/process-runner.mjs','package.json',
  ...Object.keys(files).map(path=>`templates/service/${path}`)];
 for (const path of sources) manifest.sources[`platform/builder-cli/${path}`]=hash(readFileSync(join(builder,path)));
 for (const path of [...recipe.sources,...recipe.contracts]) manifest.sources[path]=hash(readFileSync(join(root,path)));
 for (const [path,file] of Object.entries(files)) {
  mkdirSync(dirname(join(output,path)),{recursive:true,mode:0o700});
  writeFileSync(join(output,path),file.content,{mode:0o600});
  manifest.files[path]={classification:file.classification,sha256:hash(file.content)};
 }
 persist();
 const uvEnv={...clean,UV_CACHE_DIR:cache};
 const common=['--project',output,'--python',python,'--offline','--no-config','--no-python-downloads','--default-index','https://pypi.org/simple'];
 run('lock',uv,['lock',...common],uvEnv,output);
 manifest.files['uv.lock']={classification:'generated',sha256:hash(readFileSync(join(output,'uv.lock')))};
 manifest.lock_provenance={owner:'uv 0.13.1',command_label:'lock',independently_resolved:true,offline:true};
 persist();
 run('lock-check',uv,['lock','--check',...common],uvEnv,output);
 const checkHashes=()=>{
  for(const [path,file] of Object.entries(manifest.files)) {
   if(hash(readFileSync(join(output,path)))!==file.sha256) fail('source_or_lock_drift');
  }
  for(const [path,digest] of Object.entries(manifest.sources)) {
   if(hash(readFileSync(join(root,path)))!==digest) fail('builder_source_drift');
  }
 };
 for(const name of ['first','second']) {
  const environment=join(proof,name,'venv');
  if(existsSync(environment)) fail('environment_not_absent');
  run(`${name}-sync`,uv,['sync','--frozen','--no-build','--no-install-project','--group','test','--link-mode','copy',...common],{...uvEnv,UV_PROJECT_ENVIRONMENT:environment},output);
  const interpreter=join(environment,'bin/python');
  run(`${name}-runtime`,interpreter,['-I','-B','-m','pytest','-q','-s','--tb=no','-p','no:cacheprovider','-c',join(output,'pyproject.toml'),'--confcutdir',output,'--basetemp',join(proof,name,'pytest-tmp'),join(output,'tests')],{...clean,PYTEST_DISABLE_PLUGIN_AUTOLOAD:'1'},output);
  checkHashes();
  manifest.environments.push({name,environment,frozen_offline_wheel_only:true,runtime_verified:true,source_lock_unchanged:true});
  persist();
 }
 manifest.status='passed'; persist();
 process.stdout.write(JSON.stringify({bootstrap_only:true,generation_ready:false,status:'passed',proof})+'\n');
} catch(error) {
 const known=new Set(['configured_tool_invalid','configured_cache_invalid','configured_tool_version_invalid','arguments_invalid','bootstrap_stage_failed','proof_parent_invalid','environment_not_absent','source_or_lock_drift','builder_source_drift','service_bootstrap_unsupported']);
 const identifier=known.has(error.message)?error.message:'bootstrap_failed';
 let failureRecordingFailed=false;
 if(manifest) {
  manifest.status='failed';manifest.error=identifier;
  try { persist(); } catch { failureRecordingFailed=true; }
 }
 process.stdout.write(JSON.stringify({error:identifier,bootstrap_only:true,generation_ready:false,...(proof?{proof}:{}),
  ...(failureRecordingFailed?{failure_recording_failed:true}:{})})+'\n');
 process.exitCode=1;
}
