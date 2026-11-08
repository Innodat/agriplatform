import test from 'node:test';
import assert from 'node:assert/strict';
import {revokeOriginalSession} from '../src/sessionRevocation.ts';

const original={id:'account',token:'original',refreshToken:'original-refresh',sessionId:'original-session'};
test('expired original refreshes its explicit refresh token and verifies exact session before revoke',async()=>{
 const calls=[];
 await revokeOriginalSession(original,{
  revoke:async token=>{calls.push(['revoke',token]);if(token==='original')throw {status:401};},
  refresh:async refresh=>{calls.push(['refresh',refresh]);return {id:'account',token:'renewed',refreshToken:'rotated-refresh'};},
  claims:async token=>{calls.push(['verified-claims',token]);return {sub:'account',session_id:'original-session'};},
  retain:async()=>{calls.push(['retain-verified-rotation']);},
 });
 assert.deepEqual(calls,[['revoke','original'],['refresh','original-refresh'],['verified-claims','renewed'],['retain-verified-rotation'],['revoke','renewed']]);
});
test('different verified session in same account never receives provider revocation',async()=>{
 const revoked=[];
 await assert.rejects(()=>revokeOriginalSession(original,{
  revoke:async token=>{revoked.push(token);throw {status:401};},
  refresh:async()=>({id:'account',token:'different-session-credential',refreshToken:'different-refresh'}),
  claims:async()=>({sub:'account',session_id:'different-session'}),
  retain:async()=>assert.fail('wrong-session material persisted'),
 }));
 assert.deepEqual(revoked,['original']);
});
test('provider outage remains failed and does not refresh another current session',async()=>{
 await assert.rejects(()=>revokeOriginalSession(original,{
  revoke:async()=>{throw {status:503};},refresh:async()=>assert.fail('outage cannot invoke refresh'),claims:async()=>assert.fail('outage cannot check new claims'),retain:async()=>assert.fail('outage cannot persist rotation'),
 }));
});
test('verified rotation is durable before failed revoke and reload retries latest credentials',async()=>{
 let retained={...original};const events=[];
 const owner={
  revoke:async token=>{events.push(['revoke',token]);throw {status:token==='original'?401:503};},
  refresh:async refresh=>{events.push(['refresh',refresh]);return {id:'account',token:'renewed',refreshToken:'rotated-refresh'};},
  claims:async()=>({sub:'account',session_id:'original-session'}),
  retain:async(_,next)=>{events.push(['retain',next.refreshToken]);retained={...retained,revocationToken:next.token,refreshToken:next.refreshToken};},
 };
 await assert.rejects(()=>revokeOriginalSession(original,owner));
 assert.equal(retained.token,'original');assert.equal(retained.refreshToken,'rotated-refresh');
 assert(events.findIndex(value=>value[0]==='retain')<events.findIndex(value=>value[0]==='revoke'&&value[1]==='renewed'));
 await revokeOriginalSession(JSON.parse(JSON.stringify(retained)),{...owner,
  revoke:async token=>{events.push(['retry-revoke',token]);if(token==='renewed')throw {status:401};},
  refresh:async refresh=>{assert.equal(refresh,'rotated-refresh');return {id:'account',token:'latest',refreshToken:'latest-refresh'};},
 });
 assert.equal(retained.refreshToken,'latest-refresh');
});
