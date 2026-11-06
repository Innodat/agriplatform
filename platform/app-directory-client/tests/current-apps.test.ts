import test from 'node:test';
import assert from 'node:assert/strict';
import {createAppDirectoryClient,AppDirectoryError} from '../src/index.ts';
const app={id:'pts',name:'PtS',url:'https://machon.io/pts/',icon:'book-open',description:'Poetry',enabled:true};
test('v2 uses current explicit bearer, no-store and validated states',async()=>{
 let call:any;
 const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch:async(url,init)=>{call={url,init};return new Response(JSON.stringify({apps:[app],protected_access_status:'complete'}));}});
 assert.deepEqual((await client.getCurrentApps({token:'current'})).apps,[app]);
 assert.equal(call.url,'https://directory.test/api/v2/me/apps');assert.equal(call.init.cache,'no-store');assert.equal(call.init.headers.Authorization,'Bearer current');
});
test('malformed or inconsistent envelopes clear authority',async()=>{
 for(const body of [{apps:[app],protected_access_status:'unavailable'},{apps:[],protected_access_status:'unknown'},{apps:[app,app],protected_access_status:'complete'}]){
  const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch:async()=>new Response(JSON.stringify(body))});
  await assert.rejects(client.getCurrentApps(),e=>e instanceof AppDirectoryError&&e.errorId==='discovery_unavailable');
 }
});
test('typed errors depend on identifiers/status and never echo upstream text',async()=>{
 const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch:async()=>new Response(JSON.stringify({error:'secret-token',error_id:'authentication_required',details:{token:'private'}}),{status:401})});
 await assert.rejects(client.getCurrentApps(),e=>e instanceof AppDirectoryError&&e.errorId==='authentication_required'&&!e.message.includes('secret'));
});
test('deadline bounds transports ignoring abort and body stalls',async()=>{
 for(const fetch of [async()=>new Promise<Response>(()=>{}),async()=>new Response(new ReadableStream({start(){}}))]){
  const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch,timeoutMs:20});
  await assert.rejects(client.getCurrentApps(),e=>e instanceof AppDirectoryError&&e.errorId==='discovery_unavailable');
 }
});
test('caller cancellation rejects even if transport ignores abort',async()=>{
 const controller=new AbortController();const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch:async()=>new Promise<Response>(()=>{})});
 const pending=client.getCurrentApps({signal:controller.signal});controller.abort();
 await assert.rejects(pending,e=>e instanceof AppDirectoryError&&e.errorId==='request_cancelled');
});
test('catalogue URL policy agrees with Directory for every shared case',async()=>{
 const {readFileSync}=await import('node:fs');
 const cases=JSON.parse(readFileSync(new URL('../../../services/app-directory/tests/fixtures/catalogue-urls.json',import.meta.url),'utf8'));
 for(const [url,valid] of cases){
  const client=createAppDirectoryClient({baseUrl:'https://directory.test',fetch:async()=>new Response(JSON.stringify({apps:[{...app,url}],protected_access_status:'complete'}))});
  if(valid)assert.equal((await client.getCurrentApps()).apps[0].url,url);
  else await assert.rejects(client.getCurrentApps(),e=>e instanceof AppDirectoryError&&e.errorId==='discovery_unavailable');
 }
});
