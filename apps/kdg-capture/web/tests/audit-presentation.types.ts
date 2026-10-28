import {auditPresentation,type AuditPresentationResult} from '../src/audit-presentation';
import type {AuditDetailsResult} from '../src/audit-display';
function types(input:AuditDetailsResult,result:AuditPresentationResult){
 auditPresentation(input);
 if(result.kind==='loaded'){
  // @ts-expect-error immutable header
  result.model.creation.recorded_at='changed';
  // @ts-expect-error immutable list
  result.model.events.push(result.model.events[0]);
  if(result.model.original_capturer.status==='resolved'){
   const name:string=result.model.original_capturer.display_name;void name;
  }else{
   // @ts-expect-error unavailable labels have no ordinary name
   result.model.original_capturer.display_name;
  }
 }else{
  // @ts-expect-error failed reads cannot carry a presentation
  result.model;
 }
}
void types;
// @ts-expect-error raw wire objects must pass the adapter first
auditPresentation({audit:{},actor_display:{status:'loaded',labels:[]}});
