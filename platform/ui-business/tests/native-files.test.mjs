import test from 'node:test';
import assert from 'node:assert/strict';
import {createNativeFileClient} from '../src/files/native-file-client.ts';

const fileOrigin='https://files.owner.example.test';
const frontendOrigin='https://owner.example.test';
const identity={token:'current-access-credential'};
const context='11111111-1111-4111-8111-111111111111';
test('native transport sends a credentialed POST and accepts only its owner context',async()=>{
 const seen=[];const client=createNativeFileClient({fileOrigin,frontendOrigin,fetch:async(url,options)=>{
  seen.push([url,options]);return new Response(JSON.stringify(url.includes('/file-contexts/')?{url:fileOrigin+'/api/files/'+context}:url.endsWith('/clear')?{status:'cleared',provider_session:'absent',account_id:context,session_id:context}:{status:'ready'}),{status:200,headers:{'Content-Type':'application/json'}});
 }});
 await client.establish(identity);assert.equal(await client.context('stored source','download',identity),fileOrigin+'/api/files/'+context);await client.clear(identity);
 assert.deepEqual(seen.map(([url])=>url),[fileOrigin+'/api/file-session',fileOrigin+'/api/file-contexts/stored%20source?presentation=download',fileOrigin+'/api/file-session/clear']);
 for(const [url,options] of seen){assert.equal(options.method,'POST');assert.equal(options.credentials,'include');assert.equal(options.headers.Authorization,'Bearer '+identity.token);assert.equal(options.cache,'no-store');assert(!url.includes(identity.token));assert(options.signal);}
});
test('transport refuses another site, origin, path, query or fragment as a native context',async()=>{
 for(const file of ['http://files.owner.example.test','https://foreign.test','https://files.owner.example.test/path','https://files.owner.example.test:444']){
  const client=createNativeFileClient({fileOrigin:file,frontendOrigin,fetch:()=>assert.fail('invalid origin fetched')});await assert.rejects(()=>client.establish(identity));
 }
 for(const url of ['https://foreign.test/api/files/'+context,fileOrigin+'/api/files/'+context+'?token=unsafe',fileOrigin+'/api/files/'+context+'#fragment',fileOrigin+'/api/files/invalid',fileOrigin+'/arbitrary/'+context]){
  const client=createNativeFileClient({fileOrigin,frontendOrigin,fetch:async()=>new Response(JSON.stringify({url}))});await assert.rejects(()=>client.context('source','open',identity));
 }
});
test('denial remains typed for the owning application recovery and no refresh owner is added',async()=>{
 const client=createNativeFileClient({fileOrigin,frontendOrigin,fetch:async()=>new Response('{}',{status:401})});
 await assert.rejects(()=>client.establish(identity),error=>error.status===401&&error.code==='file_request_failed');
 const disabled=createNativeFileClient({fileOrigin:'',frontendOrigin,fetch:()=>assert.fail('disabled clear fetched')});await disabled.clear(identity);await assert.rejects(()=>disabled.establish(identity));
});
