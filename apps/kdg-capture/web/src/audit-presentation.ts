/** Pure KDG projection of validated adapter outcomes; callers own authority and lifetime. */
import type {AuditDetailsResult} from './audit-display.js';
import {freeze,type Frozen} from './read-validation.js';
export type AuditActorLabel =
 | {actor_id:string;status:'resolved';display_name:string}
 | {actor_id:string;status:'unavailable';message_key:'audit.name_unavailable'}
 | {actor_id:string;status:'temporarily_unavailable';message_key:'audit.names_temporarily_unavailable'};
export type AuditPresentation = {
 scope:{account_id:string;org_id:string;capture_id:string;owner_account_id:string};
 original_capturer:AuditActorLabel;
 creation:{actor:AuditActorLabel;recorded_at:string};
 latest_modification:{actor:AuditActorLabel;recorded_at:string};
 current_revision:string;
 names:{status:'loaded';retry_available:false}|{status:'temporarily_unavailable';retry_available:true};
 events:{revision:string;command_type:'capture.create'|'capture.edit';executor:AuditActorLabel;initiator:AuditActorLabel|null;recorded_at:string}[];
 limit:number;next_cursor:string|null;
};
export type AuditPresentationResult = Readonly<{kind:'loaded';model:Frozen<AuditPresentation>}> | Exclude<AuditDetailsResult,{kind:'loaded'}>;
export function auditPresentation(result:AuditDetailsResult):AuditPresentationResult {
 if(result.kind!=='loaded')return result;
 const {audit,actor_display}=result.page;
 const labels=new Map(actor_display.status==='loaded'?actor_display.labels.map(label=>[label.actor_id,label] as const):[]);
 const actor=(actor_id:string):AuditActorLabel=>{
  if(actor_display.status==='temporarily_unavailable')return {actor_id,status:'temporarily_unavailable',message_key:'audit.names_temporarily_unavailable'};
  // The adapter has already proved the exact complete actor set. Never fall back
  // from a missing mapping to an account, reader or inferred service identity.
  const label=labels.get(actor_id)!;
  return label.status==='resolved'?{actor_id,status:'resolved',display_name:label.display_name}:{actor_id,status:'unavailable',message_key:'audit.name_unavailable'};
 };
 return freeze({kind:'loaded',model:{
  scope:{account_id:audit.account_id,org_id:audit.org_id,capture_id:audit.capture_id,owner_account_id:audit.owner_account_id},
  original_capturer:actor(audit.owner_actor_id),
  creation:{actor:actor(audit.created_by),recorded_at:audit.created_at},
  latest_modification:{actor:actor(audit.updated_by),recorded_at:audit.updated_at},
  current_revision:audit.current_revision,
  names:actor_display.status==='loaded'?{status:'loaded',retry_available:false}:{status:'temporarily_unavailable',retry_available:true},
  events:audit.events.map(event=>({revision:event.revision,command_type:event.command_type,executor:actor(event.executor_actor_id),initiator:event.initiator_actor_id===null?null:actor(event.initiator_actor_id),recorded_at:event.recorded_at})),
  limit:audit.limit,next_cursor:audit.next_cursor
 }});
}
