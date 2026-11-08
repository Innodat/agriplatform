// UI-only transport double; actual cookie/provider/TLS proof is separate.
const origin='https://files.localhost:5181';
const context=origin+'/api/files/11111111-1111-4111-8111-111111111111';
const fixtureAccount='33333333-3333-3333-3333-333333333333';
function sessionFor(account,email='fixture@example.invalid',label='current',sessionId='55555555-5555-4555-8555-555555555555'){
 const payload={sub:account,session_id:sessionId,exp:Math.floor(Date.now()/1000)+3600,jti:label};
 const access_token=[{alg:'HS256',typ:'JWT'},payload,'fixture-signature'].map(v=>Buffer.from(typeof v==='string'?v:JSON.stringify(v)).toString('base64url')).join('.');
 return {access_token,refresh_token:'fixture-refresh-'+label,expires_at:payload.exp,expires_in:3600,token_type:'bearer',user:{id:account,email,aud:'authenticated',app_metadata:{},user_metadata:{}}};
}
async function files(page){
 await page.route(origin+'/**',async r=>{
  const headers={'access-control-allow-origin':'https://localhost:5181','access-control-allow-credentials':'true','access-control-allow-headers':'Authorization,Content-Type','access-control-allow-methods':'POST,OPTIONS'};
  if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers});
  // Request-owned evidence survives navigation and cannot accidentally use the
  // replacement account's browser storage for a delayed original request.
  const token=r.request().headers().authorization?.replace(/^Bearer /,'');
  let actor,sessionId;try{const claims=JSON.parse(Buffer.from(token.split('.')[1],'base64url').toString());actor=claims.sub;sessionId=claims.session_id;}catch{actor=['test-token','refreshed-token'].includes(token)?fixtureAccount:undefined;}
  if(!actor)return r.fulfill({status:401,json:{detail:{code:'authentication_required'}}});
  const pair={account_id:actor,session_id:sessionId||'55555555-5555-4555-8555-555555555555'};
  const path=new URL(r.request().url()).pathname;
  const json=path.includes('/api/file-contexts/')?{url:context,expires_at:new Date(Date.now()+60000).toISOString()}:path.endsWith('/prepare')?{status:'prepared',...pair}:path.endsWith('/clear')?{status:'cleared',provider_session:'absent',...pair}:{status:'ready'};
  return r.fulfill({headers,json});
 });
}
// A capture listener runs before either supported SDK subscription style. Replay
// through the native EventTarget so listener options/removal keep their meaning.
function installAuthNotificationHold(initial=true){
 window.heldAuthNotifications=[];window.holdAuthNotifications=initial;const Native=BroadcastChannel;
 window.BroadcastChannel=class extends Native{
  constructor(...args){super(...args);super.addEventListener('message',event=>{
   if(!window.holdAuthNotifications)return;
   event.stopImmediatePropagation();
   const deliver=()=>this.dispatchEvent(new MessageEvent('message',{data:event.data,origin:event.origin,lastEventId:event.lastEventId,ports:event.ports}));
   // Private fixture selection can release one real current SDK notification
   // while older notifications stay held; no event or credential is logged.
   deliver.authData=event.data;window.heldAuthNotifications.push(deliver);
  },true);}
 };
 window.addEventListener('storage',event=>{if(window.holdAuthNotifications&&event.key==='pts-auth')event.stopImmediatePropagation();},true);
}
module.exports={files,origin,context,sessionFor,installAuthNotificationHold};
