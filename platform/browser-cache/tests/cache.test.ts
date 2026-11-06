import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createJsonCache,withDeadline} from '../src/index.ts';
const storage=()=>{const rows=new Map<string,string>();return {rows,get length(){return rows.size},key:(i:number)=>[...rows.keys()][i]??null,getItem:(k:string)=>rows.get(k)??null,setItem:(k:string,v:string)=>{rows.set(k,v)},removeItem:(k:string)=>{rows.delete(k)}}};
const scope={app:'test',api:'https://api.invalid',account:'a',format:1};
test('scope, version, bounded entries and invalidation reject late writes',()=>{
 const s=storage(),cache=createJsonCache({...scope,storage:s,maxEntries:2});
 const guard=cache.operation();cache.put('/one','W/"1"',{text:'one'},guard);cache.put('/two','W/"2"',{text:'two'},guard);cache.put('/three','W/"3"',{text:'three'},guard);
 assert.equal(cache.get('/one'),null);assert.deepEqual(cache.get('/three')?.value,{text:'three'});
 assert.equal(createJsonCache({...scope,account:'b',storage:s}).get('/three'),null);
 assert.equal(createJsonCache({...scope,format:2,storage:s}).get('/three'),null);
 cache.clear();cache.put('/late','W/"late"',{text:'old'},guard);assert.equal(cache.get('/late'),null);assert.equal(s.length,0);
});
test('corrupt, oversized and unavailable storage falls back to memory',()=>{
 const s=storage(),cache=createJsonCache({...scope,storage:s,maxBytes:500});
 cache.put('/ok','W/"1"',{text:'hello'},cache.operation());
 const key=s.key(0)!;s.setItem(key,'not json');assert.equal(createJsonCache({...scope,storage:s}).get('/ok'),null);
 const broken={...s,getItem:()=>{throw Error('blocked')},setItem:()=>{throw Error('quota')},removeItem:()=>{throw Error('blocked')}};
 const memory=createJsonCache({...scope,storage:broken});memory.put('/ok','W/"1"',{text:'hello'},memory.operation());assert.equal(memory.get('/ok')?.value.text,'hello');
 cache.put('/huge','W/"2"',{text:'x'.repeat(1000)},cache.operation());assert.equal(cache.get('/huge'),null);
});
test('deadline bounds body work even when it ignores abort',async()=>{
 await assert.rejects(withDeadline(async()=>new Promise(()=>{}),{timeoutMs:15}),/timed out/);
 const controller=new AbortController();const task=withDeadline(async()=>new Promise(()=>{}),{signal:controller.signal});controller.abort();await assert.rejects(task,e=>(e as Error).name==='AbortError');
});
test('application decoder rejects corrupt payloads inside valid envelopes',()=>{
 const s=storage(),cache=createJsonCache({...scope,storage:s});cache.put('/ok','W/"1"',{poems:[]},cache.operation());
 const key=s.key(0)!,entry=JSON.parse(s.getItem(key)!);entry.value=null;s.setItem(key,JSON.stringify(entry));
 const guarded=createJsonCache({...scope,storage:s,validate:v=>Boolean(v&&Array.isArray((v as {poems?:unknown}).poems))});
 assert.equal(guarded.get('/ok'),null);assert.equal(s.length,0);
});
test('conditional JSON read waits for authorized response and rejects stale body completion',async()=>{
 const s=storage(),cache=createJsonCache({...scope,storage:s});
 await cache.read('/one',async tag=>{assert.equal(tag,undefined);return new Response(JSON.stringify({text:'one'}),{headers:{ETag:'W/"1"'}})});
 const restored=await cache.read('/one',async tag=>{assert.equal(tag,'W/"1"');return new Response(null,{status:304})});assert.deepEqual(restored,{text:'one'});
 await assert.rejects(cache.read('/one',async()=>new Response(null,{status:403})),/retry/);
 let release:(value:any)=>void=()=>{};const response=new Response();response.json=()=>new Promise(resolve=>{release=resolve});
 const late=cache.read('/late',async()=>response);await new Promise(resolve=>setTimeout(resolve,0));cache.clear();release({text:'old'});await assert.rejects(late,e=>(e as Error).name==='AbortError');assert.equal(cache.get('/late'),null);
});
test('aggregate byte budget evicts older account and format entries',()=>{
 const s=storage(),bytes=()=>[...s.rows.values()].reduce((sum,raw)=>sum+raw.length*2,0);
 const old=createJsonCache({...scope,account:'old',format:0,storage:s,maxEntries:10});
 old.put('/older','W/"old"',{text:'x'.repeat(100)},old.operation());
 const oldKey=s.key(0)!,envelope=JSON.parse(s.getItem(oldKey)!);envelope.written=1;s.setItem(oldKey,JSON.stringify(envelope));
 const oldBytes=bytes();const maxBytes=oldBytes*2+100;
 const current=createJsonCache({...scope,storage:s,maxEntries:10,maxBytes});
 current.put('/one','W/"one"',{text:'x'.repeat(100)},current.operation());
 assert.equal(s.length,2);assert.ok(bytes()<=maxBytes);
 // Both old and new entries fit individually; only their aggregate triggers eviction.
 const oneBytes=bytes()-oldBytes;assert.ok(oldBytes<maxBytes&&oneBytes<maxBytes);
 current.put('/two','W/"two"',{text:'x'.repeat(100)},current.operation());
 assert.equal(s.getItem(oldKey),null);assert.equal(s.length,2);assert.ok(bytes()<=maxBytes);
 assert.deepEqual(current.get('/one')?.value,{text:'x'.repeat(100)});assert.deepEqual(current.get('/two')?.value,{text:'x'.repeat(100)});
 const twoBytes=JSON.stringify(current.get('/two')).length*2;assert.ok(twoBytes<maxBytes&&oldBytes+oneBytes+twoBytes>maxBytes);
 assert.equal(bytes(),oneBytes+twoBytes);
});
