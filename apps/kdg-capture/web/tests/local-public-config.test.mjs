import {test} from 'node:test';
import assert from 'node:assert/strict';
const {parseKdgLocalPublicConfig}=await import('../../../../compiled/web/src/local-public-config.js').catch(()=>({}));
const ORG='33333333-3333-4333-8333-333333333333';
const config=()=>({schema_version:1,environment_kind:'local_disposable',org_id:ORG,auth_url:'http://localhost:55481',auth_public_key:'sb_publishable_synthetic_public_123456'});
test('local public configuration accepts explicit loopback public inputs and returns an immutable owner snapshot',()=>{
 assert.equal(typeof parseKdgLocalPublicConfig,'function','local public parser missing');const input=config(),parsed=parseKdgLocalPublicConfig(input,'http://localhost:5188');assert.deepEqual(parsed,{org:ORG,url:input.auth_url,publicKey:input.auth_public_key});assert.ok(Object.isFrozen(parsed));input.org_id='PRIVATE';assert.equal(parsed.org,ORG);
});
for(const [name,change] of Object.entries({version:v=>v.schema_version=2,environment:v=>v.environment_kind='production',array_environment:v=>v.environment_kind=['local_disposable'],newline_org:v=>v.org_id+='\n',org:v=>v.org_id='PRIVATE',nil:v=>v.org_id='00000000-0000-0000-0000-000000000000',extra:v=>v.service_key='PRIVATE',remote:v=>v.auth_url='https://real-auth.example.com',query:v=>v.auth_url='http://localhost:55481?key=PRIVATE',credentials:v=>v.auth_url='http://u:PRIVATE@localhost:55481',private_key:v=>v.auth_public_key='sb_secret_PRIVATE'}))test('local public config refuses '+name+' without raw errors',()=>{
 const input=config();change(input);assert.equal(parseKdgLocalPublicConfig(input,'http://127.0.0.1:5188'),null);
});
test('local public config refuses missing/nonobject values and non-loopback page origins',()=>{
 for(const value of [null,undefined,[],1,'PRIVATE',{}])assert.equal(parseKdgLocalPublicConfig(value,'http://localhost:5188'),null);
 for(const origin of ['https://app.example.com','http://localhost.evil.invalid','file:///tmp/app','null','http://u:PRIVATE@localhost:5188','http://localhost:5188/path'])assert.equal(parseKdgLocalPublicConfig(config(),origin),null);
});
test('local public config supports explicit CI, loopback IPv6 and public legacy anon keys',()=>{
 const input=config();input.environment_kind='ci_disposable';input.auth_url='http://[::1]:55481';input.auth_public_key='e30.'+Buffer.from(JSON.stringify({role:'anon'})).toString('base64url')+'.synthetic';assert.ok(parseKdgLocalPublicConfig(input,'http://[::1]:5188'));
});
