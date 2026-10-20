// Internal candidate bootstrap only. No public generation command or supplied output.
import { runBounded } from './process-runner.mjs';
import { qualifyWebDependencies, recordInstallationManifests, verifyInstallationManifests } from './application-dependency-proof.mjs';
import { installScaffold, checkScaffold } from '../src/scaffold-install.ts';
import { renderApplication } from '../src/application-renderer.ts';
import { createHash } from 'node:crypto';
import { accessSync, constants, chmodSync, cpSync, existsSync, globSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const builder=join(root,'platform/builder-cli'), parent=join(root,'platform/deployment/.local/scaffold-application');
const clean={PATH:'/usr/bin:/bin',LC_ALL:'C.UTF-8',CI:'1'};
const hash=value=>createHash('sha256').update(value).digest('hex');
const digest=path=>hash(readFileSync(path));
const fail=identifier=>{throw new Error(identifier);};
let proof,manifest;
const preflight=[];
function safePath(path,kind) {
 if(!isAbsolute(path)) fail('configured_path_invalid');
 let current='/';
 for(const segment of path.split('/').filter(Boolean)) {
  current=join(current,segment);
  if(lstatSync(current).isSymbolicLink()) fail('configured_path_invalid');
 }
 const stat=lstatSync(path);
 if(kind==='file'?!stat.isFile():!stat.isDirectory()) fail('configured_path_invalid');
 return path;
}
function tool(name,executable=true) {
 const path=process.env[name]; if(!path||!isAbsolute(path)||!existsSync(path)) fail('configured_tool_invalid');
 const actual=realpathSync(path); safePath(actual,'file'); if(executable) accessSync(actual,constants.X_OK); return actual;
}
function cache(name) {const path=process.env[name];if(!path||!isAbsolute(path)||!existsSync(path)) fail('configured_cache_invalid');return safePath(path,'directory');}
function persist() {if(manifest) writeFileSync(join(proof,'proof.json'),JSON.stringify(manifest,null,2)+'\n',{mode:0o600});}
function run(label,executable,args,env=clean,cwd=builder,timeoutMs=120000,expectedFailure) {
 const result=runBounded(executable,args,{cwd,env,timeoutMs});
 const log=(result.stdout??'')+(result.stderr??'');
 const record={label,command:[executable,...args],cwd,environment:env,exit_code:result.status,signal:result.signal,error_code:result.error?.code??null,group_termination:result.groupTermination,log_sha256:hash(log)};
 if(manifest) {manifest.commands.push(record);writeFileSync(join(proof,`${label}.log`),log,{mode:0o600});persist();} else preflight.push({record,log});
 if(expectedFailure) {if(result.error||result.status===0||!log.includes(expectedFailure)) fail('expected_failure_missing');record.expected_failure=expectedFailure;persist();} else if(result.error||result.status!==0) fail('bootstrap_stage_failed');return log.trim();
}
try {
 if(process.argv.length!==2) fail('arguments_invalid');
 const npm=tool('SCAFFOLD_NPM',false),uv=tool('SCAFFOLD_UV'),python=tool('SCAFFOLD_PYTHON'),chromium=tool('SCAFFOLD_CHROMIUM');
 const npmCache=cache('SCAFFOLD_NPM_CACHE'),pythonCache=cache('UV_CACHE_DIR');
 const node=realpathSync(process.execPath);
 const npmVersion=run('npm-version',node,[npm,'--version']);
 const uvVersion=run('uv-version',uv,['--version']);
 const pythonInfo=JSON.parse(run('python-version',python,['-I','-B','-c',"import json,platform,sys,sysconfig;print(json.dumps({'version':platform.python_version(),'implementation':platform.python_implementation(),'free_threaded':bool(sysconfig.get_config_var('Py_GIL_DISABLED')),'executable':sys.executable}))"]));
 const browserVersion=run('chromium-version',chromium,['--version']);
 if(process.version!=='v26.11.1'||npmVersion!=='12.2.0'||!/^uv 0\.13\.1(?:\s|$)/.test(uvVersion)||pythonInfo.version!=='3.15.0'||pythonInfo.implementation!=='CPython'||pythonInfo.free_threaded||realpathSync(pythonInfo.executable)!==realpathSync(python)||!/^(?:Chromium|Google Chrome for Testing) \d+\./.test(browserVersion)) fail('configured_tool_version_invalid');
 const recipe={schema_version:1,owner_id:'bootstrap_application',owner_kind:'application',sources:['platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md'],contracts:['platform/docs/architecture/contracts/scaffold-environment-and-generation.md'],patterns:['api.owner-http.v1','web.react-shell.v1','auth.organization-account.fixed.v1','errors.safe-envelope.v1','saving.none.v1'],extensions:[],deployment_manifest:'apps/bootstrap-application/deployment/manifest.json'};
 const files=renderApplication(recipe,root);
 let current=root;
 for(const segment of relative(root,parent).split('/')) {current=join(current,segment);if(!existsSync(current)) mkdirSync(current,{mode:0o700});safePath(current,'directory');}
 proof=mkdtempSync(join(parent,'proof-'));chmodSync(proof,0o700);
 const copy=join(proof,'root'),appRelative='apps/bootstrap-application',webRelative=`${appRelative}/web`,app=join(copy,appRelative),web=join(app,'web'),api=join(app,'api');
 mkdirSync(copy,{mode:0o700});
 const extensionSource=join(proof,'extension-source');mkdirSync(extensionSource,{mode:0o700});
 const initialExtension={
  'message.ts':"export const importedMessage = 'Initial extension import.';\n",
  'obsolete.ts':"export const obsolete = 'Initial owner file.';\n",
 };
 for(const [path,content] of Object.entries(initialExtension)) writeFileSync(join(extensionSource,path),content,{mode:0o600});
 recipe.extensions.push({source:relative(root,extensionSource),destination:'web/src/custom'});
 manifest={schema_version:1,bootstrap_only:true,generation_ready:false,status:'incomplete',template_version:'application-v1-candidate',recipe,recipe_sha256:hash(JSON.stringify(recipe)),qualification_host:{platform:process.platform,architecture:process.arch},sources:{},files:{},commands:[],tools:{},tool_versions:{node:process.version,npm:npmVersion,uv:uvVersion,python:pythonInfo.version,chromium:browserVersion}};
 for(const [name,path] of Object.entries({node,npm,uv,python,chromium})) manifest.tools[name]={path,realpath:realpathSync(path),sha256:digest(path)};
 for(const {record,log} of preflight) {manifest.commands.push(record);writeFileSync(join(proof,`${record.label}.log`),log,{mode:0o600});}
 persist();
 function source(path) {safePath(join(root,path),'file');manifest.sources[path]=digest(join(root,path));return readFileSync(join(root,path));}
 function copyManifest(path) {const content=source(path);mkdirSync(dirname(join(copy,path)),{recursive:true,mode:0o700});writeFileSync(join(copy,path),content,{mode:0o600});return JSON.parse(content);}
 const rootPackage=copyManifest('package.json');copyManifest('package-lock.json');
 const workspaces=[...new Set(rootPackage.workspaces.flatMap(pattern=>globSync(`${pattern}/package.json`,{cwd:root})))].sort();
 // Copy canonical workspace manifests at their original relative paths. Local file
 // dependencies must target another copied workspace; no links back into checkout.
 for(const path of workspaces) copyManifest(path);
 // Copy the existing build-time owners; never resolve their source from checkout.
 for(const owner of ['api-client','builder-cli']) for(const path of globSync(`platform/${owner}/src/*`,{cwd:root})) {
  const content=source(path);mkdirSync(dirname(join(copy,path)),{recursive:true,mode:0o700});writeFileSync(join(copy,path),content,{mode:0o600});
 }
 for(const path of workspaces) {
  const pkg=JSON.parse(readFileSync(join(copy,path)));
  for(const group of ['dependencies','devDependencies','optionalDependencies']) for(const value of Object.values(pkg[group]??{})) {
   if(value.startsWith('file:')) {
    const target=resolve(dirname(join(root,path)),value.slice(5));
    if(!workspaces.some(candidate=>dirname(join(root,candidate))===target)) fail('workspace_dependency_unsupported');
   }
  }
 }
 rootPackage.workspaces.push(webRelative);
 writeFileSync(join(copy,'package.json'),JSON.stringify(rootPackage,null,2)+'\n',{mode:0o600});
 manifest.root_lock={source:'package-lock.json',base_sha256:manifest.sources['package-lock.json'],workspaces,installation_workspace:webRelative,installation_scope:'selected generated web workspace only',extended_by:'npm 12.2.0 offline package-lock-only'};
 const installIdentity={generator:'builder-v1',template:'application-v1-candidate',recipe:hash(JSON.stringify(recipe)),source:hash(JSON.stringify(files))};
 const importInput={repositoryRoot:root,declarations:recipe.extensions};
 installScaffold(app,files,installIdentity,undefined,importInput);
 const customPath=join(app,'web/src/App.tsx');
 const customShell="import { importedMessage } from './custom/message';\n"+readFileSync(customPath,'utf8').replace('Your application starts here.', '{importedMessage}');
 if(!customShell.includes('<p>{importedMessage}</p>')) fail('extension_proof_failed');
 writeFileSync(customPath,customShell,{mode:0o600});
 const expectedText='Imported owner customization preserved.';
 writeFileSync(join(app,'web/src/custom/message.ts'),`export const importedMessage = '${expectedText}';\n`,{mode:0o600});
 // This new synthetic import is owner-maintained: edits, additions and deletion survive.
 rmSync(join(app,'web/src/custom/obsolete.ts'));
 writeFileSync(join(app,'web/src/custom/owner-added.ts'),"export const ownerAdded = 'Owner addition.';\n",{mode:0o600});
 writeFileSync(join(app,'custom-owner.txt'),'Synthetic application-owned custom file.\n',{mode:0o600});
 const preserved=Object.fromEntries(['web/src/App.tsx','web/src/custom/message.ts','web/src/custom/owner-added.ts','custom-owner.txt'].map(path=>[path,digest(join(app,path))]));
 // Keep the original synthetic artifact, but make its declared location unavailable.
 writeFileSync(join(extensionSource,'message.ts'),"export const importedMessage = 'Changed upstream source.';\n",{mode:0o600});
 writeFileSync(join(extensionSource,'upstream-added.ts'),"export const upstreamAdded = 'Do not recopy.';\n",{mode:0o600});
 renameSync(extensionSource,join(proof,'extension-source-retained'));
 installScaffold(app,renderApplication({...recipe,extensions:[]},root),installIdentity,undefined,importInput);
 checkScaffold(app);
 for(const [path,before] of Object.entries(preserved)) if(digest(join(app,path))!==before) fail('extension_proof_failed');
 const absent=['web/src/custom/obsolete.ts','web/src/custom/upstream-added.ts'];
 if(existsSync(extensionSource)||absent.some(path=>existsSync(join(app,path)))) fail('extension_proof_failed');
 manifest.preservation={status:'passed',identity:installIdentity,custom_files:preserved,manifest_sha256:digest(join(app,'.generated-files.json'))};
 manifest.extensions={status:'passed',initial_source_files:Object.fromEntries(Object.entries(initialExtension).map(([path,content])=>[path,hash(content)])),owner_files:preserved,absent,original_source_unavailable:true,ownership:JSON.parse(readFileSync(join(app,'.generated-files.json'))).extensions};
 for(const [path,sha256] of Object.entries(preserved)) if(!files[path]) manifest.files[`${appRelative}/${path}`]={classification:'custom',sha256};
 manifest.files[`${appRelative}/.generated-files.json`]={classification:'ownership-manifest',sha256:manifest.preservation.manifest_sha256};
 for(const [path,file] of Object.entries(files)) {
  manifest.files[`${appRelative}/${path}`]={classification:file.classification,sha256:digest(join(app,path))};
  const template=path.startsWith('api/')?`templates/service/${path.slice(4)}`:`templates/application/${path}`;
  source(`platform/builder-cli/${template}`);
 }
 for(const path of ['src/scaffold-install.ts','tests/scaffold-extensions.test.mjs','tests/scaffold-preservation.test.mjs','src/recipe.ts','src/application-renderer.ts','src/service-renderer.ts','scripts/test-generation-application.mjs','scripts/process-runner.mjs','scripts/application-dependency-proof.mjs','package.json']) source(`platform/builder-cli/${path}`);
 for(const path of [...recipe.sources,...recipe.contracts]) source(path);
 manifest.installation_manifests=recordInstallationManifests(copy,['package.json',...workspaces,`${webRelative}/package.json`]);
 const config=join(proof,'config');mkdirSync(config,{mode:0o700});
 for(const kind of ['user','global']) writeFileSync(join(config,kind),'',{mode:0o600});
 const npmEnv={...clean,PATH:`${dirname(node)}:/usr/bin:/bin`,NPM_CONFIG_USERCONFIG:join(config,'user'),NPM_CONFIG_GLOBALCONFIG:join(config,'global'),NPM_CONFIG_CACHE:npmCache,NPM_CONFIG_REGISTRY:'https://registry.npmjs.org/',NPM_CONFIG_AUDIT:'false',NPM_CONFIG_FUND:'false',NPM_CONFIG_FETCH_RETRIES:'0',NPM_CONFIG_FETCH_TIMEOUT:'30000',PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD:'1'};
 persist();
 run('npm-lock',node,[npm,'install','--package-lock-only','--ignore-scripts','--offline','--allow-remote=all'],npmEnv,copy,300000);
 manifest.root_lock.extended_sha256=digest(join(copy,'package-lock.json'));persist();
 run('npm-ci',node,[npm,'ci','--workspace',webRelative,'--include-workspace-root=false','--ignore-scripts','--offline','--allow-remote=all'],npmEnv,copy,300000);
 if(digest(join(copy,'package-lock.json'))!==manifest.root_lock.extended_sha256) fail('source_or_lock_drift');
 manifest.web_dependencies=qualifyWebDependencies(web,copy);persist();
 checkScaffold(app);

 const uvEnv={...clean,UV_CACHE_DIR:pythonCache};
 const common=['--project',api,'--python',python,'--offline','--no-config','--no-python-downloads','--default-index','https://pypi.org/simple'];
 run('api-lock',uv,['lock',...common],uvEnv,api);
 manifest.files[`${appRelative}/api/uv.lock`]={classification:'generated',sha256:digest(join(api,'uv.lock'))};
 manifest.python_lock={owner:'uv 0.13.1',independently_resolved:true,offline:true};persist();
 run('api-lock-check',uv,['lock','--check',...common],uvEnv,api);
 const environment=join(proof,'python','venv');
 run('api-sync',uv,['sync','--frozen','--no-build','--no-install-project','--group','test','--link-mode','copy',...common],{...uvEnv,UV_PROJECT_ENVIRONMENT:environment},api);
 const interpreter=join(environment,'bin/python');
 run('api-tests',interpreter,['-I','-B','-m','pytest','-q','-s','--tb=no','-p','no:cacheprovider','-c',join(api,'pyproject.toml'),'--confcutdir',api,'--basetemp',join(proof,'python','pytest-tmp'),join(api,'tests')],{...clean,PYTEST_DISABLE_PLUGIN_AUTOLOAD:'1'},api);
 manifest.python_environment={path:environment,frozen_offline_wheel_only:true,runtime_verified:true};persist();
 // Owner export -> upstream types -> real owner client. Each command uses the fresh installation.
 run('api-export',interpreter,['-I','-B','-c',"import sys;sys.path.insert(0,sys.argv.pop(1));import export_openapi;raise SystemExit(export_openapi.main())",api],clean,api);
 run('api-export-check',interpreter,['-I','-B','-c',"import sys;sys.path.insert(0,sys.argv.pop(1));import export_openapi;raise SystemExit(export_openapi.main())",api,'--check'],clean,api);
 run('client-generate',node,[npm,'run','api:generate','--workspace',webRelative],npmEnv,copy);
 run('client-check',node,[npm,'run','api:check','--workspace',webRelative],npmEnv,copy);
 run('client-tests',node,[npm,'run','test:client','--workspace',webRelative],npmEnv,copy);
 run('web-type-check-initial',node,[npm,'run','type-check','--workspace',webRelative],npmEnv,copy);
 const dtoPath=join(api,'main.py'),beforeDto=readFileSync(dtoPath,'utf8');
 if(!beforeDto.includes('class HealthResponse(BaseModel):')) fail('client_proof_failed');
 writeFileSync(dtoPath,beforeDto.replace('class HealthResponse(BaseModel):','class HealthResponse(BaseModel):\n    proof_note: str | None = None'),{mode:0o600});
 const dtoUse=join(web,'src/api/owner-dto-proof.ts');
 writeFileSync(dtoUse,"import type {HealthResponse} from './generated/types.gen';\nexport const proofNote: HealthResponse['proof_note'] = null;\n",{mode:0o600});
 run('api-export-drift',interpreter,['-I','-B','-c',"import sys;sys.path.insert(0,sys.argv.pop(1));import export_openapi;raise SystemExit(export_openapi.main())",api],clean,api);
 run('client-stale-check',node,[npm,'run','api:check','--workspace',webRelative],npmEnv,copy,120000,'api_client_stale');
 run('web-stale-types',node,[npm,'run','type-check','--workspace',webRelative],npmEnv,copy,120000,'proof_note');
 run('client-regenerate',node,[npm,'run','api:generate','--workspace',webRelative],npmEnv,copy);
 run('client-regenerated-check',node,[npm,'run','api:check','--workspace',webRelative],npmEnv,copy);
 for(const script of ['type-check','build']) run(`web-${script}`,node,[npm,'run',script,'--workspace',webRelative],npmEnv,copy);
 // Keep a tampered synthetic copy and its failure; never repair the main proof output.
 const clientRoot=join(web,'src/api/generated'),tampered=join(proof,'tampered-client');cpSync(clientRoot,tampered,{recursive:true});
 writeFileSync(join(tampered,'types.gen.ts'),readFileSync(join(tampered,'types.gen.ts'),'utf8')+'\n// synthetic owner edit\n');
 const tamperedBefore=digest(join(tampered,'types.gen.ts'));
 run('client-tampered-refusal',node,[manifest.web_dependencies.commands['platform-api-client'].path,'--schema',join(api,'openapi.json'),'--output',tampered],npmEnv,copy,120000,'scaffold_conflict');
 if(digest(join(tampered,'types.gen.ts'))!==tamperedBefore) fail('client_proof_failed');
 for(const [path,before] of Object.entries(preserved)) if(digest(join(app,path))!==before) fail('preservation_proof_failed');
 for(const path of ['api/main.py','api/openapi.json','web/src/api/owner-dto-proof.ts',...globSync('web/src/api/generated/*',{cwd:app}), 'web/src/api/generated/.generated-files.json']) manifest.files[`${appRelative}/${path}`]={classification:files[path]?.classification??'generated-client-proof',sha256:digest(join(app,path))};
 manifest.client={status:'passed',owner_dto_changed:true,stale_check_failed:true,stale_types_failed:true,regeneration_passed:true,owner_files_preserved:true,tampered_output_refused:true,tampered_sha256:tamperedBefore};persist();
 run('web-browser',node,[npm,'run','test:browser','--workspace',webRelative],{...npmEnv,SCAFFOLD_CHROMIUM:chromium,SCAFFOLD_API_PYTHON:interpreter,SCAFFOLD_SCREENSHOTS:proof,SCAFFOLD_EXPECTED_TEXT:expectedText},copy);
 manifest.browser=JSON.parse(readFileSync(join(proof,'browser-result.json')));
 if(manifest.browser.unavailability_verified!==true||manifest.browser.health_responses<4||manifest.browser.expected_text_verified!==true||manifest.browser.status!=='passed'||manifest.browser.browser.sha256!==manifest.tools.chromium.sha256||realpathSync(manifest.browser.browser.path)!==realpathSync(chromium)) fail('browser_identity_invalid');
 manifest.evidence={};
 for(const name of ['desktop.png','mobile.png','browser-result.json','browser-cleanup.json']) manifest.evidence[name]={sha256:digest(join(proof,name))};
 for(const [path,digestBefore] of Object.entries(manifest.sources)) if(digest(join(root,path))!==digestBefore) fail('builder_source_drift');
 for(const [path,file] of Object.entries(manifest.files)) if(digest(join(copy,path))!==file.sha256) fail('source_or_lock_drift');
 if(digest(join(copy,'package-lock.json'))!==manifest.root_lock.extended_sha256) fail('source_or_lock_drift');
 verifyInstallationManifests(copy,manifest.installation_manifests);
 if(existsSync(join(web,'package-lock.json'))) fail('nested_lock_invalid');
 manifest.status='passed';persist();
 process.stdout.write(JSON.stringify({bootstrap_only:true,generation_ready:false,status:'passed',proof})+'\n');
} catch(error) {
 const known=new Set(['expected_failure_missing','client_proof_failed','extension_proof_failed','preservation_proof_failed','scaffold_conflict','scaffold_busy','scaffold_recovery_required','configured_tool_invalid','configured_cache_invalid','configured_tool_version_invalid','configured_path_invalid','arguments_invalid','bootstrap_stage_failed','workspace_dependency_unsupported','source_or_lock_drift','builder_source_drift','browser_identity_invalid','nested_lock_invalid','dependency_provenance_invalid','installation_manifest_drift','application_bootstrap_unsupported']);
 const identifier=known.has(error.message)?error.message:'bootstrap_failed';let failureRecordingFailed=false;
 if(manifest) {manifest.status='failed';manifest.error=identifier;try {persist();} catch {failureRecordingFailed=true;}}
 process.stdout.write(JSON.stringify({error:identifier,bootstrap_only:true,generation_ready:false,...(proof?{proof}:{}),...(failureRecordingFailed?{failure_recording_failed:true}:{})})+'\n');process.exitCode=1;
}
