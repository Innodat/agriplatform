import {createAuditReview,type AuditReviewState} from '../src/audit-review';
function types(state:AuditReviewState){if(state.kind==='loaded'){
 // @ts-expect-error immutable snapshot
 state.model.events.length=0;
}else{
 // @ts-expect-error only loaded states have business content
 state.model;
}}
void types;
// @ts-expect-error no implicit current authority/session
createAuditReview({pending:{account_id:'a',org_id:'o',capture_id:'c'}});
