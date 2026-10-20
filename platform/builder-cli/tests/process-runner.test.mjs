import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { runBounded } from '../scripts/process-runner.mjs';
const clean={PATH:'/usr/bin:/bin'};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function terminated(pid) {
 try { return readFileSync(`/proc/${pid}/stat`,'utf8').split(' ')[2]==='Z'; }
 catch(error) {if(error.code==='ENOENT') return true; throw error;}
}
test('timeout terminates own synthetic child and grandchild with failure evidence',async()=>{
 const fixture=mkdtempSync('/tmp/scaffold-runner-timeout-');
 const pids=join(fixture,'pids.json');
 const grandchild=join(fixture,'grandchild.mjs');
 writeFileSync(grandchild,'setInterval(()=>{},1000);');
 const child=join(fixture,'child.mjs');
 writeFileSync(child,`import {spawn} from 'node:child_process';
import {writeFileSync} from 'node:fs';
const grandchild=spawn(${JSON.stringify(process.execPath)},[${JSON.stringify(grandchild)}],{stdio:'ignore'});
writeFileSync(${JSON.stringify(pids)},JSON.stringify([process.pid,grandchild.pid]));
setInterval(()=>{},1000);`);
 const result=runBounded(process.execPath,[child],{cwd:fixture,env:clean,timeoutMs:700});
 assert.equal(result.error?.code,'ETIMEDOUT');
 assert.equal(result.status,null);assert.equal(result.signal,'SIGKILL');
 assert.ok(['signalled','already_exited'].includes(result.groupTermination));
 const ownedPids=JSON.parse(readFileSync(pids,'utf8'));
 const deadline=Date.now()+3000;
 while(Date.now()<deadline && !ownedPids.every(terminated)) await pause(25);
 assert.ok(ownedPids.every(terminated),'owned process descendants must stop');
 writeFileSync(join(fixture,'result.json'),JSON.stringify({error_code:result.error.code,status:result.status,signal:result.signal,group_termination:result.groupTermination,owned_pids:ownedPids,terminated:true},null,2));
});
