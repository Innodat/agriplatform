import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { stopOwnedApi, presentationRequestFailure, presentationResponseFailure } from '../templates/application/web/scripts/proof-support.mjs';
test('presentational guard rejects successful same-origin Auth fetch/XHR mutation',()=>{
 const origin='http://127.0.0.1:5188';
 for(const type of ['fetch','xhr']) {
  const mutation={url:()=>`${origin}/auth/session`,resourceType:()=>type};
  assert.equal(presentationRequestFailure(mutation,origin),'business_request');
  assert.equal(presentationResponseFailure({status:()=>200}),null);
 }
 assert.equal(presentationRequestFailure({url:()=>`${origin}/assets/main.js`,resourceType:()=> 'script'},origin),null);
 assert.equal(presentationRequestFailure({url:()=> 'https://external.invalid/main.js',resourceType:()=> 'script'},origin),'external_request');
 for(const status of [400,404,500]) assert.equal(presentationResponseFailure({status:()=>status}),'http_failure');
});
async function child(code) {
 const processChild=spawn(process.execPath,['-e',code],{stdio:['ignore','pipe','ignore']});
 await once(processChild.stdout,'data');return processChild;
}
test('owned API cleanup confirms ordinary TERM without forcing or group signals',async()=>{
 const api=await child("console.log('ready');setInterval(()=>{},1000)");
 try {const evidence=await stopOwnedApi(api);assert.equal(evidence.exit_confirmed,true);assert.equal(evidence.term_sent,true);assert.equal(evidence.forced,false);assert.equal(evidence.kill_sent,false);assert.equal(evidence.signal,'SIGTERM');}
 finally {if(api.exitCode===null&&api.signalCode===null) api.kill('SIGKILL');}
});
test('owned API cleanup bounds ignored TERM and awaits forced KILL confirmation',async()=>{
 const api=await child("process.on('SIGTERM',()=>{});console.log('ready');setInterval(()=>{},1000)");
 try {const evidence=await stopOwnedApi(api);assert.equal(evidence.term_sent,true);assert.equal(evidence.forced,true);assert.equal(evidence.kill_sent,true);assert.equal(evidence.exit_confirmed,true);assert.equal(evidence.signal,'SIGKILL');assert.equal(api.signalCode,'SIGKILL');}
 finally {if(api.exitCode===null&&api.signalCode===null) api.kill('SIGKILL');}
});
