import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {EntryScreen} from '../../../../compiled/web/src/EntryScreen.js';
const html=(kind,online=true)=>renderToStaticMarkup(createElement(EntryScreen,{
 state:{kind,context:{account_id:'SENSITIVE',actor_id:'SENSITIVE',checked_at:'SENSITIVE'}},online,
 onSignIn:()=>{},onRetry:()=>{},
}));
for(const [kind,title,action] of [
 ['signed_out','Sign in to continue','Sign in'],
 ['authentication_required','Sign in again','Sign in'],
 ['checking','Checking access','Checking access'],
 ['authorized','Setup not completed','Check access again'],
 ['access_denied','Access denied','Check access again'],
 ['actor_setup_required','Account setup not completed','Retry'],
 ['authorization_unavailable','Could not check access','Retry'],
 ['invalid_response','Could not verify access','Retry'],
 ['cancelled','Access check interrupted','Retry'],
 ['superseded','Access check interrupted','Retry'],
])test('safe presentation '+kind,()=>{
 const output=html(kind);assert.ok(output.includes(title));assert.match(output,new RegExp('>'+action+'(?:…)?</button>'));
 assert.ok(output.includes('Khula Development Group'));assert.ok(!output.includes('SENSITIVE'));
 assert.ok(output.includes('role="status"'));assert.ok(output.includes('aria-live="polite"'));
 assert.equal(/<button[^>]*disabled/.test(output),kind==='checking');
});
for(const kind of ['signed_out','checking','authorized','access_denied'])test('offline masks '+kind,()=>{
 const output=html(kind,false);assert.ok(output.includes('Connect to the internet'));
 assert.ok(output.includes('Online sign-in and setup are required'));
 assert.match(output,/<button[^>]*disabled/);assert.ok(!output.includes('SENSITIVE'));
 assert.ok(!output.includes('Setup not completed'));
});


test('authorized entry explicitly withholds domain setup and every failure offers safe guidance',()=>{
 assert.ok(html('authorized').includes('Online setup is still required before observations are available.'));
 assert.ok(html('signed_out').includes('Sign in to check your current KDG Capture access.'));
 assert.ok(html('access_denied').includes('This account does not currently have KDG Capture access.'));
 assert.ok(html('actor_setup_required').includes('Account setup is not yet complete.'));
 for(const kind of ['authorization_unavailable','invalid_response'])assert.ok(html(kind).includes('Retry when you are ready.'));
 for(const kind of ['cancelled','superseded'])assert.ok(html(kind).includes('Check access again to continue.'));
 for(const kind of ['authorized','access_denied','actor_setup_required','authorization_unavailable','invalid_response']){
  const output=html(kind);assert.ok(!output.includes('Start observation'));assert.ok(!output.includes('Setup completed'));
  assert.ok(!output.includes('<input'));assert.ok(!output.includes('<select'));
 }
});
