import type {ReviewedEdit,LocalEditIntent,LocalCaptureBase} from '../src/history-store';
declare const review:ReviewedEdit;
if('version' in review&&review.version===2){
 const kind:'capture.create'|'capture.edit'=review.predecessor.type;
 // @ts-expect-error Local bases have no server revision.
 review.base.revision;
 // @ts-expect-error Local bases have no server creation audit.
 review.base.created_at;
 void kind;
}
declare const intent:LocalEditIntent;
if(intent.version===2){const base:intentBase= intent.base;void base;}
type intentBase=Extract<LocalEditIntent,{version:2}>['base'];
