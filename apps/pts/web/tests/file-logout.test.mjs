import test from 'node:test';
import assert from 'node:assert/strict';
import {completeFileLogout} from '../src/fileLogout.ts';

test('file outage still attempts provider revocation; original recovery remains incomplete',async()=>{
 let revokes=0,clears=0;
 await assert.rejects(()=>completeFileLogout('original',{clear:async()=>{clears++;throw new Error('file outage');},revoke:async()=>{revokes++;}}));
 assert.equal(revokes,1);assert.equal(clears,2);
 await completeFileLogout('original',{clear:async()=>({provider_session:'absent'}),revoke:async()=>{throw new Error('already revoked');}});
});
test('file cleanup before failed provider revocation stays incomplete and can retry',async()=>{
 let absent=false,revokes=0;
 const clear=async()=>({provider_session:absent?'absent':'present'});
 await assert.rejects(()=>completeFileLogout('original',{clear,revoke:async()=>{revokes++;throw new Error('provider outage');}}));
 await completeFileLogout('original',{clear,revoke:async()=>{revokes++;absent=true;}});
 assert.equal(revokes,2);
});
test('generic401 and missing proof never claim provider absence',async()=>{
 await assert.rejects(()=>completeFileLogout('original',{clear:async()=>{throw Object.assign(new Error('denied'),{status:401});},revoke:async()=>{throw new Error('denied');}}));
 await assert.rejects(()=>completeFileLogout('original',{clear:async()=>undefined,revoke:async()=>{throw new Error('unverified');}}));
});
test('missing native cleanup proof cannot complete even when provider revocation succeeds',async()=>{
 await assert.rejects(()=>completeFileLogout('original',{clear:async()=>undefined,revoke:async()=>{}}));
});
test('original absence preserves failed replacement custody after both cleanup attempts',async()=>{
 let clears=0,revokes=0;
 const failure=Object.assign(new Error('file_cleanup_replacement_unavailable'),{code:'file_cleanup_replacement_unavailable'});
 await assert.rejects(()=>completeFileLogout('original',{
  clear:async()=>{clears++;return {provider_session:'absent'};},
  revoke:async()=>{revokes++;throw failure;},
 }),error=>error===failure);
 assert.equal(clears,2);assert.equal(revokes,1);
});
