// Synthetic built-file/proxy edges; actual built-browser shell proof is separate.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {mkdtempSync,mkdirSync,writeFileSync,symlinkSync} from 'node:fs';
import {join} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createLocalShellServer} from '../scripts/serve-local-shell.mjs';
async function listen(server){server.listen(0,'127.0.0.1');await once(server,'listening');return 'http://127.0.0.1:'+server.address().port;}
async function stop(server){server.closeAllConnections();await new Promise(r=>server.close(r));}
const parent=join(process.cwd(),'platform/deployment/.local/kdg-local-shell-host');mkdirSync(parent,{recursive:true});
function fixture(apiOrigin='http://127.0.0.1:8188'){
 const proof=mkdtempSync(join(parent,'proof-')),dist=join(proof,'dist'),config=join(proof,'public.json');mkdirSync(dist);mkdirSync(join(dist,'assets'));
 const publicConfig={schema_version:1,environment_kind:'ci_disposable',org_id:'33333333-3333-4333-8333-333333333333',auth_url:'http://127.0.0.1:8189',auth_public_key:'sb_publishable_synthetic_public_123456'};
 writeFileSync(config,JSON.stringify({...publicConfig,api_origin:apiOrigin}));writeFileSync(join(dist,'index.html'),'<script id="kdg-local-config" type="application/json">'+JSON.stringify(publicConfig)+'</script><script src="/assets/index-abcd.js"></script>');writeFileSync(join(dist,'sw.js'),'/* public revision */');writeFileSync(join(dist,'manifest.webmanifest'),'{}');writeFileSync(join(dist,'icon.svg'),'<svg/>');writeFileSync(join(dist,'assets/index-abcd.js'),'export{}');writeFileSync(join(dist,'assets/index-abcd.css'),'body{}');writeFileSync(join(dist,'PRIVATE'),'PRIVATE');
 return {proof,dist,config,publicConfig};
}
test('built shell serves fixed public files and exact API methods without fallback or ambient credentials',async()=>{
 const calls=[];const api=createServer((req,res)=>{const chunks=[];req.on('data',c=>chunks.push(c));req.on('end',()=>{calls.push({url:req.url,method:req.method,headers:req.headers,body:Buffer.concat(chunks).toString()});res.writeHead(200,{'Content-Type':'application/json','Set-Cookie':'PRIVATE=1'});res.end('{"ok":true}');});});const apiOrigin=await listen(api),f=fixture(apiOrigin);const server=createLocalShellServer({dist:f.dist,configFile:f.config}),origin=await listen(server);
 try{
  for(const [path,type]of [['/','text/html'],['/admin','text/html'],['/sw.js','application/javascript'],['/manifest.webmanifest','application/manifest+json'],['/icon.svg','image/svg+xml'],['/assets/index-abcd.js','application/javascript'],['/assets/index-abcd.css','text/css']]){const result=await fetch(origin+path);assert.equal(result.status,200,path);assert.ok(result.headers.get('content-type').startsWith(type));assert.ok(!(await result.text()).includes('api_origin'));}
  assert.equal((await fetch(origin+'/sw.js')).headers.get('cache-control'),'no-store');
  for(const path of ['/PRIVATE','/unknown','/admin/','/assets/../PRIVATE','/@fs'+f.config,'/src/main.ts','/local-host.config.ts','/api/private']){const result=await fetch(origin+path);assert.equal(result.status,404,path);assert.ok(!(await result.text()).includes('PRIVATE'));}
  const write=await fetch(origin+'/api/v1/captures',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer synthetic',Cookie:'PRIVATE=1','X-Service-Key':'PRIVATE'},body:' {"saved":true} '});assert.equal(write.status,200);assert.equal(write.headers.get('set-cookie'),null);assert.equal(calls[0].body,' {"saved":true} ');assert.equal(calls[0].headers.cookie,undefined);assert.equal(calls[0].headers['x-service-key'],undefined);assert.equal(calls[0].headers.authorization,'Bearer synthetic');
  assert.equal((await fetch(origin+'/api/v1/admin/captures',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,405);
  const id='cccccccc-cccc-4ccc-8ccc-cccccccccccc';assert.equal((await fetch(origin+'/api/v1/captures/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:'{}'})).status,200);
  for(const path of ['/api/v1/provision','/api/v1/captures?limit=5','/api/v1/captures/'+id,'/api/v1/captures/'+id+'/edit-context','/api/v1/operations/'+id+'?command_type=capture.create'])assert.equal((await fetch(origin+path)).status,200,path);
  const before=calls.length;assert.equal((await fetch(origin+'/api/v1/captures',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({value:'x'.repeat(131072)})})).status,422);assert.equal(calls.length,before);
 }finally{await stop(server);await stop(api);}
});
test('built shell rejects private inputs in served roots, symlinked assets, mismatching public input and unsafe targets',()=>{
 const f=fixture();assert.throws(()=>createLocalShellServer({dist:'relative',configFile:f.config}),/kdg_local_shell_configuration_invalid/);
 const inside=join(f.dist,'private.json');writeFileSync(inside,'{}');assert.throws(()=>createLocalShellServer({dist:f.dist,configFile:inside}),/kdg_local_shell_configuration_invalid/);
 const link=join(f.dist,'assets/link.js');symlinkSync(f.config,link);assert.throws(()=>createLocalShellServer({dist:f.dist,configFile:f.config}),/kdg_local_shell_configuration_invalid/);
 const other=fixture();writeFileSync(other.config,JSON.stringify({...other.publicConfig,api_origin:'https://remote.invalid'}));assert.throws(()=>createLocalShellServer({dist:other.dist,configFile:other.config}),/kdg_local_shell_configuration_invalid/);
 const mismatch=fixture();writeFileSync(mismatch.config,JSON.stringify({...mismatch.publicConfig,org_id:'11111111-1111-4111-8111-111111111111',api_origin:'http://127.0.0.1:8188'}));assert.throws(()=>createLocalShellServer({dist:mismatch.dist,configFile:mismatch.config}),/kdg_local_shell_configuration_invalid/);
});

test('built shell CLI validates fixed loopback port, emits only readiness and stops normally',async()=>{
 const f=fixture(),script=fileURLToPath(new URL('../scripts/serve-local-shell.mjs',import.meta.url)),baseEnv={PATH:'/usr/bin:/bin',KDG_LOCAL_WEB_CONFIG:f.config,KDG_LOCAL_SHELL_DIST:f.dist};
 for(const port of ['-1','65536','01','PRIVATE']){const run=spawnSync(process.execPath,[script],{env:{...baseEnv,KDG_LOCAL_SHELL_PORT:port},encoding:'utf8',timeout:3000});assert.equal(run.status,1);assert.equal(run.stdout,'');assert.equal(run.stderr.trim(),'kdg_local_shell_configuration_invalid');}
 const child=spawn(process.execPath,[script],{env:{...baseEnv,KDG_LOCAL_SHELL_PORT:'0'},stdio:['ignore','pipe','pipe']});let output='',errors='';child.stderr.on('data',chunk=>errors+=chunk);
 try{
  const ready=await new Promise((resolve,reject)=>{const deadline=setTimeout(()=>reject(Error('shell_ready_timeout')),3000);child.once('error',reject);child.stdout.on('data',chunk=>{output+=chunk;if(output.includes('\n')){clearTimeout(deadline);try{resolve(JSON.parse(output.trim()));}catch(error){reject(error);}}});});
  assert.equal(ready.kind,'kdg_local_shell_ready');assert.match(ready.origin,/^http:\/\/127\.0\.0\.1:[1-9][0-9]*$/);assert.equal((await fetch(ready.origin)).status,200);
  const exit=once(child,'exit');child.kill('SIGTERM');const [code,signal]=await exit;assert.equal(code,0);assert.equal(signal,null);assert.equal(errors,'');assert.ok(!output.includes('api_origin')&&!output.includes('sb_publishable'));
 }finally{if(child.exitCode===null&&child.signalCode===null){const exit=once(child,'exit');child.kill('SIGTERM');await exit;}}
});
