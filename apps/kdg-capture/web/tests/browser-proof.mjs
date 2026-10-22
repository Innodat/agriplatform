// Synthetic native-browser consumer proof. This is not the product entry screen.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createRequire} from 'node:module';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
const root=process.cwd(),hash=data=>createHash('sha256').update(data).digest('hex');
assert.equal(process.version,'v26.11.1');
assert.equal(JSON.parse(readFileSync(join(root,'node_modules/typescript/package.json'))).version,'7.0.2');
const retained=join(root,'platform/deployment/.local/scaffold-application/proof-dI2Gy9/root');
const require=createRequire(join(retained,'package.json'));
assert.equal(require('@playwright/test/package.json').version,'1.64.0');
const {chromium}=require('@playwright/test');
const executable=join(root,'platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell');
const proof=join(root,'platform/deployment/.local/kdg-browser-entry-20261022','browser-'+randomUUID());
mkdirSync(proof,{mode:0o700});
const sources=['apps/kdg-capture/web/src/entry.ts','apps/kdg-capture/web/tests/entry.test.mjs','apps/kdg-capture/web/tests/entry.types.ts','apps/kdg-capture/web/tests/browser-proof.mjs',
 'apps/kdg-capture/web/tsconfig.json','apps/kdg-capture/web/package.json','apps/kdg-capture/contracts/generated/types.gen.ts'];
const captured=Object.fromEntries(sources.map(path=>{
 const data=readFileSync(join(root,path));const destination=join(proof,'sources',path);
 mkdirSync(resolve(destination,'..'),{recursive:true});writeFileSync(destination,data);return[path,hash(data)];
}));
const compiler=spawnSync(process.execPath,[join(root,'node_modules/typescript/bin/tsc'),'--project','apps/kdg-capture/web/tsconfig.json',
 '--noEmit','false','--rootDir','apps/kdg-capture','--outDir',join(proof,'compiled')],{cwd:root,encoding:'utf8',timeout:30000});
writeFileSync(join(proof,'compiler.log'),compiler.stdout+compiler.stderr);assert.equal(compiler.status,0,'compiler_failed');
const script=readFileSync(join(proof,'compiled/web/src/entry.js'));
const A='11111111-1111-4111-8111-111111111111',B='22222222-2222-4222-8222-222222222222',ORG='33333333-3333-4333-8333-333333333333';
let mode='success',requests=0;const sockets=new Set();
const document=`<!doctype html><html><meta charset="utf-8"><title>Synthetic entry boundary</title><output id="state">signed_out</output><script type="module">
import {createEntryBoundary,getCurrentContext} from '/entry.js';
const session=account=>({account_id:account,access_token:'synthetic-'+account});
const gate=createEntryBoundary('${ORG}',state=>document.getElementById('state').textContent=state.kind);
window.fixture={check:account=>gate.check(session(account)),clear:()=>gate.clear(),state:()=>gate.state().kind,
  bounded:account=>getCurrentContext(session(account),'${ORG}',{timeoutMs:30})};
</script></html>`;
const server=createServer((request,response)=>{
 response.setHeader('Cache-Control','private, no-store');
 if(request.url==='/') {response.setHeader('Content-Type','text/html');response.end(document);return;}
 if(request.url==='/entry.js') {response.setHeader('Content-Type','text/javascript');response.end(script);return;}
 if(request.url!=='/api/v1/context') {response.writeHead(404).end();return;}
 assert.equal(request.method,'GET');assert.equal(request.headers['x-service-key'],undefined);requests++;
 const account=request.headers.authorization==='Bearer synthetic-'+A?A:B;
 const selected=mode;
 const send=()=>{
  response.setHeader('Content-Type','application/json');
  if(selected==='denied') {response.writeHead(403).end(JSON.stringify({error_id:'access_denied',error:'SENSITIVE'}));return;}
  if(selected==='outage') {response.writeHead(503).end(JSON.stringify({error_id:'authorization_unavailable',error:'SENSITIVE'}));return;}
  const value={account_id:account,actor_id:'44444444-4444-4444-8444-444444444444',membership_id:'9007199254740993',
   permission:'kdg_capture.capture.read.own',authorization_scope:{kind:'organization',org_id:ORG},resource_scope:{kind:'own_account',account_id:account},
   decision_id:randomUUID(),checked_at:new Date().toISOString()};
  response.end(JSON.stringify(value));
 };
 if(selected==='delay')setTimeout(send,200);else send();
});
server.on('connection',socket=>{sockets.add(socket);socket.once('close',()=>sockets.delete(socket));});
let browser;let passed=false;const checks=[];const errors=[];const failedResponses=[];
try {
 server.listen(0,'127.0.0.1');await once(server,'listening');
 browser=await chromium.launch({executablePath:executable,headless:true});
 const page=await browser.newPage();page.on('pageerror',()=>errors.push({event:'page_error'}));
 page.on('response',response=>{if(!response.ok())failedResponses.push({path:new URL(response.url()).pathname,status:response.status()});});
 page.on('console',message=>{if(message.type()==='error'){let path='<unknown>';try{path=new URL(message.location().url).pathname;}catch{}errors.push({event:'console_error',path});}});
 await page.goto('http://127.0.0.1:'+server.address().port);await page.waitForFunction(()=>Boolean(window.fixture));
 assert.equal(await page.evaluate(async account=>(await window.fixture.check(account)).kind,A),'authorized');checks.push('authorized_native_fetch');
 assert.equal(await page.evaluate(()=>window.fixture.state()),'authorized');
 mode='delay';await page.evaluate(account=>{void window.fixture.check(account);},A);
 assert.equal(await page.locator('#state').textContent(),'checking');
 await page.evaluate(()=>window.fixture.clear());await page.waitForTimeout(250);
 assert.equal(await page.locator('#state').textContent(),'signed_out');checks.push('logout_blocks_late_completion');
 mode='success';assert.equal(await page.evaluate(async account=>(await window.fixture.check(account)).context.account_id,B),B);checks.push('new_account_only');
 mode='denied';assert.equal(await page.evaluate(async account=>(await window.fixture.check(account)).kind,B),'access_denied');checks.push('denial');
 mode='outage';assert.equal(await page.evaluate(async account=>(await window.fixture.check(account)).kind,B),'authorization_unavailable');checks.push('outage');
 mode='delay';assert.equal(await page.evaluate(async account=>(await window.fixture.bounded(account)).kind,B),'authorization_unavailable');checks.push('native_deadline');
 assert.deepEqual(await page.evaluate(()=>[localStorage.length,sessionStorage.length]),[0,0]);checks.push('no_browser_storage');
 assert.ok(!(await page.content()).includes('SENSITIVE'));assert.deepEqual(failedResponses,[{path:'/api/v1/context',status:403},{path:'/api/v1/context',status:503}]);
 assert.ok(errors.length===2 && errors.every(error=>error.event==='console_error'&&error.path==='/api/v1/context'),'unexpected_browser_error');
 assert.ok(requests>=6);
 assert.ok(sources.every(path=>hash(readFileSync(join(root,path)))===captured[path]));passed=true;
} finally {
 if(browser)await browser.close();
 const closed=new Promise(resolve=>server.close(resolve));for(const socket of sockets)socket.destroy();await closed;
 const result={passed,checks,requests,source_sha256:captured,compiled_sha256:hash(script),
  chromium_sha256:hash(readFileSync(executable)),node:process.version,typescript:'7.0.2',playwright:'1.64.0',
  server_stopped:!server.listening,expected_failure_responses:failedResponses,browser_errors:errors,limitations:['synthetic HTTP API and Auth session fixtures','not product UI/provider/current SQL proof'],proof};
 writeFileSync(join(proof,'result.json'),JSON.stringify(result,null,2)+'\n');
 process.stdout.write(JSON.stringify({passed,proof})+'\n');
}
