import {A,O,C,Q,detail} from './read-fixture.mjs';
export {A,O,C,Q,detail};
export const pending=(changes={})=>({account_id:A,org_id:O,from_date:'2026-10-01',to_date:'2026-10-26',limit:2,...changes});
export const cursor=(item=detail(),changes={})=>Buffer.from(JSON.stringify(Object.fromEntries(Object.entries({v:1,org_id:O,account_id:A,permission:'kdg_capture.capture.read.own',from_date:'2026-10-01',to_date:'2026-10-26',limit:2,last_created_at:item.created_at,last_id:item.capture_id,...changes}).sort(([a],[b])=>a<b?-1:a>b?1:0)))).toString('base64url');
export const page=(changes={})=>({account_id:A,org_id:O,from_date:'2026-10-01',to_date:'2026-10-26',limit:2,items:[detail()],next_cursor:null,...changes});
export const response=(value=page(),status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json','Cache-Control':'private, no-store'}});
