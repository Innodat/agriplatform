import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateInputs,redirectsFor,hasSecretToken} from '../build-release.mjs';
const good={DEPLOY_ENV:'production',PUBLIC_SITE_ORIGIN:'https://scribeswell.com',PUBLIC_API_ORIGIN:'https://api.scribeswell.com',VITE_SUPABASE_URL:'https://gjbsnxmbhxsvcblzgfts.supabase.co',VITE_SUPABASE_ANON_KEY:'sb_publishable_fixture'};
test('release inputs fail closed, permit public keys only',()=>{
 assert.throws(()=>validateInputs({}));
 assert.throws(()=>validateInputs({...good,DEPLOY_ENV:'staging'}));
 for(const key of ['sb_secret_no','service_role','broken',`x.${Buffer.from(JSON.stringify({role:'service_role'})).toString('base64url')}.x`]) assert.throws(()=>validateInputs({...good,VITE_SUPABASE_ANON_KEY:key}));
 assert.equal(validateInputs(good).VITE_PLATFORM_ORIGIN,'https://scribeswell.com');
 assert.throws(()=>validateInputs({...good,VITE_SUPABASE_URL:'http://localhost:54321'}));
});

test('manifest frontends generate nested SPA rules before root fallback',()=>{
 assert.equal(redirectsFor([{frontend:{base:'/'}},{frontend:{base:'/scribeswell/'}}]),'/scribeswell /scribeswell/ 301\n/scribeswell/* /scribeswell/index.html 200\n/* /index.html 200\n');
});

test('bundle audit distinguishes library prefix checks from token values',()=>{
 assert.equal(hasSecretToken('key.startsWith("sb_secret_")'),false);
 assert.equal(hasSecretToken('sb_secret_abcdefghijklmnopqrstuv'),true);
 assert.equal(hasSecretToken('eyJhbGciOiJIUzI1NiJ9.'+Buffer.from(JSON.stringify({role:'service_role'})).toString('base64url')+'.signature'),true);
});
