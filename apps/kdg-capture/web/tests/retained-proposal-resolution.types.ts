import type {ReviewedConflict,ReviewedLocalConflict,ResolutionSelection,LocalResolutionSelection} from '../src/history-store.js';
import type {ConflictResolutionRequest} from '../src/conflict-resolution.js';
export function serverReview(reviewed:ReviewedConflict):ConflictResolutionRequest {
 const classification:'confirmed'|'stale'|'paused'|undefined=reviewed.retained?.kind;
 void classification;
 return {kind:'current',reviewed,decision_id:'88888888-8888-4888-8888-888888888888'};
}
export function localReview(reviewed:ReviewedLocalConflict):LocalResolutionSelection {
 const previous:string|undefined=reviewed.reconsideration?.decision_id;
 void previous;
 return {reviewed,decision_id:'88888888-8888-4888-8888-888888888888',action_id:null,changes:null};
}
export function discriminate(local:ReviewedLocalConflict,server:ReviewedConflict){
 // @ts-expect-error Local phone selection is not a server-current review.
 const wrongServer:ResolutionSelection={reviewed:local,decision_id:'x',action_id:null,changes:null};
 // @ts-expect-error Server-current selection does not carry the actual chosen phone snapshot.
 const wrongLocal:LocalResolutionSelection={reviewed:server,decision_id:'x',action_id:null,changes:null};
 return {wrongServer,wrongLocal};
}
