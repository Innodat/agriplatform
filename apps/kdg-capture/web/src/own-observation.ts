/** KDG-only exact closed offline evidence; no capability inference or lease extension. */
import {object,id,decimal,instant,invalid} from './read-validation.js';
export function validateOwnObservation(value:unknown,account:string,org:string,permission:'kdg_capture.capture.read.own'|'kdg_capture.capture.edit.own') {
 const o=object(value,['account_id','actor_id','membership_id','authorization_scope','resource_scope','permission','decision_id','checked_at','expires_at']);
 const a=object(o.authorization_scope,['kind','org_id']),r=object(o.resource_scope,['kind','account_id']);
 if(o.account_id!==account||!id(o.actor_id)||!decimal(o.membership_id)||!id(o.decision_id)||a.kind!=='organization'||a.org_id!==org||r.kind!=='own_account'||r.account_id!==account||o.permission!==permission||!instant(o.checked_at)||!instant(o.expires_at)||!o.checked_at.endsWith('Z')||!o.expires_at.endsWith('Z')||Date.parse(o.expires_at)-Date.parse(o.checked_at)!==604800000||o.checked_at.slice(19)!==o.expires_at.slice(19))return invalid();
 return o;
}
