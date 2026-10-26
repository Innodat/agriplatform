import assert from 'node:assert/strict';
import {test} from 'node:test';
import {EventEmitter} from 'node:events';
import {watchChild,readyChild,stopChild} from './persistence-child.mjs';
const fake=()=>{const child=new EventEmitter();child.stdout=new EventEmitter();child.kill=()=>{};return child;};
test('spawn error is consumed and readiness rejects for a failed proof record',async()=>{
 const child=fake(),owner=watchChild(child),ready=readyChild(child,owner,100);
 child.emit('error',Error('synthetic spawn failure'));
 await assert.rejects(ready,/fixture_spawn_error/);
 const record={passed:false,child:owner.state,...await stopChild(child,owner)};
 assert.deepEqual(record,{passed:false,child:{exited:true,code:null,signal:null,spawn_error:true},forced_stop:false,stop_signal:null,shutdown_failed:false});
});
test('hung shutdown fetch is inside original deadline and owned fallback is recorded',async()=>{
 const child=fake(),owner=watchChild(child),signals=[];let aborted=false;
 child.kill=signal=>{signals.push(signal);child.emit('exit',null,signal);};
 const result=await stopChild(child,owner,'http://127.0.0.1:1',{request:async(_url,init)=>{init.signal.addEventListener('abort',()=>{aborted=true;});return new Promise(()=>{});},timeoutMs:5,fallbackMs:5});
 assert.deepEqual(signals,['SIGTERM']);assert.equal(aborted,true);
 assert.deepEqual(result,{forced_stop:true,stop_signal:'SIGTERM',shutdown_failed:true});assert.equal(owner.state.signal,'SIGTERM');
});
test('unresponsive owned fake child reaches bounded kill fallback without a normal-stop claim',async()=>{
 const child=fake(),owner=watchChild(child),signals=[];
 child.kill=signal=>{signals.push(signal);if(signal==='SIGKILL')child.emit('exit',null,signal);};
 const result=await stopChild(child,owner,'http://127.0.0.1:1',{request:async()=>({ok:true}),timeoutMs:5,fallbackMs:5});
 assert.deepEqual(signals,['SIGTERM','SIGKILL']);assert.equal(result.forced_stop,true);assert.equal(result.stop_signal,'SIGKILL');assert.notEqual(owner.state.code,0);
});
